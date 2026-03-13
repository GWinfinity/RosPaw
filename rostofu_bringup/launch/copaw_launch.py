"""
Launch file for starting copaw ROS2 node.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for copaw node."""
    
    # Declare launch arguments
    copaw_path_arg = DeclareLaunchArgument(
        'copaw_path',
        default_value='',
        description='Path to copaw.exe executable (auto-detected if empty)'
    )
    
    working_dir_arg = DeclareLaunchArgument(
        'working_directory',
        default_value='',
        description='Working directory for copaw process'
    )
    
    auto_start_arg = DeclareLaunchArgument(
        'auto_start',
        default_value='true',
        description='Automatically start copaw on node startup'
    )
    
    # Create the copaw node
    copaw_node = Node(
        package='rostofu_bringup',
        executable='copaw_node',
        name='copaw_node',
        output='screen',
        parameters=[{
            'copaw_path': LaunchConfiguration('copaw_path'),
            'working_directory': LaunchConfiguration('working_directory'),
            'auto_start': LaunchConfiguration('auto_start'),
        }],
        emulate_tty=True,
    )
    
    return LaunchDescription([
        copaw_path_arg,
        working_dir_arg,
        auto_start_arg,
        copaw_node,
    ])
