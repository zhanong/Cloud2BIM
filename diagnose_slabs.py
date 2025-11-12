# Diagnostic script to understand slab detection
import numpy as np
import matplotlib.pyplot as plt
from aux_functions import *

# Load config
config = load_config_and_variables()
xyz_filenames = config["xyz_filenames"]
bfs_thickness = config["bfs_thickness"]
tfs_thickness = config["tfs_thickness"]

# Load point cloud
print("Loading point cloud...")
points_xyz, points_rgb = np.empty((0, 3)), np.empty((0, 3))
for xyz_filename in xyz_filenames:
    points_xyz_temp, points_rgb_temp = load_xyz_file(xyz_filename, plot_xyz=False,
                                                     select_ith_lines=False)
    points_xyz = np.vstack((points_xyz, np.array(points_xyz_temp)))

print(f"\n=== Point Cloud Statistics ===")
print(f"Total points: {len(points_xyz):,}")
print(f"X range: {points_xyz[:, 0].min():.3f} to {points_xyz[:, 0].max():.3f} ({points_xyz[:, 0].max() - points_xyz[:, 0].min():.3f} m)")
print(f"Y range: {points_xyz[:, 1].min():.3f} to {points_xyz[:, 1].max():.3f} ({points_xyz[:, 1].max() - points_xyz[:, 1].min():.3f} m)")
print(f"Z range: {points_xyz[:, 2].min():.3f} to {points_xyz[:, 2].max():.3f} ({points_xyz[:, 2].max() - points_xyz[:, 2].min():.3f} m)")

# Create Z histogram
print("\n=== Z-coordinate Distribution (Histogram) ===")
z_step = 0.15
z_min, z_max = points_xyz[:, 2].min(), points_xyz[:, 2].max()
n_steps = int((z_max - z_min) / z_step + 1)
z_array, n_points_array = [], []

for i in range(n_steps):
    z = z_min + i * z_step
    idx_selected = np.where((z < points_xyz[:, 2]) & (points_xyz[:, 2] < (z + z_step)))[0]
    z_array.append(z)
    n_points_array.append(len(idx_selected))

# Plot
plt.figure(figsize=(12, 6))
plt.plot(np.array(n_points_array) / 1000, z_array, '-b', linewidth=1.0)
plt.xlabel('Number of points (×10³)')
plt.ylabel('Height/z-coordinate (m)')
plt.title('Point Distribution along Z-axis\n(Peaks indicate potential floor/ceiling slabs)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('z_distribution.png', dpi=150)
print("Saved histogram to: z_distribution.png")
plt.show()

# Find peaks (potential slabs)
max_n_points = max(n_points_array)
threshold = 0.6 * max_n_points
print(f"\nPeak detection threshold: {threshold/1000:.1f}k points")
print(f"Maximum points at any Z-level: {max_n_points/1000:.1f}k points")

print("\n=== Potential slab Z-coordinates (above threshold) ===")
for i, (z, n_pts) in enumerate(zip(z_array, n_points_array)):
    if n_pts > threshold:
        print(f"Z = {z:.3f} m: {n_pts/1000:.1f}k points")
