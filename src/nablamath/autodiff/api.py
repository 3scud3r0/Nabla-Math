"""Dependency-free automatic differentiation reference engine.

The module keeps the original forward-mode ``Dual`` API and adds a scalar
reverse-mode tape (``Var``), VJP/Jacobian helpers and exact second-order jets
for Hessians.  It is intentionally a correctness backend; accelerator lowering
belongs to a separate compiler/backend layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import cos as _cos, exp as _exp, isfinite, log as _log, sin as _sin, tanh as _tanh
from typing import Callable, Iterable, Sequence

NumberLike = float | int

@dataclass(frozen=True)
class Dual:
    primal: float
    tangent: float
    def __add__(self, other: "Dual | NumberLike") -> "Dual":
        b = other if isinstance(other, Dual) else Dual(float(other), 0.0)
        return Dual(self.primal + b.primal, self.tangent + b.tangent)
    __radd__ = __add__
    def __neg__(self) -> "Dual": return Dual(-self.primal, -self.tangent)
    def __sub__(self, other: "Dual | NumberLike") -> "Dual": return self + (-other if isinstance(other, Dual) else -float(other))
    def __rsub__(self, other: NumberLike) -> "Dual": return float(other) + (-self)
    def __mul__(self, other: "Dual | NumberLike") -> "Dual":
        b = other if isinstance(other, Dual) else Dual(float(other), 0.0)
        return Dual(self.primal*b.primal, self.tangent*b.primal+self.primal*b.tangent)
    __rmul__ = __mul__
    def __truediv__(self, other: "Dual | NumberLike") -> "Dual":
        b = other if isinstance(other, Dual) else Dual(float(other), 0.0)
        if b.primal == 0: raise ZeroDivisionError("divisão por zero em Dual")
        return Dual(self.primal / b.primal, (self.tangent*b.primal-self.primal*b.tangent)/(b.primal*b.primal))
    def __rtruediv__(self, other: NumberLike) -> "Dual": return Dual(float(other), 0.0) / self
    def __pow__(self, exponent: int) -> "Dual":
        if type(exponent) is not int or exponent < -32 or exponent > 32:
            raise ValueError("Este backend aceita potência inteira entre -32 e 32")
        if self.primal == 0 and exponent <= 0: raise ZeroDivisionError("potência fora do domínio")
        primal = self.primal**exponent
        tangent = 0.0 if exponent == 0 else exponent*self.primal**(exponent-1)*self.tangent
        return Dual(primal, tangent)
    def exp(self) -> "Dual":
        value = _exp(self.primal); return Dual(value, value*self.tangent)
    def log(self) -> "Dual":
        if self.primal <= 0: raise ValueError("log exige argumento positivo")
        return Dual(_log(self.primal), self.tangent/self.primal)
    def sin(self) -> "Dual": return Dual(_sin(self.primal), _cos(self.primal)*self.tangent)
    def cos(self) -> "Dual": return Dual(_cos(self.primal), -_sin(self.primal)*self.tangent)
    def tanh(self) -> "Dual":
        value = _tanh(self.primal); return Dual(value, (1-value*value)*self.tangent)


def jvp(f: Callable[[Dual], Dual], x: float, direction: float = 1) -> tuple[float, float]:
    output = f(Dual(float(x), float(direction)))
    if not isinstance(output, Dual) or not all(isfinite(v) for v in (output.primal, output.tangent)):
        raise ValueError("Função deve retornar Dual finito")
    return output.primal, output.tangent


class Var:
    """Scalar reverse-mode variable with an explicit, inspectable tape."""
    __slots__ = ("value", "grad", "requires_grad", "_parents", "op")
    def __init__(self, value: NumberLike, *, requires_grad: bool = True,
                 parents: tuple[tuple["Var", float], ...] = (), op: str = "leaf") -> None:
        value = float(value)
        if not isfinite(value): raise ValueError("Var exige valor finito")
        self.value = value
        self.grad = 0.0
        self.requires_grad = bool(requires_grad)
        self._parents = parents if self.requires_grad else ()
        self.op = op

    @staticmethod
    def _coerce(value: "Var | NumberLike") -> "Var":
        return value if isinstance(value, Var) else Var(float(value), requires_grad=False)

    def _binary(self, other: "Var | NumberLike", value: float, da: float, db: float, op: str) -> "Var":
        b = self._coerce(other)
        parents: list[tuple[Var, float]] = []
        if self.requires_grad: parents.append((self, da))
        if b.requires_grad: parents.append((b, db))
        return Var(value, requires_grad=bool(parents), parents=tuple(parents), op=op)

    def __add__(self, other: "Var | NumberLike") -> "Var":
        b=self._coerce(other); return self._binary(b, self.value+b.value, 1.0, 1.0, "add")
    __radd__=__add__
    def __neg__(self) -> "Var": return Var(-self.value, requires_grad=self.requires_grad, parents=((self,-1.0),) if self.requires_grad else (), op="neg")
    def __sub__(self, other: "Var | NumberLike") -> "Var": return self + (-self._coerce(other))
    def __rsub__(self, other: NumberLike) -> "Var": return self._coerce(other) - self
    def __mul__(self, other: "Var | NumberLike") -> "Var":
        b=self._coerce(other); return self._binary(b, self.value*b.value, b.value, self.value, "mul")
    __rmul__=__mul__
    def __truediv__(self, other: "Var | NumberLike") -> "Var":
        b=self._coerce(other)
        if b.value == 0: raise ZeroDivisionError("divisão por zero em Var")
        return self._binary(b, self.value/b.value, 1.0/b.value, -self.value/(b.value*b.value), "div")
    def __rtruediv__(self, other: NumberLike) -> "Var": return self._coerce(other)/self
    def __pow__(self, exponent: int) -> "Var":
        if type(exponent) is not int or exponent < -32 or exponent > 32: raise ValueError("Expoente inteiro esperado entre -32 e 32")
        if self.value == 0 and exponent <= 0: raise ZeroDivisionError("potência fora do domínio")
        value=self.value**exponent
        local=0.0 if exponent==0 else exponent*self.value**(exponent-1)
        return Var(value, requires_grad=self.requires_grad, parents=((self,local),) if self.requires_grad else (), op=f"pow:{exponent}")
    def exp(self) -> "Var":
        value=_exp(self.value); return Var(value, requires_grad=self.requires_grad, parents=((self,value),) if self.requires_grad else (), op="exp")
    def log(self) -> "Var":
        if self.value <= 0: raise ValueError("log exige argumento positivo")
        return Var(_log(self.value), requires_grad=self.requires_grad, parents=((self,1.0/self.value),) if self.requires_grad else (), op="log")
    def sin(self) -> "Var": return Var(_sin(self.value), requires_grad=self.requires_grad, parents=((self,_cos(self.value)),) if self.requires_grad else (), op="sin")
    def cos(self) -> "Var": return Var(_cos(self.value), requires_grad=self.requires_grad, parents=((self,-_sin(self.value)),) if self.requires_grad else (), op="cos")
    def tanh(self) -> "Var":
        value=_tanh(self.value); return Var(value, requires_grad=self.requires_grad, parents=((self,1-value*value),) if self.requires_grad else (), op="tanh")
    def detach(self) -> "Var": return Var(self.value, requires_grad=False)

    def _topological(self) -> list["Var"]:
        order: list[Var] = []
        seen: set[int] = set()
        stack: list[tuple[Var, bool]] = [(self, False)]
        while stack:
            node, expanded = stack.pop()
            marker = id(node)
            if expanded:
                order.append(node)
                continue
            if marker in seen:
                continue
            seen.add(marker)
            stack.append((node, True))
            for parent, _ in reversed(node._parents):
                if id(parent) not in seen:
                    stack.append((parent, False))
        return order

    def backward(self, seed: float = 1.0) -> None:
        seed=float(seed)
        if not isfinite(seed): raise ValueError("seed precisa ser finito")
        order=self._topological()
        for node in order: node.grad=0.0
        self.grad=seed
        for node in reversed(order):
            for parent,local in node._parents:
                parent.grad += node.grad*local


def value_and_grad(f: Callable[..., Var], *xs: float) -> tuple[float, tuple[float, ...]]:
    leaves=tuple(Var(x) for x in xs)
    output=f(*leaves)
    if not isinstance(output,Var): raise TypeError("A função diferenciável deve retornar Var")
    output.backward()
    return output.value, tuple(leaf.grad for leaf in leaves)


def grad(f: Callable[[Var], Var], x: float) -> float:
    _, gradients=value_and_grad(f,x); return gradients[0]


def vjp(f: Callable[..., Var], xs: Sequence[float], cotangent: float = 1.0) -> tuple[float, tuple[float, ...]]:
    leaves=tuple(Var(x) for x in xs); output=f(*leaves)
    if not isinstance(output,Var): raise TypeError("VJP escalar exige saída Var")
    output.backward(cotangent)
    return output.value, tuple(leaf.grad for leaf in leaves)


def jacobian(f: Callable[..., Var | Sequence[Var]], xs: Sequence[float]) -> tuple[tuple[float, ...], tuple[tuple[float, ...], ...]]:
    leaves=tuple(Var(x) for x in xs); raw=f(*leaves)
    outputs=(raw,) if isinstance(raw,Var) else tuple(raw)
    if not outputs or not all(isinstance(item,Var) for item in outputs): raise TypeError("Jacobian exige Var ou sequência não vazia de Var")
    rows=[]
    for output in outputs:
        for leaf in leaves: leaf.grad=0.0
        output.backward()
        rows.append(tuple(leaf.grad for leaf in leaves))
    return tuple(output.value for output in outputs), tuple(rows)


@dataclass(frozen=True)
class _Jet2:
    value: float
    gradient: tuple[float, ...]
    hessian: tuple[tuple[float, ...], ...]
    @classmethod
    def variable(cls, value: float, index: int, size: int) -> "_Jet2":
        g=tuple(1.0 if i==index else 0.0 for i in range(size)); z=tuple(tuple(0.0 for _ in range(size)) for _ in range(size)); return cls(float(value),g,z)
    @classmethod
    def constant(cls, value: float, size: int) -> "_Jet2":
        z=tuple(0.0 for _ in range(size)); return cls(float(value),z,tuple(z for _ in range(size)))
    def _coerce(self, other: "_Jet2 | NumberLike") -> "_Jet2": return other if isinstance(other,_Jet2) else _Jet2.constant(float(other),len(self.gradient))
    def __add__(self,other):
        b=self._coerce(other); n=len(self.gradient); return _Jet2(self.value+b.value,tuple(self.gradient[i]+b.gradient[i] for i in range(n)),tuple(tuple(self.hessian[i][j]+b.hessian[i][j] for j in range(n)) for i in range(n)))
    __radd__=__add__
    def __neg__(self): return self._unary(-self.value,-1.0,0.0)
    def __sub__(self,other): return self+(-self._coerce(other))
    def __rsub__(self,other): return self._coerce(other)-self
    def __mul__(self,other):
        b=self._coerce(other); n=len(self.gradient)
        g=tuple(self.gradient[i]*b.value+self.value*b.gradient[i] for i in range(n))
        h=tuple(tuple(self.hessian[i][j]*b.value+self.gradient[i]*b.gradient[j]+self.gradient[j]*b.gradient[i]+self.value*b.hessian[i][j] for j in range(n)) for i in range(n))
        return _Jet2(self.value*b.value,g,h)
    __rmul__=__mul__
    def _unary(self,value:float,first:float,second:float):
        n=len(self.gradient); g=tuple(first*self.gradient[i] for i in range(n)); h=tuple(tuple(second*self.gradient[i]*self.gradient[j]+first*self.hessian[i][j] for j in range(n)) for i in range(n)); return _Jet2(value,g,h)
    def reciprocal(self):
        if self.value==0: raise ZeroDivisionError
        return self._unary(1/self.value,-1/(self.value**2),2/(self.value**3))
    def __truediv__(self,other): return self*self._coerce(other).reciprocal()
    def __rtruediv__(self,other): return self._coerce(other)*self.reciprocal()
    def __pow__(self,exponent:int):
        if type(exponent) is not int or exponent < -32 or exponent > 32: raise ValueError("Expoente inteiro esperado entre -32 e 32")
        if self.value==0 and exponent<=0: raise ZeroDivisionError
        value=self.value**exponent; first=0.0 if exponent==0 else exponent*self.value**(exponent-1); second=0.0 if exponent in (0,1) else exponent*(exponent-1)*self.value**(exponent-2)
        return self._unary(value,first,second)
    def exp(self):
        value=_exp(self.value); return self._unary(value,value,value)
    def log(self):
        if self.value<=0: raise ValueError("log exige argumento positivo")
        return self._unary(_log(self.value),1/self.value,-1/(self.value*self.value))
    def sin(self): return self._unary(_sin(self.value),_cos(self.value),-_sin(self.value))
    def cos(self): return self._unary(_cos(self.value),-_sin(self.value),-_cos(self.value))
    def tanh(self):
        value=_tanh(self.value); first=1-value*value; return self._unary(value,first,-2*value*first)


def hessian(f: Callable[..., object], xs: Sequence[float]) -> tuple[float, tuple[float, ...], tuple[tuple[float, ...], ...]]:
    """Return value, gradient and Hessian using exact second-order AD rules."""
    n=len(xs)
    if n == 0: raise ValueError("Hessian exige ao menos uma variável")
    variables=tuple(_Jet2.variable(float(value),i,n) for i,value in enumerate(xs))
    output=f(*variables)
    if not isinstance(output,_Jet2): raise TypeError("A função de Hessian deve preservar os objetos diferenciáveis")
    return output.value,output.gradient,output.hessian


def exp(x): return x.exp() if isinstance(x,(Dual,Var,_Jet2)) else _exp(float(x))
def log(x): return x.log() if isinstance(x,(Dual,Var,_Jet2)) else _log(float(x))
def sin(x): return x.sin() if isinstance(x,(Dual,Var,_Jet2)) else _sin(float(x))
def cos(x): return x.cos() if isinstance(x,(Dual,Var,_Jet2)) else _cos(float(x))
def tanh(x): return x.tanh() if isinstance(x,(Dual,Var,_Jet2)) else _tanh(float(x))

__all__=["Dual","Var","jvp","value_and_grad","grad","vjp","jacobian","hessian","exp","log","sin","cos","tanh"]
