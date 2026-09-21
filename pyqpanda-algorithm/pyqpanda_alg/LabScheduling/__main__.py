"""Run with python -m pyqpanda_alg.LabScheduling INPUT.json."""

import argparse
import json
from pathlib import Path

from .report import run_experiment


def main(argv: list[str] | None = None) -> int:
    """Print JSON; exit 2 for input errors, 3 for infeasibility, 4 for a miss."""
    parser = argparse.ArgumentParser(description="共享实验室 QUBO 最小扰动重排（CPU）")
    parser.add_argument("input", type=Path)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--layers", type=int, default=1)
    parser.add_argument("--shots", type=int, default=512)
    parser.add_argument("--maxiter", type=int, default=60)
    parser.add_argument("--restarts", type=int, default=2)
    parser.add_argument("--mixer", choices=("xy", "x"), default="xy")
    parser.add_argument(
        "--reduce", action="store_true", help="exact propagation and component solving"
    )
    parser.add_argument("--output", type=Path, help="also save the JSON report here")
    args = parser.parse_args(argv)
    try:
        report = run_experiment(
            args.input,
            args.seed,
            args.layers,
            args.shots,
            args.maxiter,
            args.restarts,
            args.mixer,
            reduce=args.reduce,
        )
        text = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text + "\n", encoding="utf-8")
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(text)
    return {
        "feasible": 0,
        "infeasible": 3,
        "no_feasible_sample": 4,
        "resource_limit": 5,
    }[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
