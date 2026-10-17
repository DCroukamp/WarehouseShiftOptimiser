from ortools.sat.python import cp_model

from generate_data import generate_demand

POSSIBLE_SHIFTS = [
    {"name": "midnight", "start": 0, "length": 8},
    {"name": "midnight", "start": 0, "length": 6},
    {"name": "early", "start": 4, "length": 8},
    {"name": "early", "start": 4, "length": 6},
    {"name": "day", "start": 8, "length": 8},
    {"name": "day", "start": 8, "length": 6},
    {"name": "afternoon", "start": 12, "length": 8},
    {"name": "afternoon", "start": 12, "length": 6},
    {"name": "night", "start": 16, "length": 8},
    {"name": "night", "start": 16, "length": 6},
]

SLOT_MINUTES = 30  # Duration of 1 time slot
BREAK_SLOTS = 1
SLOTS_PER_DAY = 24 * 60 // SLOT_MINUTES
MAX_EMPLOYEES = 60
HOURLY_WAGE = 14


def possible_break_patterns(
        shift_start,
        shift_length_hours=8,
        slot_minutes=SLOT_MINUTES,
        break_length_slots=BREAK_SLOTS,
        min_slots_before_break=4,
        min_slots_after_break=2,
):
    shift_slots = shift_length_hours * 60 // slot_minutes
    patterns = []

    first_break_start = min_slots_before_break
    last_break_start = (shift_slots - break_length_slots - min_slots_after_break)

    for break_start in range(first_break_start, last_break_start + 1):
        patterns.append({
            "shift_start": shift_start,
            "shift_slots": shift_slots,
            "break_start": break_start,
            "break_length_slots": break_length_slots,
            "shift_length_hours": shift_length_hours,
        })

    return patterns


# Get time slots which are not a break
def get_active_slots(break_pattern):
    start_slot = break_pattern["shift_start"] * 60 // SLOT_MINUTES
    shift_slots = break_pattern["shift_slots"]
    break_start = break_pattern["break_start"]
    break_length = break_pattern["break_length_slots"]

    active_slots = set()

    for index in range(shift_slots):
        on_break = break_start <= index < break_start + break_length
        if not on_break:
            active_slots.add((start_slot + index) % SLOTS_PER_DAY)

    return active_slots


def get_all_patterns():
    all_patterns = []
    for possible_shift in POSSIBLE_SHIFTS:
        break_patterns = possible_break_patterns(possible_shift["start"], possible_shift["length"], SLOT_MINUTES,
                                                 BREAK_SLOTS)

        for break_pattern in break_patterns:
            break_pattern["name"] = possible_shift["name"]
            break_pattern["active_slots"] = get_active_slots(break_pattern)
            all_patterns.append(break_pattern)
    return all_patterns


def optimise_shifts(demand, max_employees=MAX_EMPLOYEES):
    model = cp_model.CpModel()  # Constraint Programming model
    all_patterns = get_all_patterns()

    num_employees = {
        p: model.new_int_var(0, max_employees, "pattern_" + str(p))
        for p in range(len(all_patterns))
    }

    # Cannot have more than the maximum available employees per day
    model.add(sum(num_employees.values()) <= max_employees)

    # checking demand is met for each time slot
    for t in range(SLOTS_PER_DAY):
        active_workers = sum(num_employees[p]
                             for p, pattern in enumerate(all_patterns)
                             if t in pattern["active_slots"]
                             )
        model.add(active_workers >= int(demand[t]))

    cost_per_slot_pence = round((HOURLY_WAGE * 100) * (SLOT_MINUTES / 60))

    # Minimise cost
    model.minimize(
        sum(
            num_employees[p] * (
                    all_patterns[p]["shift_slots"] - all_patterns[p]["break_length_slots"]) * cost_per_slot_pence
            for p in range(len(all_patterns))
        )
    )

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60

    status = solver.Solve(model)

    if status != cp_model.OPTIMAL and status != cp_model.FEASIBLE:
        print("No feasible solution found")
        print("Status:", solver.status_name(status))
        return None

    print("Solver status:", solver.status_name(status))

    # Extracting solution
    schedule = []
    total_employees = 0
    for p, pattern in enumerate(all_patterns):

        count = solver.value(num_employees[p])

        if count == 0:
            continue

        total_employees += count

        start_minutes = pattern["shift_start"] * 60
        break_minutes = start_minutes + pattern["break_start"] * SLOT_MINUTES

        schedule.append({
            # f"{pattern['name']:10} "
            # f"employees={count:2} "
            # f"shift_start={start_minutes // 60:02}:{start_minutes % 60:02} "
            # f"break_start={break_minutes // 60:02}:{break_minutes % 60:02}"
            # f"shift_length={pattern['shift_length_hours']:2} "

            "name": pattern["name"],
            "shift_start": f"{start_minutes // 60:02}:{start_minutes % 60:02}",
            "shift_slots": pattern["shift_slots"],
            "shift_length": pattern["shift_length_hours"],
            "break_start": f"{break_minutes // 60:02}:{break_minutes % 60:02}",
            "break_length": pattern["break_length_slots"] * SLOT_MINUTES,
            "employees": count,
        })

    print("Total employees assigned:", total_employees)
    print(f"Labour cost: £{solver.objective_value / 100:.2f}")

    return schedule


if __name__ == "__main__":
    # print("Active Shifts:")
    # for index, shift in enumerate(get_active_shifts()):
    #     print(index, shift)
    #
    # print("Breaks:")
    # for possible_break_patterns in possible_break_patterns(5):
    #     print(possible_break_patterns)

    demand_data = generate_demand(days=1)
    demand = demand_data["required_workers"].tolist()

    # print("Number of slots:", len(demand))
    # print("Maximum workers required:", max(demand))
    # print("Demand:", demand)

    optimise_shifts(demand)
