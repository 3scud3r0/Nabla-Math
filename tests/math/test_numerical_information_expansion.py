import math
from fractions import Fraction
import pytest
from nablamath.math.analysis import derivative, newton, second_derivative, simpson
from nablamath.math.information import cross_entropy, entropy, mutual_information, relative_entropy
from nablamath.math.polynomials import divided_differences, finite_differences, lagrange, newton_interpolation


def test_finite_differences_derivatives_and_simpson():
    assert derivative(lambda x: x**3, 2.0) == pytest.approx(12.0, rel=1e-9)
    assert derivative(lambda x: x**2, 2.0, method="forward") == pytest.approx(4.0, rel=1e-5)
    assert second_derivative(lambda x: x**2, 7.0) == pytest.approx(2.0, rel=1e-6)
    assert simpson(math.sin, 0, math.pi, 100) == pytest.approx(2.0, rel=1e-8)
    with pytest.raises(ValueError):
        simpson(math.sin, 0, 1, 3)


def test_newton_result_reports_convergence_and_failure():
    result = newton(lambda x: x*x-2, 1, derivative_function=lambda x: 2*x)
    assert result.converged and result.root == pytest.approx(math.sqrt(2))
    failure = newton(lambda x: x*x+1, 0, derivative_function=lambda _: 0)
    assert not failure.converged and failure.iterations == 0


def test_exact_polynomial_interpolation():
    points = ((0, 1), (1, 3), (2, 7), (3, 13))
    expected = (Fraction(1), Fraction(1), Fraction(1))
    assert lagrange(points).coefficients == expected
    assert newton_interpolation(points).coefficients == expected
    assert divided_differences(points) == (1, 2, 1, 0)
    assert finite_differences((1, 3, 7, 13))[-1] == (0,)
    with pytest.raises(ValueError):
        lagrange(((0, 1), (0, 2)))


def test_entropy_divergence_and_mutual_information():
    fair = {0: .5, 1: .5}; biased = {0: .75, 1: .25}
    assert entropy(fair) == 1 and relative_entropy(fair, fair) == 0
    assert cross_entropy(fair, biased) > entropy(fair)
    correlated = {(0, 0): .5, (0, 1): 0, (1, 0): 0, (1, 1): .5}
    assert mutual_information(correlated) == 1
    assert math.isinf(relative_entropy({0: 1., 1: 0.}, {0: 0., 1: 1.}))
