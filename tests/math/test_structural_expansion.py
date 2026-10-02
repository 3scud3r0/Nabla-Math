from fractions import Fraction
import pytest
from nablamath.math.statistics import linear_regression
from nablamath.math.probability import FiniteDistribution, first_marginal, independent, product_distribution
from nablamath.math.graph_theory import maximum_bipartite_matching, topological_sort
from nablamath.math.topology import FiniteTopology, boundary, closure, interior, is_connected, subspace
from nablamath.math.category_theory import product_cones
from nablamath.math.category_theory.categories import FiniteCategory, Morphism


def test_exact_linear_regression_and_residuals():
    fit = linear_regression([0, 1, 2], [1, 3, 5])
    assert (fit.intercept, fit.slope, fit.residual_sum_squares) == (1, 2, 0)
    assert fit.predict(Fraction(3, 2)) == 4
    with pytest.raises(ValueError): linear_regression([1, 1], [2, 3])


def test_joint_distribution_marginals_and_independence():
    coin = FiniteDistribution({0: Fraction(1, 2), 1: Fraction(1, 2)})
    joint = product_distribution(coin, coin)
    assert first_marginal(joint) == coin and independent(joint)
    dependent = FiniteDistribution({(0, 0): Fraction(1, 2), (1, 1): Fraction(1, 2)})
    assert not independent(dependent)


def test_dag_sort_and_bipartite_matching():
    order = topological_sort(frozenset({"a", "b", "c"}), frozenset({("a", "b"), ("b", "c")}))
    assert order == ("a", "b", "c")
    with pytest.raises(ValueError): topological_sort(frozenset({"a", "b"}), frozenset({("a", "b"), ("b", "a")}))
    matching = maximum_bipartite_matching(frozenset({"u", "v"}), frozenset({"x", "y"}),
                                          frozenset({("u", "x"), ("u", "y"), ("v", "x")}))
    assert len(matching) == 2 and len(set(matching.values())) == 2


def test_finite_topological_operations():
    space = FiniteTopology(frozenset({"a", "b"}), frozenset({frozenset(), frozenset({"a"}), frozenset({"a", "b"})}))
    assert interior(space, frozenset({"b"})) == frozenset()
    assert closure(space, frozenset({"b"})) == frozenset({"b"})
    assert boundary(space, frozenset({"b"})) == frozenset({"b"})
    assert is_connected(space)
    assert subspace(space, frozenset({"a"})).points == frozenset({"a"})


def test_product_universal_property_in_one_object_category():
    category = FiniteCategory(("1",), (Morphism("id", "1", "1"),), {"1": "id"}, {("id", "id"): "id"})
    cones = product_cones(category, "1", "1")
    assert len(cones) == 1 and cones[0].product == "1"
