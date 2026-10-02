from fractions import Fraction
import pytest
from nablamath.math.set_theory import equivalence_classes, is_injective, is_surjective, power_set
from nablamath.math.game_theory import TwoPlayerGame
from nablamath.math.dynamical_systems import detect_cycle, iterate
from nablamath.math.information import decode, encode, is_prefix_free, kraft_sum
from nablamath.math.graph_theory import maximum_flow


def test_finite_sets_functions_and_quotients():
    values = frozenset(range(4))
    assert len(power_set(values)) == 16
    assert equivalence_classes(values, lambda a, b: a % 2 == b % 2) == (frozenset({0, 2}), frozenset({1, 3}))
    assert is_injective(values, lambda x: x + 1)
    assert is_surjective(values, frozenset({0, 1}), lambda x: x % 2)


def test_pure_game_equilibria_and_zero_sum_value():
    game = TwoPlayerGame(("H", "T"), ("H", "T"), {
        ("H", "H"): (1, -1), ("H", "T"): (-1, 1),
        ("T", "H"): (-1, 1), ("T", "T"): (1, -1),
    })
    assert game.is_zero_sum()
    assert game.pure_nash_equilibria() == ()
    assert game.pure_maximin_row()[1] == -1


def test_discrete_orbits_and_cycle_detection():
    assert iterate(lambda x: (x + 1) % 3, 0, 4) == (0, 1, 2, 0, 1)
    orbit = detect_cycle(lambda x: (2 * x + 1) % 5, 0)
    assert orbit.transient_length == 0 and orbit.period == 4


def test_prefix_codes_roundtrip_and_kraft():
    code = {"a": "0", "b": "10", "c": "11"}
    assert is_prefix_free(code) and kraft_sum(code) == 1
    bits = encode(("a", "c", "b"), code)
    assert decode(bits, code) == ("a", "c", "b")
    assert not is_prefix_free({"a": "0", "b": "01"})


def test_exact_maximum_flow():
    vertices = frozenset({"s", "a", "b", "t"})
    value, flow = maximum_flow(vertices, {("s", "a"): 3, ("s", "b"): 2, ("a", "b"): 1,
                                            ("a", "t"): 2, ("b", "t"): 3}, "s", "t")
    assert value == 5
    assert flow["s", "a"] + flow["s", "b"] == 5
    with pytest.raises(ValueError): maximum_flow(vertices, {("s", "t"): -1}, "s", "t")
