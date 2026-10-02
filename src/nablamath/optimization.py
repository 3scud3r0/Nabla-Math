"""Canonical differentiable optimizers built on NablaMath reverse autodiff."""
from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Callable, Sequence

from .autodiff import Var, hessian, value_and_grad

Objective = Callable[..., Var | float]


@dataclass(frozen=True)
class OptimizationTrace:
    method: str
    points: tuple[tuple[float, ...], ...]
    values: tuple[float, ...]
    gradient_norms: tuple[float, ...]
    converged: bool
    reason: str

    @property
    def evaluations(self) -> int:
        return len(self.values)

    @property
    def best_index(self) -> int:
        if not self.values:
            raise ValueError("Traço vazio")
        return min(range(len(self.values)), key=self.values.__getitem__)

    @property
    def best_point(self) -> tuple[float, ...]:
        return self.points[self.best_index]

    @property
    def best_value(self) -> float:
        return self.values[self.best_index]


def _check_point(start: Sequence[float]) -> tuple[float, ...]:
    point = tuple(float(x) for x in start)
    if not point or not all(math.isfinite(x) for x in point):
        raise ValueError("Ponto inicial deve ser não vazio e finito")
    return point


def _value_gradient(objective: Objective, point: tuple[float, ...]) -> tuple[float, tuple[float, ...]]:
    value, gradient = value_and_grad(objective, *point)
    if not math.isfinite(value) or not all(math.isfinite(g) for g in gradient):
        raise ValueError("Objetivo ou gradiente não finito")
    return value, gradient


def _norm(vector: Sequence[float]) -> float:
    return math.sqrt(sum(value * value for value in vector))


def gradient_descent(objective: Objective, start: Sequence[float], *, learning_rate: float = 0.01,
                     steps: int = 1000, tolerance: float = 1e-8,
                     clip_gradient: float | None = None) -> OptimizationTrace:
    if not math.isfinite(learning_rate) or learning_rate <= 0:
        raise ValueError("learning_rate deve ser positivo e finito")
    if not 1 <= steps <= 10_000_000:
        raise ValueError("steps fora do intervalo")
    point = _check_point(start)
    points=[]; values=[]; norms=[]
    converged=False; reason="max_steps"
    for _ in range(steps):
        value, gradient = _value_gradient(objective, point)
        norm = _norm(gradient)
        points.append(point); values.append(value); norms.append(norm)
        if norm <= tolerance:
            converged=True; reason="gradient_tolerance"; break
        if clip_gradient is not None:
            if clip_gradient <= 0 or not math.isfinite(clip_gradient):
                raise ValueError("clip_gradient deve ser positivo e finito")
            if norm > clip_gradient:
                scale = clip_gradient / norm
                gradient = tuple(g * scale for g in gradient)
        point = tuple(x - learning_rate * g for x, g in zip(point, gradient))
    return OptimizationTrace("gradient_descent",tuple(points),tuple(values),tuple(norms),converged,reason)


def adam(objective: Objective, start: Sequence[float], *, learning_rate: float = 0.03,
         steps: int = 1000, beta1: float = 0.9, beta2: float = 0.999,
         epsilon: float = 1e-8, tolerance: float = 1e-8) -> OptimizationTrace:
    if not (0 <= beta1 < 1 and 0 <= beta2 < 1):
        raise ValueError("beta1 e beta2 devem estar em [0,1)")
    if learning_rate <= 0 or epsilon <= 0 or steps < 1:
        raise ValueError("Parâmetros de Adam inválidos")
    point=_check_point(start); m=[0.0]*len(point); v=[0.0]*len(point)
    points=[]; values=[]; norms=[]; converged=False; reason="max_steps"
    for t in range(1, steps+1):
        value, gradient=_value_gradient(objective,point); norm=_norm(gradient)
        points.append(point); values.append(value); norms.append(norm)
        if norm <= tolerance:
            converged=True; reason="gradient_tolerance"; break
        updated=[]
        for i,g in enumerate(gradient):
            m[i]=beta1*m[i]+(1-beta1)*g
            v[i]=beta2*v[i]+(1-beta2)*g*g
            mhat=m[i]/(1-beta1**t); vhat=v[i]/(1-beta2**t)
            updated.append(point[i]-learning_rate*mhat/(math.sqrt(vhat)+epsilon))
        point=tuple(updated)
    return OptimizationTrace("adam",tuple(points),tuple(values),tuple(norms),converged,reason)


