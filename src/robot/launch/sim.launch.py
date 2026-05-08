import os

from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable, TimerAction
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg_path = get_package_share_directory('robot')
    world_file = os.path.join(pkg_path, 'worlds', 'obstacle_world.sdf')
    sdf_file = os.path.join(pkg_path, 'models', 'robot.sdf')
    urdf_file = os.path.join(pkg_path, 'urdf', 'robot.urdf')

    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    return LaunchDescription([

        # ---------------------------------------------------
        # Gazebo resource path so meshes/models are discoverable
        # ---------------------------------------------------
        SetEnvironmentVariable(
            name='GZ_SIM_RESOURCE_PATH',
            value=pkg_path
        ),

        # ---------------------------------------------------
        # Publish URDF + TF tree for RViz RobotModel
        # ---------------------------------------------------
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[
                {'robot_description': robot_desc},
                {'use_sim_time': True}
            ],
            output='screen'
        ),

        # ---------------------------------------------------
        # Launch Gazebo world
        # ---------------------------------------------------
        ExecuteProcess(
            cmd=['ign', 'gazebo', world_file, '-r'],
            output='screen'
        ),

        # ---------------------------------------------------
        # Spawn robot into Gazebo after world loads
        # ---------------------------------------------------
        TimerAction(
            period=3.0,
            actions=[
                ExecuteProcess(
                    cmd=[
                        'ros2', 'run', 'ros_gz_sim', 'create',
                        '-file', sdf_file,
                        '-name', 'my_robot',
                        '-x', '0.0',
                        '-y', '0.0',
                        '-z', '0.1'
                    ],
                    output='screen'
                )
            ]
        ),

        # ---------------------------------------------------
        # Start ROS <-> Gazebo topic bridges
        # ---------------------------------------------------
        TimerAction(
            period=5.0,
            actions=[
                Node(
                    package='ros_gz_bridge',
                    executable='parameter_bridge',
                    arguments=[
                        '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
                        '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
                        '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
                        '/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',
                        '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
                        '/joint_states@sensor_msgs/msg/JointState[ignition.msgs.Model'
                    ],
                    output='screen'
                )
            ]
        )
    ])
