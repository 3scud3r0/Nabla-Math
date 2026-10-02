"""Deterministic execution planning for compiler IR across logical devices.

This module creates a *plan* only.  It does not claim NCCL, MPI, CUDA streams,
remote execution or multi-GPU speedup.  The purpose is to make placement,
cross-shard dependencies and cost estimates explicit and auditable before a
runtime backend implements the transport/execution layer.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Mapping, Sequence

from .ir import Program


@dataclass(frozen=True)
class LogicalDevice:
    name: str
    capacity: float = 1.0

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Dispositivo lógico precisa de nome")
        if not math.isfinite(self.capacity) or self.capacity <= 0:
            raise ValueError("Capacidade precisa ser positiva e finita")


@dataclass(frozen=True)
class ExecutionShard:
    id: int
    device: str
    instruction_ids: tuple[int, ...]
    dependencies: tuple[int, ...]
    estimated_cost: float

    def to_data(self) -> dict[str, object]:
        return {
            "id": self.id,
            "device": self.device,
            "instruction_ids": list(self.instruction_ids),
            "dependencies": list(self.dependencies),
            "estimated_cost": self.estimated_cost,
        }


@dataclass(frozen=True)
class ExecutionPlan:
    program_id: str
    devices: tuple[LogicalDevice, ...]
    shards: tuple[ExecutionShard, ...]
    output_shard: int
    schema_version: int = 1

    def validate(self, program: Program) -> None:
        program.validate()
        if self.program_id != program.content_id:
            raise ValueError("Plano não corresponde ao programa")
        names = tuple(device.name for device in self.devices)
        if len(set(names)) != len(names):
            raise ValueError("Nomes de dispositivos precisam ser únicos")
        if not self.shards:
            raise ValueError("Plano vazio")
        shard_ids = {shard.id for shard in self.shards}
        if shard_ids != set(range(len(self.shards))):
            raise ValueError("IDs de shards devem ser densos e começar em zero")
        owner: dict[int, int] = {}
        for shard in self.shards:
            if shard.device not in names:
                raise ValueError("Shard usa dispositivo não declarado")
            if not shard.instruction_ids:
                raise ValueError("Shard sem instruções")
            if not math.isfinite(shard.estimated_cost) or shard.estimated_cost < 0:
                raise ValueError("Custo de shard inválido")
            if any(dep >= shard.id or dep < 0 for dep in shard.dependencies):
                raise ValueError("Dependência de shard viola ordem topológica")
            for instruction_id in shard.instruction_ids:
                if instruction_id in owner:
                    raise ValueError("Instrução atribuída a mais de um shard")
                owner[instruction_id] = shard.id
        expected = set(range(len(program.instructions)))
        if set(owner) != expected:
            raise ValueError("Plano não cobre exatamente todas as instruções")
        for instruction in program.instructions:
            shard_id = owner[instruction.id]
            actual_dependencies = {
                owner[arg] for arg in instruction.args if owner[arg] != shard_id
            }
            declared = set(self.shards[shard_id].dependencies)
            if not actual_dependencies <= declared:
                raise ValueError("Dependência cruzada ausente no shard")
        if self.output_shard != owner[program.output]:
            raise ValueError("output_shard não contém a saída do programa")

    def to_data(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "program_id": self.program_id,
            "devices": [
                {"name": device.name, "capacity": device.capacity}
                for device in self.devices
            ],
            "shards": [shard.to_data() for shard in self.shards],
            "output_shard": self.output_shard,
        }

    @property
    def content_id(self) -> str:
        canonical = json.dumps(
            self.to_data(), sort_keys=True, separators=(",", ":"), ensure_ascii=True
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def instruction_costs(
    program: Program,
    operation_costs: Mapping[str, float] | None = None,
) -> tuple[float, ...]:
    """Return validated per-instruction costs using a backend-neutral model."""
    weights = {
        "number": 0.05,
        "symbol": 0.05,
        "+": 1.0,
        "-": 1.0,
        "*": 1.2,
        "/": 4.0,
        "**": 6.0,
    }
    if operation_costs:
        for op, cost in operation_costs.items():
            numeric = float(cost)
            if not math.isfinite(numeric) or numeric < 0:
                raise ValueError("Custos de operação precisam ser finitos e não negativos")
            weights[op] = numeric
    return tuple(weights.get(instruction.op, 1.0) for instruction in program.instructions)


def _target_cost(total_cost: float, devices: Sequence[LogicalDevice]) -> tuple[float, ...]:
    capacity_sum = sum(device.capacity for device in devices)
    return tuple(total_cost * device.capacity / capacity_sum for device in devices)


def plan_execution(
    program: Program,
    devices: Sequence[LogicalDevice | str],
    *,
    operation_costs: Mapping[str, float] | None = None,
    max_shards_per_device: int = 1,
) -> ExecutionPlan:
    """Partition topological IR into deterministic contiguous execution shards.

    Contiguous ranges preserve the program's topological order and make transfer
    boundaries explicit.  Capacity weights control how much estimated work each
    logical device receives; they are not benchmark-derived performance claims.
    """
    program.validate()
    normalized = tuple(
        device if isinstance(device, LogicalDevice) else LogicalDevice(str(device))
        for device in devices
    )
    if not normalized:
        raise ValueError("Ao menos um dispositivo lógico é necessário")
    if len({device.name for device in normalized}) != len(normalized):
        raise ValueError("Nomes de dispositivos precisam ser únicos")
    if (isinstance(max_shards_per_device, bool) or not isinstance(max_shards_per_device, int)
            or max_shards_per_device < 1):
        raise ValueError("max_shards_per_device deve ser inteiro positivo")

    costs = instruction_costs(program, operation_costs)
    total = sum(costs)
    shard_budget = min(
        len(program.instructions),
        len(normalized) * max_shards_per_device,
    )
    # A zero-cost program still needs deterministic non-empty ranges.
    cumulative_targets = [
        total * (index + 1) / shard_budget for index in range(shard_budget - 1)
    ]
    boundaries: list[int] = []
    running = 0.0
    target_index = 0
    for instruction_id, cost in enumerate(costs):
        running += cost
        while (target_index < len(cumulative_targets)
               and running >= cumulative_targets[target_index]
               and instruction_id + 1 < len(program.instructions)):
            minimum_remaining = len(cumulative_targets) - target_index
            if len(program.instructions) - (instruction_id + 1) >= minimum_remaining:
                boundaries.append(instruction_id + 1)
                target_index += 1
            else:
                break
    # If skewed costs did not create enough boundaries, split remaining legal gaps.
    candidate = 1
    while len(boundaries) < shard_budget - 1:
        if candidate not in boundaries and candidate < len(program.instructions):
            boundaries.append(candidate)
        candidate += 1
    boundaries.sort()
    ranges: list[tuple[int, int]] = []
    start = 0
    for end in boundaries[: shard_budget - 1]:
        if end > start:
            ranges.append((start, end))
            start = end
    ranges.append((start, len(program.instructions)))

    # Assign ranges to devices by normalized accumulated load/capacity.
    assigned_cost = {device.name: 0.0 for device in normalized}
    shard_device: list[LogicalDevice] = []
    for start, end in ranges:
        device = min(
            normalized,
            key=lambda d: (assigned_cost[d.name] / d.capacity, d.name),
        )
        shard_device.append(device)
        assigned_cost[device.name] += sum(costs[start:end])

    instruction_owner: dict[int, int] = {}
    for shard_id, (start, end) in enumerate(ranges):
        for instruction_id in range(start, end):
            instruction_owner[instruction_id] = shard_id

    shards: list[ExecutionShard] = []
    for shard_id, ((start, end), device) in enumerate(zip(ranges, shard_device)):
        dependencies = set()
        for instruction in program.instructions[start:end]:
            for arg in instruction.args:
                owner = instruction_owner[arg]
                if owner != shard_id:
                    dependencies.add(owner)
        shards.append(ExecutionShard(
            shard_id,
            device.name,
            tuple(range(start, end)),
            tuple(sorted(dependencies)),
            sum(costs[start:end]),
        ))
    plan = ExecutionPlan(
        program.content_id,
        normalized,
        tuple(shards),
        instruction_owner[program.output],
    )
    plan.validate(program)
    return plan


__all__ = [
    "LogicalDevice", "ExecutionShard", "ExecutionPlan", "instruction_costs",
    "plan_execution",
]
