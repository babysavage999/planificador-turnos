import time

from benchmark import DAYS, SHIFTS, SCENARIOS, build_scenario
from model import generate_schedule

for scenario, divisor in SCENARIOS.items():
    employees, min_staff, unavailable, _ = build_scenario(500, divisor)

    start = time.perf_counter()
    result = generate_schedule(
        employees, DAYS, SHIFTS, min_staff, unavailable, time_limit=10
    )
    total = time.perf_counter() - start

    print(
        f"[{scenario}] total {total:.2f}s | solver {result['solve_time_s']:.2f}s | "
        f"status {result['status']} | load gap {result['load_gap']}"
    )