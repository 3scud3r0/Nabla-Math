"""Jogos finitos de dois jogadores e equilíbrios puros."""

from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping


@dataclass(frozen=True)
class TwoPlayerGame:
    rows: tuple[str, ...]
    columns: tuple[str, ...]
    payoffs: Mapping[tuple[str, str], tuple[Fraction, Fraction]]

    def __post_init__(self) -> None:
        if not self.rows or not self.columns or len(set(self.rows)) != len(self.rows) or len(set(self.columns)) != len(self.columns):
            raise ValueError("estratégias inválidas")
        expected = {(row, column) for row in self.rows for column in self.columns}
        if set(self.payoffs) != expected: raise ValueError("matriz de pagamentos deve ser total")
        object.__setattr__(self, "payoffs", {profile: (Fraction(values[0]), Fraction(values[1]))
                                             for profile, values in self.payoffs.items()})

    def pure_nash_equilibria(self) -> tuple[tuple[str, str], ...]:
        equilibria = []
        for row in self.rows:
            for column in self.columns:
                row_payoff, column_payoff = self.payoffs[row, column]
                row_best = all(row_payoff >= self.payoffs[candidate, column][0] for candidate in self.rows)
                column_best = all(column_payoff >= self.payoffs[row, candidate][1] for candidate in self.columns)
                if row_best and column_best: equilibria.append((row, column))
        return tuple(equilibria)

    def is_zero_sum(self) -> bool:
        return all(left + right == 0 for left, right in self.payoffs.values())

    def pure_maximin_row(self) -> tuple[str, Fraction]:
        scored = [(min(self.payoffs[row, column][0] for column in self.columns), row) for row in self.rows]
        value, row = max(scored, key=lambda item: (item[0], item[1]))
        return row, value


__all__ = ["TwoPlayerGame"]
