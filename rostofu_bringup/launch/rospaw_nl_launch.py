"""
RosPaw NL (Natural Language) Launch File
启动自然语言控制完整栈

包含:
- NL Commander Node (自然语言解析)
- Voice Input Node (语音输入, 可选)
- Copaw Node (AI 助手)
"""

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, 
    IncludeLaunchDescription,
)
from launch.conditions import LaunchConfigurationEquals
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    """Generate launch description for RosPaw NL."""
    
    # 声明参数
    llm_provider_arg = DeclareLaunchArgument(
        'llm_provider',
        default_value='ollama',
        description='LLM provider: ollama, openai, dashscope, zhipu'
    )
    
    ollama_model_arg = DeclareLaunchArgument(
        'ollama_model',
        default_value='qwen2.5:7b',
        description='Ollama model name'
    )
    
    dashscope_api_key_arg = DeclareLaunchArgument(
        'dashscope_api_key',
        default_value='',
        description='DashScope API Key (for dashscope provider)'
    )
    
    voice_enabled_arg = DeclareLaunchArgument(
        'voice_enabled',
        default_value='false',
        description='Enable voice input'
    )
    
    tts_enabled_arg = DeclareLaunchArgument(
        'tts_enabled',
        default_value='false',
        description='Enable text-to-speech'
    )
    
    auto_execute_arg = DeclareLaunchArgument(
        'auto_execute',
        default_value='true',
        description='Auto execute parsed commands'
    )
    
    # NL Commander Node
    nl_commander_node = Node(
        package='rostofu_bringup',
        executable='nl_commander_node',
        name='nl_commander',
        output='screen',
        parameters=[{
            'llm_provider': LaunchConfiguration('llm_provider'),
            'ollama_model': LaunchConfiguration('ollama_model'),
            'dashscope_api_key': LaunchConfiguration('dashscope_api_key'),
            'auto_execute': LaunchConfiguration('auto_execute'),
            'tts_enabled': LaunchConfiguration('tts_enabled'),
        }],
    )
    
    # Voice Input Node (条件启动)
    voice_input_node = Node(
        package='rostofu_bringup',
        executable='voice_input_node',
        name='voice_input',
        output='screen',
        parameters=[{
            'enabled': LaunchConfiguration('voice_enabled'),
            'stt_provider': 'whisper',
            'whisper_model': 'base',
            'language': 'zh',
            'wake_word': '你好机器人',
        }],
        condition=LaunchConfigurationEquals('voice_enabled', 'true')
    )
    
    # 包含原有的 copaw launch
    copaw_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('rostofu_bringup'),
                'launch',
                'copaw_launch.py'
            )
        )
    )
    
    return LaunchDescription([
        # 参数声明
        llm_provider_arg,
        ollama_model_arg,
        dashscope_api_key_arg,
        voice_enabled_arg,
        tts_enabled_arg,
        auto_execute_arg,
        
        # 节点
        copaw_launch,
        nl_commander_node,
        voice_input_node,
    ])
