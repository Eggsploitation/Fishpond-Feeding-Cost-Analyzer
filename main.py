"""Fishpond Feeding Cost Analyzer

Estimates fish biomass, daily feed requirements, total feed consumption,
and feeding cost over a fishpond culture period.
"""

import numpy as np
import matplotlib.pyplot as plt


def get_positive_number(prompt):
    """Ask until the user enters a valid number greater than zero."""
    while True:
        try:
            value = float(input(prompt))

            if np.isfinite(value) and value > 0:
                return value

            print("Please enter a finite number greater than zero.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_positive_integer(prompt):
    """Ask until the user enters a whole number greater than zero."""
    while True:
        try:
            value = int(input(prompt))

            if value > 0:
                return value

            print("Please enter a whole number greater than zero.")
        except ValueError:
            print("Invalid input. Please enter a whole number.")


def calculate_biomass(number_of_fish, average_weight):
    """Calculate total fish biomass in kilograms."""
    return number_of_fish * average_weight / 1000


def calculate_daily_feed(biomass, feeding_rate):
    """Calculate daily feed requirement in kilograms."""
    return biomass * (feeding_rate / 100)

def calculate_fish_weight(initial_weight, daily_growth, day):
    """Estimate fish weight using an illustrative nonlinear growth model."""
    growth_acceleration = daily_growth * 0.1
    return (
        initial_weight
        + daily_growth * day
        + growth_acceleration * day**2
    )


def gaussian_quadrature(function, start, end):
    """Approximate a definite integral with two-point Gauss-Legendre quadrature."""
    # Nodes and weights for two-point Gauss-Legendre quadrature on [-1, 1].
    node1 = -1 / np.sqrt(3)
    node2 = 1 / np.sqrt(3)
    weight1 = 1
    weight2 = 1

    # Transform the nodes from [-1, 1] to the interval [start, end].
    midpoint = (start + end) / 2
    half_width = (end - start) / 2
    point1 = midpoint + half_width * node1
    point2 = midpoint + half_width * node2

    return half_width * (
        weight1 * function(point1)
        + weight2 * function(point2)
    )


def main():
    """Collect inputs, calculate estimates, display results, and plot graphs."""
    print("=" * 40)
    print("FISHPOND FEEDING COST ANALYZER")
    print("=" * 40)

    # Collect the fishpond information from the user.
    number_of_fish = get_positive_integer("Number of fish stocked: ")
    initial_weight = get_positive_number(
        "Initial average fish weight (grams): "
    )
    daily_growth = get_positive_number(
        "Assumed daily weight gain per fish (grams): "
    )
    feeding_rate = get_positive_number("Daily feeding rate (%): ")
    culture_days = get_positive_integer("Culture period (days): ")
    feed_price = get_positive_number("Feed price per kilogram (PHP): ")

    # Calculate the starting biomass and daily feed requirement.
    initial_biomass = calculate_biomass(number_of_fish, initial_weight)
    initial_daily_feed = calculate_daily_feed(initial_biomass, feeding_rate)

    # Estimate the fish weight and biomass at the end of the culture period.
    final_weight = calculate_fish_weight(
    initial_weight, daily_growth, culture_days
)
    final_biomass = calculate_biomass(number_of_fish, final_weight)
    final_daily_feed = calculate_daily_feed(final_biomass, feeding_rate)

    # Create NumPy arrays for each day, including day zero.
    days = np.arange(culture_days + 1)
    weights = calculate_fish_weight(
    initial_weight, daily_growth, days
)
    biomass_values = number_of_fish * weights / 1000
    feed_values = biomass_values * (feeding_rate / 100)

    # Define daily feed as a function of time for Gaussian quadrature.
    def feed_function(day):
        fish_weight = calculate_fish_weight(
            initial_weight, daily_growth, day
        )
        biomass = number_of_fish * fish_weight / 1000
        return biomass * (feeding_rate / 100)

    # Method 1: estimate total feed using the trapezoidal rule.
    trapezoidal_feed = np.trapezoid(feed_values, days)

    # Method 2: estimate the same total using Gaussian quadrature.
    gaussian_feed = gaussian_quadrature(feed_function, 0, culture_days)

    # Calculate costs and the absolute difference between the feed estimates.
    trapezoidal_cost = trapezoidal_feed * feed_price
    gaussian_cost = gaussian_feed * feed_price
    difference = abs(trapezoidal_feed - gaussian_feed)
    cost_difference = abs(trapezoidal_cost - gaussian_cost)

    # Display the calculation results.
    print("\n" + "=" * 40)
    print("FEEDING COST SUMMARY")
    print("=" * 40)
    print(f"Initial biomass: {initial_biomass:.2f} kg")
    print(f"Final biomass: {final_biomass:.2f} kg")
    print(f"Initial daily feed: {initial_daily_feed:.2f} kg")
    print(f"Final daily feed: {final_daily_feed:.2f} kg")
    print(f"Trapezoidal total feed: {trapezoidal_feed:.3f} kg")
    print(f"Gaussian total feed: {gaussian_feed:.3f} kg")
    print(f"Trapezoidal feed cost: PHP {trapezoidal_cost:,.3f}")
    print(f"Gaussian feed cost: PHP {gaussian_cost:,.3f}")
    print(f"Difference between methods: {difference:.6f} kg")
    print(f"Difference in estimated cost: PHP {cost_difference:,.3f}")

    # Explain the result in simple terms.
    print("\n" + "=" * 40)
    print("INTERPRETATION")
    print("=" * 40)
    print(f"Estimated total feed needed: {trapezoidal_feed:.3f} kg")
    print(f"Estimated total feeding cost: PHP {trapezoidal_cost:,.3f}")

    if difference < 0.01:
        print(
            "Both numerical integration methods "
            "produced nearly identical results."
        )
    else:
        print("The two methods produced different estimates.")

    print(
        "Note: Results are estimates based on the "
        "assumed daily fish growth and feeding rate."
    )

    # Estimate cumulative cost for each day using the trapezoidal rule.
    daily_cost_values = feed_values * feed_price
    cumulative_cost_values = np.zeros(len(days))

    for i in range(1, len(days)):
        cumulative_cost_values[i] = np.trapezoid(
            daily_cost_values[: i + 1], days[: i + 1]
        )

    # Create three graphs in one window.
    _, axes = plt.subplots(3, 1, figsize=(9, 12))

    # Graph 1: fish biomass over time.
    axes[0].plot(
        days, biomass_values, label="Fish Biomass", marker="o", markersize=3
    )
    axes[0].set_title("Estimated Fish Biomass Over Time")
    axes[0].set_xlabel("Culture Period (Days)")
    axes[0].set_ylabel("Biomass (kg)")
    axes[0].legend()
    axes[0].grid(True)

    # Graph 2: daily feed requirement over time.
    axes[1].plot(
        days, feed_values,
        label="Daily Feed Requirement", marker="o", markersize=3
    )
    axes[1].set_title("Estimated Daily Feed Requirement")
    axes[1].set_xlabel("Culture Period (Days)")
    axes[1].set_ylabel("Feed (kg/day)")
    axes[1].legend()
    axes[1].grid(True)

    # Graph 3: cumulative feeding cost over time.
    axes[2].plot(
        days, cumulative_cost_values,
        label="Cumulative Feeding Cost", marker="o", markersize=3
    )
    axes[2].set_title("Estimated Cumulative Feeding Cost")
    axes[2].set_xlabel("Culture Period (Days)")
    axes[2].set_ylabel("Cost (PHP)")
    axes[2].legend()
    axes[2].grid(True) 

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Repeat the analysis until the user chooses to exit.
    while True:
        main()
        choice = input(
            "\nWould you like to analyze another fishpond? (yes/no): "
        ).strip().lower()

        if choice not in ("yes", "y"):
            print("Thank you for using Fishpond Feeding Cost Analyzer!")
            break
