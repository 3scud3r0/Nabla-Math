from fractions import Fraction
import pytest
from nablamath.math.polynomials import Polynomial, polynomial_gcd
from nablamath.math.formal_languages import DFA
from nablamath.math.optimization import Constraint2, maximize_2d


def test_exact_polynomial_arithmetic_division_and_gcd():
    x_minus_one = Polynomial((-1, 1))
    x_plus_one = Polynomial((1, 1))
    square_minus_one = x_minus_one * x_plus_one
    quotient, remainder = square_minus_one.divmod(x_minus_one)
    assert quotient == x_plus_one and remainder.is_zero
    assert square_minus_one.derivative() == Polynomial((0, 2))
    assert polynomial_gcd(square_minus_one, x_minus_one * x_minus_one) == x_minus_one


def test_total_dfa_acceptance_and_reachability():
    transitions = {("even", "0"): "even", ("even", "1"): "odd", ("odd", "0"): "odd", ("odd", "1"): "even"}
    dfa = DFA(frozenset({"even", "odd"}), frozenset({"0", "1"}), "even", frozenset({"even"}), transitions)
    assert dfa.accepts("1011") is False
    assert dfa.accepts("1010") is True
    assert dfa.reachable() == frozenset({"even", "odd"})
    with pytest.raises(ValueError): dfa.accepts("2")


def test_exact_bounded_linear_optimization():
    constraints = (Constraint2(1, 1, 4), Constraint2(1, 0, 3), Constraint2(0, 1, 3))
    point, value = maximize_2d((3, 2), constraints, x_bounds=(0, 10), y_bounds=(0, 10))
    assert point == (Fraction(3), Fraction(1)) and value == 11
    with pytest.raises(ValueError):
        maximize_2d((1, 1), (Constraint2(1, 1, -1),), x_bounds=(0, 2), y_bounds=(0, 2))
