# ROS 2 Obstacle Avoidance Bot

ROS 2 package that spawns a simple mobile robot in Gazebo (Ignition/GZ) and runs a
3‑phase LiDAR‑based obstacle avoidance controller.

## Features
- Gazebo world, robot model, meshes, and URDF for visualization.
- `obstacle_avoidance` ROS 2 node publishing velocity commands based on `/scan`.
- ROS ↔ Gazebo bridges for `/cmd_vel`, `/odom`, `/scan`, `/tf`, and `/clock`.

## Repository layout
- `src/robot/robot/obstacle_avoidance.py` — avoidance node implementation.
- `src/robot/launch/sim.launch.py` — Gazebo simulation launch file.
- `src/robot/{models,meshes,urdf,worlds}` — simulation assets.

## Prerequisites
- ROS 2 installation (e.g., Humble, Iron, or newer)
- `colcon` build tools
- Gazebo (Ignition/GZ) and ROS ↔ GZ bridge packages:
  - `ros_gz_sim`, `ros_gz_bridge`
  - `robot_state_publisher`, `joint_state_publisher`
  - `slam_toolbox` (dependency listed in `package.xml`)

## Build
From the repository root (workspace):

```bash
source /opt/ros/<ros_distro>/setup.bash
colcon build --packages-select robot
source install/setup.bash
```

## Run the simulation
Launch the Gazebo world, spawn the robot, and start the bridges:

```bash
source /opt/ros/<ros_distro>/setup.bash
source install/setup.bash
ros2 launch robot sim.launch.py
```

In a second terminal, start the obstacle avoidance node:

```bash
source /opt/ros/<ros_distro>/setup.bash
source install/setup.bash
ros2 run robot obstacle_avoidance
```

## Topics
The node uses:
- **Input:** `/scan` (`sensor_msgs/msg/LaserScan`)
- **Output:** `/cmd_vel` (`geometry_msgs/msg/Twist`)

## License
Apache-2.0. See `src/robot/package.xml` for details.
