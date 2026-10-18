import matplotlib.pyplot as plt


def plot_staffing_coverage(results):
    #Compare required with actual staffing

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.step(
        results["time"],
        results["demand"],
        where="post", #Shows after point plot
        label="Required workers",
    )

    ax.step(
        results["time"],
        results["coverage"],
        where="post",
        label="Actual active workers",
    )


    ax.set_title("Staffing Demand vs Coverage")
    ax.set_xlabel("Time of day")
    ax.set_ylabel("Number of workers")
    ax.legend()
    ax.grid(True)

    tick_step = max(1, len(results) // 12) # every 2 hours
    ticks = list(range(0, len(results), tick_step))

    ax.set_xticks(ticks)
    ax.set_xticklabels(
        results["time"].iloc[ticks],
        rotation=45,
        ha="right",
    )

    fig.savefig(
        "images/staffing_coverage.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()



def plot_overstaffing(results):
    # Overstaffed Times

    fig, ax = plt.subplots(figsize=(14, 5))

    ax.bar(
        results["time"],
        results["overstaffing"],
        label="Overstaffing",
    )

    ax.set_title("Shift Overstaffing")
    ax.set_xlabel("Time of day")
    ax.set_ylabel("Number of workers above demand")
    ax.grid(axis="y", alpha=0.3)

    tick_step = max(1, len(results) // 12)
    ticks = list(range(0, len(results), tick_step))

    ax.set_xticks(ticks)
    ax.set_xticklabels(
        results["time"].iloc[ticks],
        rotation=45,
        ha="right",
    )

    fig.savefig(
        "images/shift_overstaffing.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
