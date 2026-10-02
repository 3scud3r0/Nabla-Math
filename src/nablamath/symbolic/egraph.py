"""Equality saturation for the small, exact NablaMath expression language.

The implementation deliberately has no optional dependencies.  It is a bounded
e-graph rather than an unbounded simplifier: callers always choose a resource
budget, and every equality used during saturation is retained in an audit log.
Only identities that preserve the domain of the current partial-expression
semantics are enabled by default.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
from typing import Callable, Literal, Mapping

from ..expression import Binary, Expr, Number, Symbol, to_data

EGRAPH_SCHEMA_VERSION = 1
RULESET_VERSION = "domain-safe-rational-v1"


@dataclass(frozen=True, order=True)
class ENode:
    """An operator whose operands point to equivalence classes."""

    op: str
    children: tuple[int, ...] = ()
    value: Fraction | str | None = None


@dataclass(frozen=True)
class RewriteEvent:
    rule: str
    source_class: int
    target_class: int


@dataclass(frozen=True)
class SaturationResult:
    original: Expr
    expression: Expr
    cost: float
    iterations: int
    saturated: bool
    class_count: int
    node_count: int
    proof: tuple[RewriteEvent, ...]
    stop_reason: Literal["saturated", "node_limit", "iteration_limit"]
    operation_costs: tuple[tuple[str, float], ...]

    def to_data(self) -> dict[str, object]:
        """Return a stable, JSON-compatible audit record."""
        payload: dict[str, object] = {
            "schema_version": EGRAPH_SCHEMA_VERSION,
            "ruleset_version": RULESET_VERSION,
            "original": to_data(self.original),
            "expression": to_data(self.expression),
            "cost": self.cost,
            "iterations": self.iterations,
            "saturated": self.saturated,
            "stop_reason": self.stop_reason,
            "class_count": self.class_count,
            "node_count": self.node_count,
            "operation_costs": dict(self.operation_costs),
            "proof": [
                {
                    "rule": event.rule,
                    "source_class": event.source_class,
                    "target_class": event.target_class,
                }
                for event in self.proof
            ],
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return {**payload, "content_id": hashlib.sha256(canonical.encode("utf-8")).hexdigest()}

    @property
    def content_id(self) -> str:
        """SHA-256 identity of the complete optimization audit record."""
        return str(self.to_data()["content_id"])


CostFunction = Callable[[str, Fraction | str | None], float]


def _default_cost(op: str, value: Fraction | str | None) -> float:
    return 1.0


class EGraphLimitError(RuntimeError):
    """The configured hard node budget is not large enough."""


class EGraph:
    """Compact union-find e-graph with congruence closure."""

    def __init__(self, *, node_limit: int | None = None) -> None:
        if node_limit is not None and node_limit < 1:
            raise ValueError("O limite de nós deve ser positivo")
        self._node_limit = node_limit
        self._parent: list[int] = []
        self._classes: dict[int, set[ENode]] = {}
        self._memo: dict[ENode, int] = {}
        self.proof: list[RewriteEvent] = []

    def find(self, class_id: int) -> int:
        parent = self._parent[class_id]
        if parent != class_id:
            self._parent[class_id] = self.find(parent)
        return self._parent[class_id]

    def add(self, node: ENode) -> int:
        node = self._canonical(node)
        existing = self._memo.get(node)
        if existing is not None:
            return self.find(existing)
        if self._node_limit is not None and self.node_count >= self._node_limit:
            raise EGraphLimitError(f"Limite rígido de {self._node_limit} nós atingido")
        class_id = len(self._parent)
        self._parent.append(class_id)
        self._classes[class_id] = {node}
        self._memo[node] = class_id
        return class_id

    def add_expr(self, expr: Expr) -> int:
        if isinstance(expr, Number):
            return self.add(ENode("number", value=expr.value))
        if isinstance(expr, Symbol):
            return self.add(ENode("symbol", value=expr.name))
        return self.add(ENode(expr.op, (self.add_expr(expr.left), self.add_expr(expr.right))))

    def union(self, first: int, second: int, rule: str) -> bool:
        first, second = self.find(first), self.find(second)
        if first == second:
            return False
        # Stable representatives make runs and proof logs reproducible.
        root, merged = min(first, second), max(first, second)
        self._parent[merged] = root
        self._classes[root].update(self._classes.pop(merged))
        self.proof.append(RewriteEvent(rule, first, second))
        return True

    def rebuild(self) -> None:
        """Restore congruence after unions, merging identical canonical nodes."""
        while True:
            self._memo.clear()
            collision: tuple[int, int] | None = None
            for class_id in sorted(self._classes):
                root = self.find(class_id)
                canonical = {self._canonical(node) for node in self._classes[class_id]}
                self._classes[class_id] = canonical
                for node in canonical:
                    other = self._memo.get(node)
                    if other is not None and self.find(other) != root:
                        collision = (root, other)
                        break
                    self._memo[node] = root
                if collision:
                    break
            if collision is None:
                return
            self.union(*collision, "congruence")

    def _canonical(self, node: ENode) -> ENode:
        return ENode(node.op, tuple(self.find(child) for child in node.children), node.value)

    def nodes(self) -> list[tuple[int, ENode]]:
        return [(root, node) for root in sorted(self._classes) for node in sorted(self._classes[root])]

    @property
    def class_count(self) -> int:
        return len(self._classes)

    @property
    def node_count(self) -> int:
        return sum(len(nodes) for nodes in self._classes.values())

    def _constant(self, class_id: int) -> Fraction | None:
        for node in self._classes[self.find(class_id)]:
            if node.op == "number":
                assert isinstance(node.value, Fraction)
                return node.value
        return None

    def apply_rules(self) -> tuple[bool, bool]:
        """Run one rule pass, returning ``(changed, budget_exhausted)``."""
        changed = False
        snapshot = self.nodes()
        try:
            for owner, node in snapshot:
                if len(node.children) != 2:
                    continue
                left, right = node.children
                # Commutativity exposes matches without choosing a canonical tree.
                if node.op in {"+", "*"}:
                    changed |= self.union(
                        owner,
                        self.add(ENode(node.op, (right, left))),
                        f"commute_{node.op}",
                    )
                lval, rval = self._constant(left), self._constant(right)
                if node.op == "+" and rval == 0:
                    changed |= self.union(owner, left, "add_zero")
                if node.op == "+" and lval == 0:
                    changed |= self.union(owner, right, "zero_add")
                if node.op == "*" and rval == 1:
                    changed |= self.union(owner, left, "multiply_one")
                if node.op == "*" and lval == 1:
                    changed |= self.union(owner, right, "one_multiply")
                if node.op == "/" and rval == 1:
                    changed |= self.union(owner, left, "divide_one")
                if node.op == "**" and rval == 1:
                    changed |= self.union(owner, left, "power_one")
                if lval is not None and rval is not None:
                    folded = _fold(node.op, lval, rval)
                    if folded is not None:
                        changed |= self.union(
                            owner,
                            self.add(ENode("number", value=folded)),
                            "constant_fold",
                        )
                # Associativity preserves domains for exact + and * expressions.
                if node.op in {"+", "*"}:
                    for inner in tuple(self._classes[self.find(left)]):
                        if inner.op == node.op:
                            a, b = inner.children
                            bc = self.add(ENode(node.op, (b, right)))
                            changed |= self.union(
                                owner,
                                self.add(ENode(node.op, (a, bc))),
                                f"associate_{node.op}",
                            )
                # a*b + a*c == a*(b+c), after commutativity exposes either side.
                if node.op == "+":
                    for left_node in tuple(self._classes[self.find(left)]):
                        for right_node in tuple(self._classes[self.find(right)]):
                            if (
                                left_node.op == right_node.op == "*"
                                and left_node.children[0] == right_node.children[0]
                            ):
                                total = self.add(
                                    ENode("+", (left_node.children[1], right_node.children[1]))
                                )
                                product = self.add(
                                    ENode("*", (left_node.children[0], total))
                                )
                                changed |= self.union(owner, product, "factor_common_left")
        except EGraphLimitError:
            if changed:
                self.rebuild()
            return changed, True
        if changed:
            self.rebuild()
        return changed, False

    def extract(self, root: int, cost: CostFunction = _default_cost) -> tuple[Expr, float]:
        best: dict[int, tuple[float, Expr]] = {}
        # Bellman-Ford-style relaxation supports cyclic e-graphs safely.
        for _ in range(max(1, len(self._classes))):
            updated = False
            for owner, node in self.nodes():
                own_cost = float(cost(node.op, node.value))
                if not math.isfinite(own_cost) or own_cost < 0:
                    raise ValueError("Custos de extração devem ser finitos e não negativos")
                if node.op == "number":
                    if not isinstance(node.value, Fraction):
                        raise TypeError("Nó numérico inválido no e-graph")
                    candidate = (own_cost, Number(node.value))
                elif node.op == "symbol":
                    if not isinstance(node.value, str):
                        raise TypeError("Nó simbólico inválido no e-graph")
                    candidate = (own_cost, Symbol(node.value))
                elif all(self.find(child) in best for child in node.children):
                    a, b = (best[self.find(child)] for child in node.children)
                    candidate = (own_cost + a[0] + b[0], Binary(node.op, a[1], b[1]))
                else:
                    continue
                owner = self.find(owner)
                if owner not in best or candidate[0] < best[owner][0]:
                    best[owner], updated = candidate, True
            if not updated:
                break
        return best[self.find(root)][1], best[self.find(root)][0]


def _fold(op: str, left: Fraction, right: Fraction) -> Fraction | None:
    if op == "+":
        return left + right
    if op == "-":
        return left - right
    if op == "*":
        return left * right
    if op == "/":
        return None if right == 0 else left / right
    if op == "**" and right.denominator == 1 and not (left == 0 and right <= 0):
        return left ** right.numerator
    return None


def saturate(
    expr: Expr,
    *,
    iteration_limit: int = 12,
    node_limit: int = 10_000,
    operation_costs: Mapping[str, float] | None = None,
) -> SaturationResult:
    """Explore equivalent expressions and extract the cheapest one.

    Limits are mandatory safety boundaries against equality-saturation blow-up.
    ``operation_costs`` can favor forms appropriate for a backend (for example,
    assigning a high cost to division).  Unknown operators cost one.
    """
    if iteration_limit < 1 or node_limit < 1:
        raise ValueError("Os limites de iteração e nós devem ser positivos")
    weights = dict(operation_costs or {})
    for name, weight in weights.items():
        try:
            numeric_weight = float(weight)
        except (TypeError, ValueError) as exc:
            raise ValueError("Custos de operação devem ser números reais") from exc
        if not isinstance(name, str) or not math.isfinite(numeric_weight) or numeric_weight < 0:
            raise ValueError("Custos de operação devem ser finitos, não negativos e ter nomes textuais")
        weights[name] = numeric_weight
    graph = EGraph(node_limit=node_limit)
    try:
        root = graph.add_expr(expr)
    except EGraphLimitError as exc:
        raise ValueError("O limite de nós é menor que a expressão de entrada") from exc
    saturated = False
    stop_reason: Literal["saturated", "node_limit", "iteration_limit"] = "iteration_limit"
    iterations = 0
    for iterations in range(1, iteration_limit + 1):
        changed, budget_exhausted = graph.apply_rules()
        if budget_exhausted:
            stop_reason = "node_limit"
            break
        if not changed:
            saturated = True
            stop_reason = "saturated"
            break
    result, result_cost = graph.extract(root, lambda op, value: weights.get(op, 1.0))
    return SaturationResult(
        expr,
        result,
        result_cost,
        iterations,
        saturated,
        graph.class_count,
        graph.node_count,
        tuple(graph.proof),
        stop_reason,
        tuple(sorted(weights.items())),
    )
