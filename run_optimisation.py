
from generate_data import generate_demand
from optimiser import optimise_shifts
from evaluate import evaluate_schedule
from visualise import (plot_staffing_coverage, plot_overstaffing)


def main():
    # Generate demand
    demand_data = generate_demand(days=1)
    demand = demand_data["required_workers"].tolist()

    # Optimisation of schedule
    schedule = optimise_shifts(demand)

    if schedule is None:
        print("No feasible schedule found.")
        return

    print("\n--- Schedule Found ---")
    for shift in schedule:
        print(
            f"{shift['name']:10} "
            f"start={shift['shift_start']} "
            f"length={shift['shift_length']} hours "
            f"break={shift['break_start']} "
            f"employees={shift['employees']}"
        )

    # Evaluation
    results, summary = evaluate_schedule(
        schedule=schedule,
        demand=demand,
        slot_minutes=30,
        wage_per_hour=14,
    )

    print("\n--- Evaluation Summary ---")
    for metric, value in summary.items():
        print(f"{metric}: {value}")

    print("\n--- Evaluation Results (first 12 slots) ---")
    print(results.head(12).to_string(index=False))

    # Visualisation Charts
    plot_staffing_coverage(results)
    plot_overstaffing(results)


if __name__ == "__main__":
    main()

