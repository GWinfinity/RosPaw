from setuptools import find_packages, setup

package_name = 'rostofu_bringup'

setup(
    name=package_name,
    version='0.2.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', [
            'launch/copaw_launch.py',
            'launch/rospaw_nl_launch.py',
        ]),
        ('share/' + package_name + '/config', [
            'config/rospaw_nl.yaml',
        ]),
    ],
    install_requires=[
        'setuptools',
        'aiohttp>=3.8.0',  # 异步 HTTP 客户端
    ],
    extras_require={
        'voice': [
            'openai-whisper>=20231117',  # 本地语音识别
            'sounddevice>=0.4.6',        # 音频录制
            'edge-tts>=6.1.0',           # 语音合成
            'pygame>=2.5.0',             # 音频播放
            'numpy>=1.24.0',
        ],
        'all': [
            'openai-whisper>=20231117',
            'sounddevice>=0.4.6',
            'edge-tts>=6.1.0',
            'pygame>=2.5.0',
            'numpy>=1.24.0',
            'openai>=1.0.0',             # OpenAI API
            'dashscope>=1.0.0',          # 阿里云 DashScope
        ],
    },
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@example.com',
    description='ROS2 package for launching copaw with natural language control',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'copaw_node = rostofu_bringup.copaw_node:main',
            'nl_commander_node = rostofu_bringup.nl_commander_node:main',
            'voice_input_node = rostofu_bringup.voice_input_node:main',
        ],
    },
)
