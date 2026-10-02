from fractions import Fraction
import pytest
from nablamath.math.graph_theory import strongly_connected_components, transitive_closure
from nablamath.math.graph_theory.directed import topological_sort
from nablamath.math.operations_research import Job, build_schedule, earliest_due_date, maximum_lateness, shortest_processing_time, total_weighted_completion, weighted_shortest_processing_time
from nablamath.math.statistics import autocorrelation, differences, exponential_smoothing, linear_trend, moving_average


def test_single_machine_scheduling_rules_and_metrics():
    jobs = (Job("long", 4, due_date=9, weight=8), Job("short", 1, due_date=3), Job("medium", 2, due_date=4))
    assert [j.identifier for j in shortest_processing_time(jobs)] == ["short", "medium", "long"]
    assert [j.identifier for j in earliest_due_date(jobs)] == ["short", "medium", "long"]
    assert [j.identifier for j in weighted_shortest_processing_time(jobs)] == ["long", "short", "medium"]
    schedule = build_schedule(shortest_processing_time(jobs))
    assert schedule[-1].completion == 7 and maximum_lateness(schedule) == -1
    assert total_weighted_completion(schedule) == Fraction(60)


def test_job_and_schedule_reject_invalid_input():
    with pytest.raises(ValueError): Job("zero", 0)
    with pytest.raises(ValueError): build_schedule((Job("same", 1), Job("same", 2)))


def test_directed_graph_components_closure_and_order():
    graph = {"a": ("b",), "b": ("a", "c"), "c": ("d",), "d": ("c",), "e": ()}
    assert set(strongly_connected_components(graph)) == {frozenset(("a", "b")), frozenset(("c", "d")), frozenset(("e",))}
    assert transitive_closure(graph)["a"] == frozenset(("a", "b", "c", "d"))
    assert topological_sort({"compile": ("test",), "test": ("ship",), "ship": ()}) == ("compile", "test", "ship")
    with pytest.raises(ValueError): topological_sort({"a": ("b",), "b": ("a",)})


def test_time_series_transforms_and_statistics():
    assert differences((1, 4, 9, 16), 2) == (2., 2.)
    assert moving_average((1, 2, 3, 4), 2) == (1.5, 2.5, 3.5)
    assert exponential_smoothing((10, 14, 14), .5) == (10., 12., 13.)
    assert linear_trend((2, 5, 8, 11)) == pytest.approx((2, 3))
    assert autocorrelation((1, 2, 3), 0) == 1
    with pytest.raises(ValueError): autocorrelation((4, 4, 4))
