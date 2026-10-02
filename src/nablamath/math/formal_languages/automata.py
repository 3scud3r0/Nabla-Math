"""Autômatos finitos determinísticos totais."""

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class DFA:
    states: frozenset[str]
    alphabet: frozenset[str]
    start: str
    accepting: frozenset[str]
    transitions: Mapping[tuple[str, str], str]

    def __post_init__(self) -> None:
        if not self.states or self.start not in self.states or not self.accepting <= self.states:
            raise ValueError("estados inicial/finais inválidos")
        if not self.alphabet or any(len(symbol) != 1 for symbol in self.alphabet): raise ValueError("alfabeto inválido")
        expected = {(state, symbol) for state in self.states for symbol in self.alphabet}
        if set(self.transitions) != expected or any(target not in self.states for target in self.transitions.values()):
            raise ValueError("função de transição deve ser total")

    def run(self, word: str) -> str:
        state = self.start
        for symbol in word:
            if symbol not in self.alphabet: raise ValueError(f"símbolo fora do alfabeto: {symbol}")
            state = self.transitions[state, symbol]
        return state

    def accepts(self, word: str) -> bool: return self.run(word) in self.accepting

    def reachable(self) -> frozenset[str]:
        found = {self.start}; pending = [self.start]
        while pending:
            state = pending.pop()
            for symbol in self.alphabet:
                target = self.transitions[state, symbol]
                if target not in found: found.add(target); pending.append(target)
        return frozenset(found)


__all__ = ["DFA"]
