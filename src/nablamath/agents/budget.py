"""Cotas para candidatos; sem executar código de terceiros."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Budget:
    max_proposals: int = 100
    max_expression_chars: int = 4096

    def __post_init__(self) -> None:
        if not 1 <= self.max_proposals <= 100_000 or not 1 <= self.max_expression_chars <= 4096:
            raise ValueError("Cota fora dos limites")
