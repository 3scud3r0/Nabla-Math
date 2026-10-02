"""Sistemas lineares discretos densos sobre matrizes racionais."""
from dataclasses import dataclass
from ..linear_algebra import Matrix

@dataclass(frozen=True)
class DiscreteLinearSystem:
    state_matrix:Matrix
    input_matrix:Matrix
    def __post_init__(self)->None:
        rows,columns=self.state_matrix.shape
        if rows!=columns: raise ValueError("matriz de estado deve ser quadrada")
        if self.input_matrix.shape[0]!=rows: raise ValueError("matriz de entrada incompatível")
    def step(self,state:Matrix,control:Matrix)->Matrix:
        if state.shape!=(self.state_matrix.shape[0],1): raise ValueError("vetor de estado incompatível")
        if control.shape!=(self.input_matrix.shape[1],1): raise ValueError("vetor de controle incompatível")
        left=self.state_matrix@state; right=self.input_matrix@control
        return Matrix(tuple(tuple(a+b for a,b in zip(lrow,rrow,strict=True)) for lrow,rrow in zip(left.rows,right.rows,strict=True)))
    def simulate(self,initial:Matrix,controls:tuple[Matrix,...])->tuple[Matrix,...]:
        states=[initial]
        for control in controls:states.append(self.step(states[-1],control))
        return tuple(states)

__all__=["DiscreteLinearSystem"]
