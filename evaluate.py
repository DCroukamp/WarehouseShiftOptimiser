
import pandas as pd

SLOT_MINUTES = 30


def time_to_slot(time_string, slot_minutes=SLOT_MINUTES):
    #Convert time to slot number
    hours, minutes = map(int, time_string.split(":"))
    total_minutes = hours * 60 + minutes

    if total_minutes % slot_minutes != 0:
        raise ValueError(
            f"{time_string} does not align with {slot_minutes}-minute slots"
        )

    return (total_minutes // slot_minutes) % (24 * 60 // slot_minutes)


def evaluate_schedule(schedule,
                      demand,
                      slot_minutes=SLOT_MINUTES,
                      wage_per_hour=14,
):
    day_slots = 24 * 60 // slot_minutes

    if len(demand) != day_slots:
        raise ValueError(f"Expected {day_slots} demand values, got {len(demand)}")

    if any(value < 0 for value in demand):
        raise ValueError("Demand cannot be negative")

    coverage = [0] * day_slots
    total_employees = 0
    total_cost = 0.0

    for pattern in schedule:
        employees = pattern["employees"]
        shift_start = time_to_slot(pattern["shift_start"], slot_minutes)
        shift_slots = pattern["shift_slots"]
        break_start = time_to_slot(pattern["break_start"], slot_minutes)
        break_slots = pattern["break_length"] // slot_minutes

        if employees < 0:
            raise ValueError("Employee count cannot be negative")

        if pattern["break_length"] % slot_minutes != 0:
            raise ValueError("Break length must align with time slots")

        # Employees not on break
        for offset in range(shift_slots):
            slot = (shift_start + offset) % day_slots
            slots_since_break_start = (slot - break_start) % day_slots

            on_break = slots_since_break_start < break_slots

            if not on_break:
                coverage[slot] += employees

        shift_hours = pattern["shift_length"]
        break_hours = pattern["break_length"] / 60

        paid_hours =  shift_hours - break_hours

        total_employees += employees
        total_cost += employees * paid_hours * wage_per_hour

    results = pd.DataFrame({
        "slot": range(day_slots),
        "time": [
            f"{(i * slot_minutes) // 60:02d}:"
            f"{(i * slot_minutes) % 60:02d}"
            for i in range(day_slots)
        ],
        "demand": demand,
        "coverage": coverage,
    })



    results["overstaffing"] = (
        results["coverage"] - results["demand"]
    ).clip(lower=0)

    # Not needed for now as understaffing is not permitted!
    results["shortage"] = (
        results["demand"] - results["coverage"]
    ).clip(lower=0)

    summary = {
        "employees_scheduled": total_employees,
        "total_labour_cost": round( total_cost, 2 ),
        "slots_with_shortage": int( (results["shortage"] > 0).sum() ),
        "maximum_shortage": int( results["shortage"].max() ),
        "total_shortage_employee_slots": int( results["shortage"].sum() ),
        "slots_with_overstaffing": int( (results["overstaffing"] > 0).sum() ),
    }

    return results, summary
