import math
import pytest
from nablamath.math.logic import And, Implies, Not, Or, Var, equivalent, is_tautology, truth_table
from nablamath.math.algebra import FiniteGroup, cyclic_group
from nablamath.math.number_theory import extended_gcd, is_prime, modular_inverse, prime_factors
from nablamath.math.graph_theory import Graph
from nablamath.math.topology import FiniteTopology
from nablamath.math.analysis import bisection, trapezoid


def test_propositional_truth_and_equivalence():
    p, q = Var("p"), Var("q")
    assert is_tautology(Implies(And(p, q), p))
    assert equivalent(Implies(p, q), Or(Not(p), q))
    assert len(truth_table(And(p, q))) == 4


def test_finite_cyclic_group_and_invalid_table():
    group = cyclic_group(6)
    assert group.inverse(2) == 4 and group.order(2) == 3
    with pytest.raises(ValueError):
        FiniteGroup((0, 1), 0, {(0, 0): 0})


def test_elementary_number_theory():
    gcd, x, y = extended_gcd(-30, 21)
    assert gcd == 3 and -30 * x + 21 * y == gcd
    assert modular_inverse(3, 11) == 4
    assert is_prime(104729) and not is_prime(104730)
    assert prime_factors(-84) == (-1, 2, 2, 3, 7)


def test_graph_paths_and_components():
    graph = Graph(("a", "b", "c", "d"), frozenset({frozenset({"a", "b"}), frozenset({"b", "c"})}))
    assert graph.shortest_path("a", "c") == ("a", "b", "c")
    assert graph.components() == (("a", "b", "c"), ("d",))


def test_finite_topology_and_continuity():
    indiscrete = FiniteTopology(frozenset({"a", "b"}), frozenset({frozenset(), frozenset({"a", "b"})}))
    point = FiniteTopology(frozenset({"x"}), frozenset({frozenset(), frozenset({"x"})}))
    assert indiscrete.is_continuous_to(point, {"a": "x", "b": "x"})


def test_real_analysis_reports_error_bounds():
    root, error = bisection(lambda x: x * x - 2, 1, 2)
    assert abs(root - math.sqrt(2)) <= error + 1e-15
    assert trapezoid(lambda x: x, 0, 1, 100) == pytest.approx(.5)
