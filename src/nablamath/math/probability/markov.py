"""Cadeias de Markov finitas com probabilidades racionais exatas."""
from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping

@dataclass(frozen=True)
class MarkovChain:
    states: tuple[str,...]
    transition: Mapping[tuple[str,str],Fraction]
    def __post_init__(self)->None:
        if not self.states or len(set(self.states))!=len(self.states): raise ValueError("estados inválidos")
        expected={(a,b) for a in self.states for b in self.states}
        normalized={edge:Fraction(value) for edge,value in self.transition.items()}
        if set(normalized)!=expected or any(value<0 for value in normalized.values()): raise ValueError("matriz de transição inválida")
        for state in self.states:
            if sum((normalized[state,target] for target in self.states),Fraction())!=1: raise ValueError("linha não estocástica")
        object.__setattr__(self,"transition",normalized)
    def step(self,distribution:Mapping[str,Fraction])->dict[str,Fraction]:
        values={state:Fraction(distribution.get(state,0)) for state in self.states}
        if any(value<0 for value in values.values()) or sum(values.values(),Fraction())!=1: raise ValueError("distribuição inválida")
        return {target:sum((values[source]*self.transition[source,target] for source in self.states),Fraction()) for target in self.states}
    def evolve(self,distribution:Mapping[str,Fraction],steps:int)->dict[str,Fraction]:
        if not 0<=steps<=10_000_000: raise ValueError("passos fora do limite")
        result=dict(distribution)
        for _ in range(steps): result=self.step(result)
        return result
    def absorbing_states(self)->tuple[str,...]:
        return tuple(state for state in self.states if self.transition[state,state]==1)

__all__=["MarkovChain"]
