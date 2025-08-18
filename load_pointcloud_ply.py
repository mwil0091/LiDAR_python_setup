import open3d as o3d
import numpy as np
import time
# Read in the PLY file
pcd = o3d.io.read_point_cloud("output_new2.ply")
print(pcd)
print(pcd.scale)
print(type(pcd))

pcd1 = o3d.io.read_point_cloud("output_1600.ply")
pcd2 = o3d.io.read_point_cloud("output_1630.ply")

cur_time = time.time()
# Compute distance from pcd1 to pcd2
distances = pcd1.compute_point_cloud_distance(pcd2)
distances = np.asarray(distances)

print("Average distance between point clouds:", np.mean(distances))
print("Max distance:", np.max(distances))
print("Min distance:", np.min(distances))
print("Time (sec)", time.time() - cur_time)
# Open an interactive visualization window
o3d.visualization.draw_geometries(
    [pcd],
    window_name='Open3D Point Cloud Viewer',
    width=800,
    height=600,
    left=50,
    top=50,
    point_show_normal=False
)

