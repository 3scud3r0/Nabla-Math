from fractions import Fraction
import pytest
from nablamath.math.algebra import integers_modulo
from nablamath.math.combinatorics import binomial, partition_number, permutations
from nablamath.math.geometry import Point2, orientation, polygon_twice_signed_area, squared_distance
from nablamath.math.probability import FiniteDistribution
from nablamath.math.statistics import covariance, mean, variance
from nablamath.math.category_theory import discrete_category, hom, initial_objects, is_isomorphism, terminal_objects


def test_finite_ring_axioms_units_and_inverses():
    ring = integers_modulo(8)
    assert ring.additive_inverse(3) == 5
    assert ring.units() == (1, 3, 5, 7)
    assert ring.multiply(3, 5) == 7


def test_exact_finite_probability_and_conditioning():
    die = FiniteDistribution({face: Fraction(1, 6) for face in range(1, 7)})
    assert die.expectation(lambda x: x) == Fraction(7, 2)
    assert die.variance(lambda x: x) == Fraction(35, 12)
    assert die.condition(lambda x: x % 2 == 0).masses == {2: Fraction(1, 3), 4: Fraction(1, 3), 6: Fraction(1, 3)}


def test_enumerative_combinatorics():
    assert binomial(10, 3) == 120
    assert permutations(5, 2) == 20
    assert [partition_number(n) for n in range(7)] == [1, 1, 2, 3, 5, 7, 11]


def test_exact_plane_geometry():
    a, b, c = Point2(0, 0), Point2(3, 0), Point2(0, 4)
    assert squared_distance(b, c) == 25
    assert orientation(a, b, c) == 1
    assert polygon_twice_signed_area((a, b, c)) == 12


def test_exact_descriptive_statistics():
    assert mean([1, 2, 3]) == 2
    assert variance([1, 2, 3]) == Fraction(2, 3)
    assert variance([1, 2, 3], sample=True) == 1
    assert covariance([1, 2, 3], [2, 4, 6]) == Fraction(4, 3)


def test_universal_objects_in_discrete_categories():
    one = discrete_category(("only",))
    assert initial_objects(one) == terminal_objects(one) == ("only",)
    assert hom(one, "only", "only") == ("id:only",)
    assert is_isomorphism(one, "id:only")
    two = discrete_category(("A", "B"))
    assert initial_objects(two) == terminal_objects(two) == ()
