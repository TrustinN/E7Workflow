import matplotlib.pyplot as plt

# Example Data
x_vals = [
    0,
    0.02,
    0.05,
    0.08,
    0.1,
    0.15,
    0.2,
]
y_vals = [
    0.2569666667,
    0.3264333333,
    0.3552,
    0.4339666667,
    0.4725,
    0.5295,
    0.7038,
]

custom_ticks = [
    0.2914333333,
    0.3263,
    0.2968,
    0.3011666667,
    0.2668,
    0.2826,
    0.2755,
    0.2803,
]  # Custom Y-ticks
# Create the figure and axis
fig, ax = plt.subplots()

# Plot the data
ax.plot(x_vals, y_vals, marker="o", linestyle="-", color="b", label="Data Points")

# Set logarithmic scale for Y-axis
ax.set_yscale("log")

# Customize Y-axis ticks
ax.set_yticks(custom_ticks)  # Explicitly set custom ticks
ax.get_yaxis().set_major_formatter(
    plt.FuncFormatter(lambda x, _: f"{x:.3f}")
)  # High precision

# Adjust tick label formatting to prevent overlap
ax.tick_params(axis="y", labelsize=10)  # Reduce label font size
for label in ax.get_yticklabels():
    label.set_rotation(45)  # Rotate labels by 45 degrees

# Add labels, title, and legend
ax.set_xlabel("X Values")
ax.set_ylabel("Y Values (Log Scale)")
ax.set_title("Logarithmic Y-axis with Non-Overlapping Custom Ticks")
ax.legend()

# Add grid for better readability
ax.grid(True, which="both", linestyle="--", alpha=0.7)

# Adjust layout to prevent clipping
plt.tight_layout()

# Show the plot
plt.show()
