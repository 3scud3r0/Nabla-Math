"""Deterministic batched Monte-Carlo tree search with explicit work budgets."""

from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Callable, Generic, Hashable, Sequence, TypeVar

State = TypeVar("State", bound=Hashable)
Action = TypeVar("Action", bound=Hashable)


@dataclass(frozen=True)
class MCTSConfig:
    simulations: int = 1_024
    max_depth: int = 64
    exploration: float = math.sqrt(2.0)
    batch_size: int = 64
    seed: int = 0

    def __post_init__(self) -> None:
        if self.simulations < 1 or self.max_depth < 1 or self.batch_size < 1:
            raise ValueError("Orçamentos MCTS devem ser positivos")
        if not math.isfinite(self.exploration) or self.exploration < 0:
            raise ValueError("exploration deve ser finito e não negativo")


@dataclass(frozen=True)
class ActionStatistic(Generic[Action]):
    action: Action
    visits: int
    mean_value: float


@dataclass(frozen=True)
class MCTSResult(Generic[Action]):
    action: Action | None
    simulations: int
    statistics: tuple[ActionStatistic[Action], ...]


@dataclass
class _Node(Generic[State, Action]):
    state: State
    parent: _Node[State, Action] | None
    action: Action | None
    unexpanded: list[Action]
    children: dict[Action, _Node[State, Action]]
    visits: int = 0
    value_sum: float = 0.0


def batch_mcts(
    initial: State,
    *,
    actions: Callable[[State], Sequence[Action]],
    transition: Callable[[State, Action], State],
    evaluate: Callable[[Sequence[State]], Sequence[float]],
    terminal: Callable[[State], bool],
    config: MCTSConfig = MCTSConfig(),
) -> MCTSResult[Action]:
    """Search with batched leaf evaluation, suitable for a neural device backend.

    ``evaluate`` receives a batch, making accelerator utilization the caller's
    responsibility while this module retains deterministic tree accounting.
    Values are from the root player's perspective and must be finite.
    """
    rng = random.Random(config.seed)
    root_actions = list(actions(initial)) if not terminal(initial) else []
    if len(set(root_actions)) != len(root_actions):
        raise ValueError("actions retornou ações duplicadas")
    root = _Node(initial, None, None, root_actions, {})
    completed = 0
    while completed < config.simulations:
        batch_count = min(config.batch_size, config.simulations - completed)
        paths: list[list[_Node[State, Action]]] = []
        leaves: list[State] = []
        for _ in range(batch_count):
            node, path, depth = root, [root], 0
            while not terminal(node.state) and depth < config.max_depth:
                if node.unexpanded:
                    choice = rng.randrange(len(node.unexpanded))
                    action = node.unexpanded.pop(choice)
                    state = transition(node.state, action)
                    available = list(actions(state)) if not terminal(state) else []
                    if len(set(available)) != len(available):
                        raise ValueError("actions retornou ações duplicadas")
                    child = _Node(state, node, action, available, {})
                    node.children[action] = child
                    node = child
                    path.append(node)
                    break
                if not node.children:
                    break
                logarithm = math.log(max(1, node.visits))
                node = max(
                    node.children.values(),
                    key=lambda child: (
                        child.value_sum / child.visits
                        + config.exploration * math.sqrt(logarithm / child.visits)
                        if child.visits else math.inf,
                        repr(child.action),
                    ),
                )
                path.append(node)
                depth += 1
            paths.append(path)
            leaves.append(node.state)
        values = list(evaluate(leaves))
        if len(values) != len(paths):
            raise ValueError("evaluate deve devolver um valor por estado")
        for path, raw_value in zip(paths, values):
            value = float(raw_value)
            if not math.isfinite(value):
                raise ValueError("evaluate devolveu valor não finito")
            for node in path:
                node.visits += 1
                node.value_sum += value
        completed += len(paths)
    statistics = tuple(sorted(
        (ActionStatistic(action, child.visits, child.value_sum / child.visits)
         for action, child in root.children.items() if child.visits),
        key=lambda item: (-item.visits, -item.mean_value, repr(item.action)),
    ))
    return MCTSResult(statistics[0].action if statistics else None, completed, statistics)


__all__ = ["ActionStatistic", "MCTSConfig", "MCTSResult", "batch_mcts"]
