import numpy as np
import pandas as pd

ORDERS_PER_WORKER_PER_SLOT = 5
SLOT_MINUTES = 30  # Duration of 1 time slot
SLOTS_PER_DAY = 24 * 60 // SLOT_MINUTES

def generate_demand(days=7, seed=67):
    rng = np.random.default_rng(seed)
    rows = []

    for day in range(days):
        for slot in range(SLOTS_PER_DAY):
            hour = slot * SLOT_MINUTES // 60

            # num orders based on time of day
            if 9 <= hour < 17:
                mean_orders_per_hour = 240
            elif 17 <= hour < 21:
                mean_orders_per_hour = 180
            else:
                mean_orders_per_hour = 120

            daily_factor = [0.85, 0.9, 1.0, 1.05, 1.15, 1.2, 0.8]

            # get binomial distribution value
            orders = rng.poisson( mean_orders_per_hour * (SLOT_MINUTES / 60) * daily_factor[day % 7] )

            # print(day, mean_orders_per_hour * (SLOT_MINUTES * 60) * daily_factor[day % 7], orders)

            workers = np.ceil(orders / ORDERS_PER_WORKER_PER_SLOT)

            rows.append({
                "day": day,
                "slots": slot,
                "hour": hour,
                "orders": orders,
                "required_workers": int(workers),
            })

    return pd.DataFrame(rows)


# If run directly (not module import)
if __name__ == "__main__":
    demand = generate_demand()
    demand.to_csv("demand.csv", index=False)
    print(demand.head(10))
