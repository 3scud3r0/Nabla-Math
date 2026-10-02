"""Execution backends for NablaMath compiler IR.

The python backend is dependency-free and preserves Python/Fraction arithmetic.
The jax backend is loaded lazily and is optional; when installed it can JIT the
same IR to whatever devices JAX exposes. No accelerator is claimed unless JAX
itself reports one at runtime.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Callable, Mapping

from .ir import Program, bind_symbols


class BackendUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class DeviceInfo:
    backend: str
    platform: str
    device_kind: str
    id: int


class CompiledExpression:
    def __init__(self, program: Program, backend: str, runner: Callable[..., Any],
                 *, grad_builder: Callable[[int], Callable[..., Any]] | None = None,
                 devices: tuple[DeviceInfo, ...] = ()) -> None:
        self.program = program
        self.backend = backend
        self._runner = runner
        self._grad_builder = grad_builder
        self.devices = devices

    def __call__(self, values: Mapping[str, object]) -> object:
        return self._runner(*bind_symbols(self.program, values))

    def value_and_grad(self, values: Mapping[str, object], wrt: str) -> tuple[object, object]:
        if wrt not in self.program.symbols:
            raise ValueError(f"Símbolo não declarado: {wrt}")
        if self._grad_builder is None:
            raise BackendUnavailable(f"Backend {self.backend} não fornece autodiff compilado")
        args = bind_symbols(self.program, values)
        index = self.program.symbols.index(wrt)
        return self._grad_builder(index)(*args)


def _execute(program: Program, args: tuple[object, ...]) -> object:
    env: list[object] = []
    symbol_values = dict(zip(program.symbols, args))
    for instruction in program.instructions:
        if instruction.op == "number":
            env.append(instruction.value)
            continue
        if instruction.op == "symbol":
            env.append(symbol_values[str(instruction.value)])
            continue
        a, b = (env[index] for index in instruction.args)
        if instruction.op == "+":
            value = a + b
        elif instruction.op == "-":
            value = a - b
        elif instruction.op == "*":
            value = a * b
        elif instruction.op == "/":
            value = a / b
        elif instruction.op == "**":
            exponent_value = b
            if isinstance(exponent_value, Fraction):
                exponent_value = exponent_value.numerator
            value = a ** exponent_value
        else:
            raise RuntimeError(f"Operador de IR desconhecido: {instruction.op}")
        env.append(value)
    return env[program.output]


def compile_python(program: Program) -> CompiledExpression:
    program.validate()
    return CompiledExpression(program, "python", lambda *args: _execute(program, args))


def _jax_modules():
    try:
        import jax
        import jax.numpy as jnp
    except ImportError as exc:
        raise BackendUnavailable("Backend JAX não instalado; instale JAX para aceleração") from exc
    return jax, jnp


def jax_available() -> bool:
    try:
        _jax_modules()
    except BackendUnavailable:
        return False
    return True


def jax_devices() -> tuple[DeviceInfo, ...]:
    jax, _ = _jax_modules()
    result = []
    for index, device in enumerate(jax.devices()):
        result.append(DeviceInfo(
            backend="jax",
            platform=str(getattr(device, "platform", "unknown")),
            device_kind=str(getattr(device, "device_kind", type(device).__name__)),
            id=index,
        ))
    return tuple(result)


def compile_jax(program: Program, *, jit: bool = True) -> CompiledExpression:
    program.validate()
    jax, jnp = _jax_modules()

    def runner(*args):
        env = []
        symbol_values = dict(zip(program.symbols, args))
        for instruction in program.instructions:
            if instruction.op == "number":
                value = instruction.value
                assert isinstance(value, Fraction)
                env.append(jnp.asarray(value.numerator / value.denominator))
                continue
            if instruction.op == "symbol":
                env.append(symbol_values[str(instruction.value)])
                continue
            a, b = (env[index] for index in instruction.args)
            if instruction.op == "+":
                value = a + b
            elif instruction.op == "-":
                value = a - b
            elif instruction.op == "*":
                value = a * b
            elif instruction.op == "/":
                value = a / b
            elif instruction.op == "**":
                value = a ** b
            else:
                raise RuntimeError(f"Operador de IR desconhecido: {instruction.op}")
            env.append(value)
        return env[program.output]

    executable = jax.jit(runner) if jit else runner

    def grad_builder(index: int):
        vg = jax.value_and_grad(runner, argnums=index)
        return jax.jit(vg) if jit else vg

    return CompiledExpression(program, "jax", executable, grad_builder=grad_builder, devices=jax_devices())


def compile_program(program: Program, *, backend: str = "python", jit: bool = True) -> CompiledExpression:
    normalized = backend.strip().lower()
    if normalized == "python":
        return compile_python(program)
    if normalized == "jax":
        return compile_jax(program, jit=jit)
    raise ValueError(f"Backend desconhecido: {backend}")


__all__ = [
    "BackendUnavailable", "DeviceInfo", "CompiledExpression", "compile_python",
    "compile_jax", "compile_program", "jax_available", "jax_devices",
]