"""Geometria euclidiana plana exata sobre coordenadas racionais."""

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class Point2:
    x: Fraction
    y: Fraction
    def __post_init__(self) -> None:
        object.__setattr__(self, "x", Fraction(self.x)); object.__setattr__(self, "y", Fraction(self.y))


def squared_distance(left: Point2, right: Point2) -> Fraction:
    return (left.x - right.x) ** 2 + (left.y - right.y) ** 2


def orientation(a: Point2, b: Point2, c: Point2) -> int:
    determinant = (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)
    return (determinant > 0) - (determinant < 0)


def polygon_twice_signed_area(points: tuple[Point2, ...]) -> Fraction:
    if len(points) < 3: raise ValueError("polígono requer ao menos três pontos")
    return sum((point.x * points[(index + 1) % len(points)].y - point.y * points[(index + 1) % len(points)].x
                for index, point in enumerate(points)), Fraction())


__all__ = ["Point2", "orientation", "polygon_twice_signed_area", "squared_distance"]
