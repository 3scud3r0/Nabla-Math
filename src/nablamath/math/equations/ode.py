"""Integradores explícitos limitados para sistemas de ODEs em ponto flutuante."""
import math
from collections.abc import Callable

State=tuple[float,...]
Derivative=Callable[[float,State],State]

def _combine(state:State, derivative:State, scale:float)->State:
    if len(state)!=len(derivative): raise ValueError("dimensão da derivada incompatível")
    return tuple(value+scale*delta for value,delta in zip(state,derivative,strict=True))

def euler_step(function:Derivative,time:float,state:State,step:float)->State:
    if not step>0 or not math.isfinite(step): raise ValueError("passo inválido")
    result=_combine(state,function(time,state),step)
    if not all(math.isfinite(value) for value in result): raise ValueError("estado não finito")
    return result

def rk4_step(function:Derivative,time:float,state:State,step:float)->State:
    if not step>0 or not math.isfinite(step): raise ValueError("passo inválido")
    k1=function(time,state)
    k2=function(time+step/2,_combine(state,k1,step/2))
    k3=function(time+step/2,_combine(state,k2,step/2))
    k4=function(time+step,_combine(state,k3,step))
    if not all(len(k)==len(state) for k in (k1,k2,k3,k4)): raise ValueError("dimensão incompatível")
    result=tuple(value+step*(a+2*b+2*c+d)/6 for value,a,b,c,d in zip(state,k1,k2,k3,k4,strict=True))
    if not all(math.isfinite(value) for value in result): raise ValueError("estado não finito")
    return result

def integrate(function:Derivative,initial:State,start:float,end:float,steps:int,method:str="rk4")->tuple[tuple[float,State],...]:
    if not 1<=steps<=10_000_000 or not start<end: raise ValueError("intervalo ou passos inválidos")
    operation={"euler":euler_step,"rk4":rk4_step}.get(method)
    if operation is None: raise ValueError("método desconhecido")
    step=(end-start)/steps; time=start; state=tuple(float(v) for v in initial); result=[(time,state)]
    for _ in range(steps): state=operation(function,time,state,step); time+=step; result.append((time,state))
    return tuple(result)

__all__=["euler_step","integrate","rk4_step"]
