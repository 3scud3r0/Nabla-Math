"""Atualização bayesiana finita com probabilidades racionais exatas."""
from fractions import Fraction
from typing import Mapping,TypeVar
H=TypeVar("H")

def posterior(prior:Mapping[H,Fraction],likelihood:Mapping[H,Fraction])->dict[H,Fraction]:
    hypotheses=set(prior)
    if not hypotheses or set(likelihood)!=hypotheses: raise ValueError("hipóteses incompatíveis")
    p={key:Fraction(value) for key,value in prior.items()}; l={key:Fraction(value) for key,value in likelihood.items()}
    if any(value<0 for value in p.values()) or sum(p.values(),Fraction())!=1: raise ValueError("prior inválido")
    if any(not 0<=value<=1 for value in l.values()): raise ValueError("likelihood inválida")
    evidence=sum((p[key]*l[key] for key in hypotheses),Fraction())
    if evidence==0: raise ValueError("evidência possui probabilidade zero")
    return {key:p[key]*l[key]/evidence for key in sorted(hypotheses,key=repr)}

def predictive(prior:Mapping[H,Fraction],likelihood:Mapping[H,Fraction])->Fraction:
    return sum((Fraction(prior[key])*Fraction(likelihood[key]) for key in prior),Fraction())

__all__=["posterior","predictive"]
