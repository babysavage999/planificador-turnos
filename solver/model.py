from ortools.sat.python import cp_model


def generate_schedule(employees, days, shifts, min_staff, unavailable,
                      max_shifts_per_week=5, time_limit=10):
    model = cp_model.CpModel()

    # x[e, d, s] = 1 if employee e works on day d during shift s
    x = {
        (e, d, s): model.NewBoolVar(f"x_{e}_{d}_{s}")
        for e in employees for d in days for s in shifts
    }

    # 1. Minimum staff required per shift
    for d in days:
        for s in shifts:
            model.Add(sum(x[e, d, s] for e in employees) >= min_staff[(d, s)])

    # 2. At most one shift per day for each employee
    for e in employees:
        for d in days:
            model.Add(sum(x[e, d, s] for s in shifts) <= 1)

    # 3. Respect days when an employee is unavailable
    for (e, d) in unavailable:
        for s in shifts:
            model.Add(x[e, d, s] == 0)

    # 4. Weekly limit of shifts per employee
    for e in employees:
        model.Add(
            sum(x[e, d, s] for d in days for s in shifts) <= max_shifts_per_week
        )

    # 5. Rest rule: no night shift followed by a morning shift the next day
    for e in employees:
        for d in days[:-1]:
            model.Add(x[e, d, "night"] + x[e, d + 1, "morning"] <= 1)

    # Objective: balance the workload across employees
    total_slots = len(days) * len(shifts)
    max_load = model.NewIntVar(0, total_slots, "max_load")
    min_load = model.NewIntVar(0, total_slots, "min_load")
    for e in employees:
        load = sum(x[e, d, s] for d in days for s in shifts)
        model.Add(load <= max_load)
        model.Add(load >= min_load)
    total_assigned = sum(x.values())
    model.Minimize(100 * total_assigned + (max_load - min_load))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"ok": False, "message": "No feasible schedule with these constraints"}

    schedule = [
        {"employee": e, "day": d, "shift": s}
        for (e, d, s), var in x.items() if solver.Value(var)
    ]
    return {
        "ok": True,
        "schedule": schedule,
        "load_gap": solver.Value(max_load) - solver.Value(min_load),
        "solve_time_s": solver.WallTime(),
    }