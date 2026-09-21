"""Independent exact certification by Cartesian enumeration of task choices."""

from itertools import product
from math import prod
from time import perf_counter
from typing import Any

from .model import Model, evaluate


def solve_exact(model: Model, max_combinations: int = 1_000_000) -> dict[str, Any]:
    """Certify the optimum using schedule constraints, never QUBO minimization.

    An empty domain proves infeasibility. A search budget overflow raises before
    enumeration; it is never misreported as an infeasible instance.
    """
    if type(max_combinations) is not int or max_combinations < 1:
        raise ValueError("max_combinations must be a positive integer")
    started = perf_counter()
    combinations = prod(map(len, model.domains))
    if combinations > max_combinations:
        raise ValueError(
            f"exact search needs {combinations} combinations; limit={max_combinations}"
        )
    best = None
    feasible_count = 0
    for choice in product(*model.domains):
        bits = [0] * len(model.variables)
        for index in choice:
            bits[index] = 1
        result = evaluate(model, bits)
        if result["feasible"]:
            feasible_count += 1
            if best is None or result["objective"] < best["objective"]:
                best = result
    return {
        "status": "optimal" if best is not None else "infeasible",
        "best": best,
        "combinations": combinations,
        "feasible_count": feasible_count,
        "runtime_seconds": perf_counter() - started,
    }