def rmsprop(objective: Objective, start: Sequence[float], *, learning_rate: float = 0.01,
            steps: int = 1000, decay: float = 0.9, epsilon: float = 1e-8,
            tolerance: float = 1e-8) -> OptimizationTrace:
    if not 0 <= decay < 1 or learning_rate <= 0 or epsilon <= 0 or steps < 1:
        raise ValueError("Parâmetros de RMSProp inválidos")
    point=_check_point(start); average=[0.0]*len(point)
    points=[]; values=[]; norms=[]; converged=False; reason="max_steps"
    for _ in range(steps):
        value,gradient=_value_gradient(objective,point); norm=_norm(gradient)
        points.append(point); values.append(value); norms.append(norm)
        if norm <= tolerance:
            converged=True; reason="gradient_tolerance"; break
        updated=[]
        for i,g in enumerate(gradient):
            average[i]=decay*average[i]+(1-decay)*g*g
            updated.append(point[i]-learning_rate*g/(math.sqrt(average[i])+epsilon))
        point=tuple(updated)
    return OptimizationTrace("rmsprop",tuple(points),tuple(values),tuple(norms),converged,reason)


def _solve(matrix: Sequence[Sequence[float]], rhs: Sequence[float]) -> tuple[float, ...]:
    n=len(rhs); a=[list(map(float,row))+[float(rhs[i])] for i,row in enumerate(matrix)]
    if n == 0 or len(a)!=n or any(len(row)!=n+1 for row in a):
        raise ValueError("Sistema de Newton inválido")
    for col in range(n):
        pivot=max(range(col,n), key=lambda row: abs(a[row][col]))
        if abs(a[pivot][col]) < 1e-15:
            raise ValueError("Hessiana singular")
        a[col],a[pivot]=a[pivot],a[col]
        for row in range(col+1,n):
            factor=a[row][col]/a[col][col]
            for j in range(col,n+1): a[row][j]-=factor*a[col][j]
    x=[0.0]*n
    for row in range(n-1,-1,-1):
        x[row]=(a[row][n]-sum(a[row][j]*x[j] for j in range(row+1,n)))/a[row][row]
    return tuple(x)


def newton(objective: Callable[..., object], start: Sequence[float], *, steps: int = 100,
           damping: float = 1e-8, tolerance: float = 1e-8) -> OptimizationTrace:
    if steps < 1 or damping < 0 or not math.isfinite(damping):
        raise ValueError("Parâmetros de Newton inválidos")
    point=_check_point(start); points=[]; values=[]; norms=[]; converged=False; reason="max_steps"
    for _ in range(steps):
        value,gradient,matrix=hessian(objective,point)
        norm=_norm(gradient); points.append(point); values.append(value); norms.append(norm)
        if norm <= tolerance:
            converged=True; reason="gradient_tolerance"; break
        regularized=tuple(tuple(value_ + (damping if i==j else 0.0) for j,value_ in enumerate(row)) for i,row in enumerate(matrix))
        try:
            delta=_solve(regularized,gradient)
        except ValueError:
            reason="singular_hessian"; break
        point=tuple(x-d for x,d in zip(point,delta))
    return OptimizationTrace("newton",tuple(points),tuple(values),tuple(norms),converged,reason)


def _plain_value(objective: Objective, point: Sequence[float]) -> float:
    result=objective(*point)
    value=result.value if isinstance(result,Var) else float(result)
    return value if math.isfinite(value) else math.inf


