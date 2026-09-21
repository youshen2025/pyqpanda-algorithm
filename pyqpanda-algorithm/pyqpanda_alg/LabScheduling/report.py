"""End-to-end reports and compact, machine-readable CLI output."""

from __future__ import annotations

import hashlib
import platform
from importlib.metadata import version
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np

from .classical import solve_exact
from .model import compile_qubo, evaluate
from .problem import load_problem
from .quantum import solve_qaoa


def run_experiment(
    path: str | Path,
    seed: int = 7,
    layers: int = 1,
    shots: int = 512,
    maxiter: int = 60,
    restarts: int = 2,
    mixer: str = "xy",
) -> dict[str, Any]:
    """Run QAOA before exact certification and attach input/environment provenance."""
    started = perf_counter()
    path = Path(path)
    problem = load_problem(path)
    model = compile_qubo(problem)
    quantum = solve_qaoa(model, seed, layers, shots, maxiter, restarts, mixer)
    exact = solve_exact(model)
    uniform_started = perf_counter()
    random = np.random.default_rng(seed)
    uniform_best = None
    feasible_samples = 0
    if all(model.domains):
        for _ in range(shots):
            bits = [0] * len(model.variables)
            for domain in model.domains:
                bits[int(random.choice(domain))] = 1
            candidate = evaluate(model, bits)
            feasible_samples += candidate["feasible"]
            if uniform_best is None or (
                not candidate["feasible"],
                candidate["qubo_energy"],
            ) < (not uniform_best["feasible"], uniform_best["qubo_energy"]):
                uniform_best = candidate
    uniform = {
        "best": uniform_best,
        "shots": shots,
        "seed": seed,
        "feasible_probability": (
            exact["feasible_count"] / exact["combinations"]
            if exact["combinations"]
            else 0.0
        ),
        "sampled_feasible_fraction": feasible_samples / shots,
        "runtime_seconds": perf_counter() - uniform_started,
    }
    quantum_best, exact_best = quantum["best"], exact["best"]
    gap = (
        quantum_best["objective"] - exact_best["objective"]
        if quantum_best and quantum_best["feasible"] and exact_best
        else None
    )
    if gap is not None and gap < 0:
        raise RuntimeError(
            "quantum result contradicts the independent exact certificate"
        )
    return {
        "schema_version": 1,
        "problem": problem.name,
        "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.system(),
            **{
                name: version(name)
                for name in ("pyqpanda3", "pyqpanda_alg", "numpy", "scipy")
            },
        },
        "model": model.audit(),
        "quantum": quantum,
        "exact": exact,
        "uniform_one_hot": uniform,
        "absolute_gap": gap,
        "status": (
            "infeasible"
            if exact["status"] == "infeasible"
            else "feasible"
            if quantum_best and quantum_best["feasible"]
            else "no_feasible_sample"
        ),
        "runtime_seconds": perf_counter() - started,
    }
