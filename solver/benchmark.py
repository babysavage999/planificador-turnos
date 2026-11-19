import random
import sys
import time
from pathlib import Path

from model import generate_schedule

SIZES = [10, 30, 100, 300, 500]
# employees per required slot: lower divisor = more staff needed per shift
SCENARIOS = {"relaxed": 6, "tight": 5}
RUNS_PER_SIZE = 3
TIME_LIMIT_S = 10
DAYS = list(range(7))
SHIFTS = ["morning", "afternoon", "night"]


def build_scenario(n_employees, divisor, seed=42):
    rng = random.Random(seed)
    employees = [f"Employee {i + 1}" for i in range(n_employees)]

    staff_per_shift = max(1, n_employees // divisor)
    min_staff = {(d, s): staff_per_shift for d in DAYS for s in SHIFTS}

    # Each employee is unavailable on one random day
    unavailable = [(e, rng.choice(DAYS)) for e in employees]

    return employees, min_staff, unavailable, staff_per_shift


def run_benchmark():
    rows = []
    for scenario, divisor in SCENARIOS.items():
        for n in SIZES:
            employees, min_staff, unavailable, per_shift = build_scenario(n, divisor)
            times = []
            last_result = None

            for _ in range(RUNS_PER_SIZE):
                start = time.perf_counter()
                last_result = generate_schedule(
                    employees, DAYS, SHIFTS, min_staff, unavailable,
                    time_limit=TIME_LIMIT_S,
                )
                times.append(time.perf_counter() - start)

            avg = sum(times) / len(times)
            rows.append({
                "scenario": scenario,
                "employees": n,
                "per_shift": per_shift,
                "ok": last_result["ok"],
                "avg_s": avg,
                "min_s": min(times),
                "max_s": max(times),
                "assignments": len(last_result.get("schedule", [])),
                "load_gap": last_result.get("load_gap", "-"),
            })
            print(f"[{scenario}] {n} employees -> {avg:.3f}s average, "
                  f"feasible: {last_result['ok']}")

    return rows


def to_markdown(rows, title):
    lines = [
        f"## {title}",
        "",
        f"Each case was run {RUNS_PER_SIZE} times (time limit {TIME_LIMIT_S}s per run).",
        "",
        "| Scenario | Employees | Staff per shift | Feasible | Avg (s) | Min (s) | Max (s) | Assignments | Load gap |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['scenario']} | {r['employees']} | {r['per_shift']} | {r['ok']} | "
            f"{r['avg_s']:.3f} | {r['min_s']:.3f} | {r['max_s']:.3f} | "
            f"{r['assignments']} | {r['load_gap']} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    label = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    results = run_benchmark()
    output = Path(__file__).resolve().parent.parent / "docs" / f"benchmark_{label}.md"
    output.parent.mkdir(exist_ok=True)
    output.write_text(to_markdown(results, f"Benchmark: {label}"), encoding="utf-8")
    print(f"\nResults saved to {output}")