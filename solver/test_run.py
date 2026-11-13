from model import generate_schedule

employees = ["Ana", "Luis", "Marta", "Pedro", "Sofia", "Juan"]
days = list(range(7))
shifts = ["morning", "afternoon", "night"]
min_staff = {(d, s): 1 for d in days for s in shifts}
unavailable = [("Ana", 5), ("Ana", 6), ("Luis", 0)]

result = generate_schedule(employees, days, shifts, min_staff, unavailable)
print(result["ok"], result.get("solve_time_s"))

for row in sorted(result.get("schedule", []), key=lambda r: (r["day"], r["shift"])):
    print(row)