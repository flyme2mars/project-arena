import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.patches import Rectangle  # Correct import for Rectangle

# Constants
g = 3.71  # Martian gravity (m/s^2)
rho0 = 0.02  # Surface atmospheric density (kg/m^3)
H = 11000  # Scale height (m)
m = 120000  # Mass (kg)
C_d = 1.0  # Drag coefficient (simplified)
A_vertical = 63.6  # Area (m^2) when vertical
A_horizontal = 450  # Area (m^2) when horizontal
T = 6000000  # Thrust from 3 Raptor engines (N)
h0 = 100000  # Initial altitude (m)
v0 = -7500  # Initial velocity (m/s, downward)
dt = 0.01  # Time step (s, reduced for accuracy)

# Initialize lists to store simulation data
t_list = [0.0]
h_list = [float(h0)]
v_list = [float(v0)]
orientation_list = [0]  # 0: vertical, 1: horizontal
thrust_list = [0]  # 0: off, 1: on

# Simulation loop with improved transition logic
while h_list[-1] > 0:
    t = t_list[-1]
    h = h_list[-1]
    v = v_list[-1]
    orientation = orientation_list[-1]
    thrust = thrust_list[-1]

    # Atmospheric density at current altitude
    rho = rho0 * np.exp(-h / H)

    # Determine drag area based on current orientation
    A = A_vertical if orientation == 0 else A_horizontal

    # Calculate accelerations
    a_d = -0.5 * rho * v * abs(v) * C_d * A / m  # Drag opposes velocity
    a_t = T / m if thrust == 1 else 0  # Thrust (upward)
    a = a_t + a_d - g  # Net acceleration (gravity downward)

    # Update velocity and altitude using Euler method
    v_new = v + a * dt
    h_new = h + v * dt + 0.5 * a * dt * dt

    # Phase transitions
    if (
        orientation == 0 and thrust == 0 and h < 50000
    ):  # Transition to Belly Flop at ~50 km
        orientation_new = 1
        thrust_new = 0
    elif orientation == 1 and h < 1000:  # Transition to Landing at 1 km
        orientation_new = 0
        thrust_new = 1
    else:
        orientation_new = orientation
        thrust_new = thrust

    # Append new values
    t_list.append(t + dt)
    h_list.append(max(h_new, 0))  # Prevent negative altitude
    v_list.append(v_new)
    orientation_list.append(orientation_new)
    thrust_list.append(thrust_new)

    # Log state near key points
    if 12.5 <= t <= 13.5 or h_new < 1000:
        print(
            f"t={t:.2f}s, h={h:.1f}m, v={v:.1f}m/s, orientation={orientation}, thrust={thrust}"
        )

# Convert lists to arrays for animation
t_array = np.array(t_list)
h_array = np.array(h_list)
orientation_array = np.array(orientation_list)
thrust_array = np.array(thrust_list)

# Set up the figure for animation
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_xlim(-50, 50)
ax.set_ylim(0, 2000)
ax.set_xlabel("Horizontal Distance (m)")
ax.set_ylabel("Altitude (m)")
ax.set_title("Starship Mars Landing Animation")


# Animation function
def animate(i):
    ax.clear()
    h = h_array[i]
    orientation = orientation_array[i]
    thrust = thrust_array[i]

    # Dynamic Y-axis adjustment
    if h > 1000:
        ax.set_ylim(h - 1000, h + 1000)
    else:
        ax.set_ylim(0, 2000)

    # Draw Martian surface
    ax.axhline(0, color="red", linewidth=2, label="Mars Surface")

    # Draw Starship based on orientation
    if orientation == 0:  # Vertical
        rect = Rectangle((-4.5, h - 25), 9, 50, color="blue", label="Starship")
    else:  # Horizontal (Belly Flop)
        rect = Rectangle((-25, h - 4.5), 50, 9, color="blue", label="Starship")
    ax.add_patch(rect)

    # Draw thrust if engines are on
    if thrust == 1 and orientation == 0:
        for dy in [0, 10, 20]:
            ax.plot([-2, 2], [h - 25 - dy, h - 25 - dy], color="orange", linewidth=2)
        ax.text(0, h - 35, "Thrust", color="orange", ha="center")

    # Set limits and labels
    ax.set_xlim(-50, 50)
    ax.set_xlabel("Horizontal Distance (m)")
    ax.set_ylabel("Altitude (m)")
    ax.set_title(f"Time: {t_array[i]:.1f} s, Altitude: {h:.1f} m")

    return [rect]  # Return the rectangle patch for animation updates


# Create animation
ani = animation.FuncAnimation(
    fig, animate, frames=len(t_array), interval=50, repeat=False
)

plt.show()