def simulated_annealing(objective: Objective, bounds: Sequence[tuple[float,float]], *, steps: int = 2000,
                        initial_temperature: float = 1.0, final_temperature: float = 1e-3,
                        seed: int = 42) -> OptimizationTrace:
    bounds=tuple((float(lo),float(hi)) for lo,hi in bounds)
    if not bounds or any(not(math.isfinite(lo) and math.isfinite(hi) and lo<hi) for lo,hi in bounds):
        raise ValueError("Bounds inválidos")
    if steps < 1 or initial_temperature <= 0 or final_temperature <= 0:
        raise ValueError("Parâmetros de annealing inválidos")
    rng=random.Random(seed); point=tuple(rng.uniform(lo,hi) for lo,hi in bounds)
    value=_plain_value(objective,point); best_point=point; best_value=value
    points=[]; values=[]
    for step in range(steps):
        alpha=step/max(1,steps-1)
        temperature=initial_temperature*((final_temperature/initial_temperature)**alpha)
        proposal=[]
        for x,(lo,hi) in zip(point,bounds):
            scale=(hi-lo)*0.08*(1-alpha+0.05)
            proposal.append(min(hi,max(lo,x+rng.gauss(0,scale))))
        proposal=tuple(proposal); candidate=_plain_value(objective,proposal)
        delta=candidate-value
        if delta <= 0 or rng.random() < math.exp(-delta/max(temperature,1e-300)):
            point,value=proposal,candidate
        if value < best_value: best_point,best_value=point,value
        points.append(best_point); values.append(best_value)
    return OptimizationTrace("simulated_annealing",tuple(points),tuple(values),tuple(float("nan") for _ in values),True,"budget_exhausted")


@dataclass(frozen=True)
class HyperparameterTrial:
    learning_rate: float
    trace: OptimizationTrace


@dataclass(frozen=True)
class SelfImprovingResult:
    trials: tuple[HyperparameterTrial, ...]
    pareto_frontier: tuple[HyperparameterTrial, ...]

    @property
    def best(self) -> HyperparameterTrial:
        return min(self.trials,key=lambda trial:trial.trace.best_value)


class SelfImprovingOptimizer:
    """Budgeted deterministic meta-search over gradient-descent learning rates."""
    def __init__(self, objective: Objective, start: Sequence[float], *, budget: int = 8,
                 steps_per_trial: int = 300, seed_rates: Sequence[float] = (0.1,0.03,0.01)) -> None:
        self.objective=objective; self.start=_check_point(start); self.budget=int(budget)
        self.steps_per_trial=int(steps_per_trial); self.seed_rates=tuple(float(x) for x in seed_rates)
        if not 1 <= self.budget <= 1000 or self.steps_per_trial < 1:
            raise ValueError("Orçamento inválido")
        if not self.seed_rates or any(rate <= 0 or not math.isfinite(rate) for rate in self.seed_rates):
            raise ValueError("Taxas sementes inválidas")

    def run(self) -> SelfImprovingResult:
        pending=list(dict.fromkeys(self.seed_rates)); seen=set(); trials=[]
        while pending and len(trials) < self.budget:
            rate=pending.pop(0)
            if rate in seen: continue
            seen.add(rate)
            trace=gradient_descent(self.objective,self.start,learning_rate=rate,steps=self.steps_per_trial)
            trials.append(HyperparameterTrial(rate,trace))
            best=min(trials,key=lambda item:item.trace.best_value)
            for factor in (0.5,0.8,1.2,2.0):
                candidate=best.learning_rate*factor
                if 1e-8 <= candidate <= 10 and candidate not in seen and candidate not in pending:
                    pending.append(candidate)
        frontier=[]
        for trial in trials:
            dominated=False
            for other in trials:
                if other is trial: continue
                better_value=other.trace.best_value <= trial.trace.best_value
                lower_cost=other.trace.evaluations <= trial.trace.evaluations
                strictly=other.trace.best_value < trial.trace.best_value or other.trace.evaluations < trial.trace.evaluations
                if better_value and lower_cost and strictly:
                    dominated=True; break
            if not dominated: frontier.append(trial)
        frontier.sort(key=lambda item:(item.trace.best_value,item.trace.evaluations,item.learning_rate))
        return SelfImprovingResult(tuple(trials),tuple(frontier))


__all__=[
    "OptimizationTrace","gradient_descent","adam","rmsprop","newton","simulated_annealing",
    "HyperparameterTrial","SelfImprovingResult","SelfImprovingOptimizer",
]
