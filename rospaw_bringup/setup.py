from setuptools import find_packages, setup

package_name = 'rospaw_bringup'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/copaw_launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@example.com',
    description='ROS2 package for launching copaw application',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'copaw_node = rospaw_bringup.copaw_node:main',
        ],
    },
)
