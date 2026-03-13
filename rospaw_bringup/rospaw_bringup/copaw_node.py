#!/usr/bin/env python3
"""
ROS2 Node for launching copaw application.
Compatible with both Windows and Linux/Ubuntu.
"""

import os
import sys
import subprocess
import signal
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
from std_msgs.msg import String


class CopawNode(Node):
    """ROS2 Node that manages copaw process."""
    
    def __init__(self):
        super().__init__('copaw_node')
        
        # Declare parameters
        self.declare_parameter('copaw_path', '')
        self.declare_parameter('working_directory', '')
        self.declare_parameter('auto_start', True)
        
        # Get parameters
        copaw_path = self.get_parameter('copaw_path').value
        working_dir = self.get_parameter('working_directory').value
        auto_start = self.get_parameter('auto_start').value
        
        # Detect platform
        self.is_windows = sys.platform == 'win32'
        self.get_logger().info(f'Running on platform: {sys.platform}')
        
        # If not specified, try to find copaw executable
        if not copaw_path:
            copaw_path = self._find_copaw_executable()
        
        self.copaw_path = copaw_path
        self.working_dir = working_dir if working_dir else str(Path(copaw_path).parent) if copaw_path else os.getcwd()
        self.process = None
        
        # Create services
        self.start_service = self.create_service(Trigger, 'start_copaw', self.start_copaw_callback)
        self.stop_service = self.create_service(Trigger, 'stop_copaw', self.stop_copaw_callback)
        self.restart_service = self.create_service(Trigger, 'restart_copaw', self.restart_copaw_callback)
        
        # Create publisher for status
        self.status_publisher = self.create_publisher(String, 'copaw_status', 10)
        
        # Create timer for status check
        self.status_timer = self.create_timer(1.0, self.publish_status)
        
        # Auto start if enabled
        if auto_start and self.copaw_path:
            self.get_logger().info('Auto-starting copaw...')
            self.start_copaw()
        
        self.get_logger().info(f'CopawNode initialized')
        self.get_logger().info(f'Copaw path: {self.copaw_path}')
        self.get_logger().info(f'Working directory: {self.working_dir}')
    
    def _find_copaw_executable(self):
        """Auto-detect copaw executable path."""
        # Try common paths based on platform
        possible_paths = []
        
        if self.is_windows:
            possible_paths = [
                # Windows virtual environment paths
                Path(__file__).parent.parent.parent.parent / '.venv' / 'Scripts' / 'copaw.exe',
                Path(__file__).parent.parent.parent.parent / 'venv' / 'Scripts' / 'copaw.exe',
                Path.home() / 'RosPaw' / '.venv' / 'Scripts' / 'copaw.exe',
                Path('D:/githbi/RosPaw/.venv/Scripts/copaw.exe'),
            ]
        else:
            # Linux/Ubuntu paths
            possible_paths = [
                # Linux virtual environment paths
                Path(__file__).parent.parent.parent.parent / '.venv' / 'bin' / 'copaw',
                Path(__file__).parent.parent.parent.parent / 'venv' / 'bin' / 'copaw',
                Path.home() / 'RosPaw' / '.venv' / 'bin' / 'copaw',
                Path.home() / 'ros2_ws' / 'src' / 'RosPaw' / '.venv' / 'bin' / 'copaw',
                Path('/opt/rospaw/.venv/bin/copaw'),
            ]
            
            # Also try to find in PATH
            try:
                result = subprocess.run(['which', 'copaw'], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except Exception:
                pass
        
        for path in possible_paths:
            if path.exists():
                self.get_logger().info(f'Auto-detected copaw at: {path}')
                return str(path)
        
        return ''
    
    def start_copaw(self):
        """Start the copaw process."""
        if self.process is not None and self.process.poll() is None:
            self.get_logger().warn('Copaw is already running')
            return False
        
        if not self.copaw_path or not os.path.exists(self.copaw_path):
            self.get_logger().error(f'Copaw executable not found: {self.copaw_path}')
            return False
        
        try:
            self.get_logger().info(f'Starting copaw: {self.copaw_path}')
            
            # Setup environment with virtual environment if available
            env = os.environ.copy()
            venv_path = Path(self.copaw_path).parent.parent
            if (venv_path / 'bin').exists() or (venv_path / 'Scripts').exists():
                # It's a virtual environment
                if self.is_windows:
                    env['PATH'] = str(venv_path / 'Scripts') + os.pathsep + env.get('PATH', '')
                else:
                    env['PATH'] = str(venv_path / 'bin') + os.pathsep + env.get('PATH', '')
                    env['VIRTUAL_ENV'] = str(venv_path)
            
            # Start copaw process with platform-specific settings
            if self.is_windows:
                # Windows: use CREATE_NEW_PROCESS_GROUP for proper termination
                self.process = subprocess.Popen(
                    [self.copaw_path],
                    cwd=self.working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                # Linux/Ubuntu: use start_new_session to create new process group
                self.process = subprocess.Popen(
                    [self.copaw_path],
                    cwd=self.working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    start_new_session=True,
                    preexec_fn=os.setsid if hasattr(os, 'setsid') else None
                )
            
            self.get_logger().info(f'Copaw started with PID: {self.process.pid}')
            return True
            
        except Exception as e:
            self.get_logger().error(f'Failed to start copaw: {e}')
            return False
    
    def stop_copaw(self):
        """Stop the copaw process."""
        if self.process is None:
            self.get_logger().warn('Copaw is not running')
            return False
        
        try:
            self.get_logger().info('Stopping copaw...')
            
            # Check if process is still running
            if self.process.poll() is not None:
                self.get_logger().info('Copaw has already stopped')
                self.process = None
                return True
            
            # Terminate the process
            if self.is_windows:
                # Windows: use taskkill to terminate the process tree
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.process.pid)])
            else:
                # Linux: send SIGTERM to process group
                try:
                    pgid = os.getpgid(self.process.pid)
                    os.killpg(pgid, signal.SIGTERM)
                except ProcessLookupError:
                    # Process already gone
                    pass
                
                # Wait for graceful termination
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if not terminated
                    try:
                        pgid = os.getpgid(self.process.pid)
                        os.killpg(pgid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    self.process.kill()
            
            self.process = None
            self.get_logger().info('Copaw stopped successfully')
            return True
            
        except Exception as e:
            self.get_logger().error(f'Failed to stop copaw: {e}')
            return False
    
    def start_copaw_callback(self, request, response):
        """Service callback to start copaw."""
        success = self.start_copaw()
        response.success = success
        response.message = 'Copaw started successfully' if success else 'Failed to start copaw'
        return response
    
    def stop_copaw_callback(self, request, response):
        """Service callback to stop copaw."""
        success = self.stop_copaw()
        response.success = success
        response.message = 'Copaw stopped successfully' if success else 'Failed to stop copaw'
        return response
    
    def restart_copaw_callback(self, request, response):
        """Service callback to restart copaw."""
        self.stop_copaw()
        success = self.start_copaw()
        response.success = success
        response.message = 'Copaw restarted successfully' if success else 'Failed to restart copaw'
        return response
    
    def publish_status(self):
        """Publish copaw status."""
        msg = String()
        if self.process is None:
            msg.data = 'stopped'
        elif self.process.poll() is None:
            msg.data = 'running'
        else:
            msg.data = f'exited with code {self.process.returncode}'
            self.process = None
        self.status_publisher.publish(msg)
    
    def destroy_node(self):
        """Clean up when node is destroyed."""
        self.stop_copaw()
        super().destroy_node()


def main(args=None):
    """Main entry point."""
    rclpy.init(args=args)
    
    node = CopawNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Keyboard interrupt received, shutting down...')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
