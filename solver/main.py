from fastapi import FastAPI
from pydantic import BaseModel

from model import generate_schedule

app = FastAPI(title="Shift Scheduler Solver")


class ScheduleRequest(BaseModel):
    employees: list[str]
    days: list[int]
    shifts: list[str]
    min_staff: dict[str, int]
    unavailable: list[list] = []
    max_shifts_per_week: int = 5


@app.post("/generate")
def generate(req: ScheduleRequest):
    min_staff = {
        (int(key.split("-")[0]), key.split("-")[1]): value
        for key, value in req.min_staff.items()
    }
    unavailable = [(name, int(day)) for name, day in req.unavailable]
    return generate_schedule(
        req.employees, req.days, req.shifts, min_staff,
        unavailable, req.max_shifts_per_week,
    )