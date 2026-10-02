from fractions import Fraction
import pytest
from nablamath.math.logic import Constant, Equal, Exists, ForAll, Function, Relation, Structure, Variable
from nablamath.math.algebra import prime_field
from nablamath.math.number_theory import chinese_remainder, solve_linear_congruence
from nablamath.math.graph_theory import WeightedDigraph
from nablamath.math.linear_algebra import Matrix, identity


def test_finite_first_order_semantics():
    structure = Structure(("0", "1"), {"zero": "0"}, {"flip": (1, lambda x: "1" if x == "0" else "0")},
                          {"different": (2, lambda x, y: x != y)})
    x = Variable("x")
    assert ForAll("x", Relation("different", (x, Function("flip", (x,))))).evaluate(structure)
    assert Exists("x", Equal(Function("flip", (x,)), Constant("zero"))).evaluate(structure)


def test_prime_fields_and_division():
    field = prime_field(7)
    assert field.inverse(3) == 5
    assert field.divide(4, 2) == 2
    with pytest.raises(ValueError): prime_field(8)


def test_generalized_chinese_remainder_and_linear_congruences():
    assert chinese_remainder(((2, 3), (3, 5), (2, 7))) == (23, 105)
    assert chinese_remainder(((1, 4), (3, 6))) == (9, 12)
    assert solve_linear_congruence(6, 8, 14) == (6, 13)
    with pytest.raises(ValueError): chinese_remainder(((0, 2), (1, 2)))


def test_exact_dijkstra_and_unreachable_vertices():
    graph = WeightedDigraph(frozenset({"a", "b", "c", "d"}), {("a", "b"): 2, ("a", "c"): 5, ("b", "c"): Fraction(1, 2)})
    assert graph.shortest_distances("a") == {"a": 0, "b": 2, "c": Fraction(5, 2), "d": None}


def test_exact_matrix_inverse():
    matrix = Matrix(((1, 2), (3, 5)))
    inverse = matrix.inverse()
    assert matrix @ inverse == identity(2)
    with pytest.raises(ValueError): Matrix(((1, 2), (2, 4))).inverse()
