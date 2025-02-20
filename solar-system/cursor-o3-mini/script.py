import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# --- Constants and Units ---
# Units: distance in AU, time in years, mass in solar masses
G = 4 * np.pi**2  # gravitational constant in these units

# --- Define Bodies in the Solar System ---
# Each body is defined by: name, mass, initial position, and initial velocity.
# For a circular orbit around the Sun (assumed at origin), if r = (a, 0) then v = (0, sqrt(G/ a))
# Masses and semi-major axes are approximate.
bodies = [
    {
        "name": "Sun",
        "mass": 1.0,
        "pos": np.array([0.0, 0.0]),
        "vel": np.array([0.0, 0.0]),
        "color": "yellow",
        "size": 20,
    },
    {
        "name": "Mercury",
        "mass": 1.65e-7,
        "pos": np.array([0.387, 0.0]),
        "vel": np.array([0.0, np.sqrt(G / 0.387)]),
        "color": "gray",
        "size": 4,
    },
    {
        "name": "Venus",
        "mass": 2.45e-6,
        "pos": np.array([0.723, 0.0]),
        "vel": np.array([0.0, np.sqrt(G / 0.723)]),
        "color": "orange",
        "size": 6,
    },
    {
        "name": "Earth",
        "mass": 3.00e-6,
        "pos": np.array([1.0, 0.0]),
        "vel": np.array([0.0, np.sqrt(G / 1.0)]),
        "color": "blue",
        "size": 6,
    },
    {
        "name": "Mars",
        "mass": 3.2e-7,
        "pos": np.array([1.524, 0.0]),
        "vel": np.array([0.0, np.sqrt(G / 1.524)]),
        "color": "red",
        "size": 5,
    },
    {
        "name": "Jupiter",
        "mass": 0.0009543,
        "pos": np.array([5.203, 0.0]),
        "vel": np.array([0.0, np.sqrt(G / 5.203)]),
        "color": "brown",
        "size": 10,
    },
    {
        "name": "Saturn",
        "mass": 0.0002857,
        "pos": np.array([9.537, 0.0]),
        "vel": np.array([0.0, np.sqrt(G / 9.537)]),
        "color": "gold",
        "size": 9,
    },
    {
        "name": "Uranus",
        "mass": 4.366e-5,
        "pos": np.array([19.191, 0.0]),
        "vel": np.array([0.0, np.sqrt(G / 19.191)]),
        "color": "lightblue",
        "size": 8,
    },
    {
        "name": "Neptune",
        "mass": 5.15e-5,
        "pos": np.array([30.07, 0.0]),
        "vel": np.array([0.0, np.sqrt(G / 30.07)]),
        "color": "purple",
        "size": 8,
    },
]

# Number of bodies
n = len(bodies)

# Create arrays for positions, velocities, and masses
positions = np.array([body["pos"] for body in bodies])  # shape (n, 2)
velocities = np.array([body["vel"] for body in bodies])  # shape (n, 2)
masses = np.array([body["mass"] for body in bodies])  # shape (n,)


def compute_accelerations(pos):
    """Compute the gravitational acceleration on each body due to every other body."""
    acc = np.zeros_like(pos)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            # Vector from body i to j
            r_ij = pos[j] - pos[i]
            distance = np.linalg.norm(r_ij)
            # Avoid singularity if distance is too small:
            if distance < 1e-5:
                continue
            acc[i] += G * masses[j] * r_ij / distance**3
    return acc


# Time parameters
dt = 0.001  # time step in years (~0.365 days)
total_time = 10  # total simulation time in years
num_steps = int(total_time / dt)
record_interval = 50  # record position every N steps for the animation

# Precompute trajectories for animation
traj = []  # will be a list of positions arrays (shape (n,2))
acc = compute_accelerations(positions)

print("Simulating dynamics... please wait.")
for step in range(num_steps):
    # Leapfrog integration (velocity Verlet)
    # Update positions
    new_positions = positions + velocities * dt + 0.5 * acc * dt**2
    # Compute new accelerations at new positions
    new_acc = compute_accelerations(new_positions)
    # Update velocities (average acceleration)
    new_velocities = velocities + 0.5 * (acc + new_acc) * dt

    # Update state
    positions = new_positions
    velocities = new_velocities
    acc = new_acc

    if step % record_interval == 0:
        traj.append(positions.copy())

print("Simulation complete.")

# --- Set Up Animation Plot ---
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_aspect("equal")
ax.set_xlim(-35, 35)
ax.set_ylim(-35, 35)
ax.set_title("Simplified Solar System Simulation")
ax.set_xlabel("AU")
ax.set_ylabel("AU")

# Plot static orbits (optional: trails from simulation)
lines = []
for body in bodies:
    (line,) = ax.plot(
        [], [], "o", color=body["color"], ms=body["size"], label=body["name"]
    )
    lines.append(line)
ax.legend(loc="upper right", fontsize="small")


def init():
    for line in lines:
        line.set_data([], [])
    return lines


def update(frame):
    pos = traj[frame]
    for i, line in enumerate(lines):
        line.set_data(pos[i, 0], pos[i, 1])
    return lines


anim = FuncAnimation(
    fig, update, frames=len(traj), init_func=init, interval=20, blit=True
)

plt.show()
