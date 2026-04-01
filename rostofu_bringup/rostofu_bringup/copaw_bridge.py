#!/usr/bin/env python3
"""
RosPaw Copaw Bridge
与 copaw AI 助手的桥接模块

功能:
- 启动和管理 copaw 进程
- 通过 API 与 copaw 通信
- 将 copaw 的响应转发到 ROS2
"""

import os
import json
import asyncio
import aiohttp
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


@dataclass
class CopawConfig:
    """Copaw 配置"""
    executable_path: str = ""
    working_directory: str = ""
    api_host: str = "127.0.0.1"
    api_port: int = 8088
    auto_start: bool = True


class CopawBridge:
    """
    Copaw 桥接器
    管理 copaw 进程并提供 API 通信
    """
    
    def __init__(self, node: Node, config: CopawConfig):
        self.node = node
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self._callbacks: List[Callable] = []
        
        # 发布 copaw 响应
        self.response_pub = node.create_publisher(
            String, '/copaw/response', 10)
    
    async def start(self) -> bool:
        """启动 copaw 进程"""
        if self.process and self.process.poll() is None:
            self.node.get_logger().info('Copaw 已经在运行')
            return True
        
        # 查找 copaw 可执行文件
        copaw_path = self._find_executable()
        if not copaw_path:
            self.node.get_logger().error('找不到 copaw 可执行文件')
            return False
        
        try:
            self.node.get_logger().info(f'启动 copaw: {copaw_path}')
            
            # 设置环境
            env = os.environ.copy()
            work_dir = self.config.working_directory or str(Path(copaw_path).parent)
            
            # Windows 下使用 CREATE_NEW_PROCESS_GROUP
            import sys
            if sys.platform == 'win32':
                self.process = subprocess.Popen(
                    [copaw_path],
                    cwd=work_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                self.process = subprocess.Popen(
                    [copaw_path],
                    cwd=work_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    start_new_session=True
                )
            
            self.node.get_logger().info(f'Copaw 已启动，PID: {self.process.pid}')
            
            # 等待 copaw API 就绪
            await asyncio.sleep(3)
            
            # 初始化 HTTP 会话
            self.session = aiohttp.ClientSession()
            
            # 测试连接
            if await self._check_health():
                self.node.get_logger().info('Copaw API 连接成功')
                return True
            else:
                self.node.get_logger().warn('Copaw API 连接失败，但进程已启动')
                return True
            
        except Exception as e:
            self.node.get_logger().error(f'启动 copaw 失败: {e}')
            return False
    
    async def stop(self) -> bool:
        """停止 copaw 进程"""
        if not self.process:
            return True
        
        try:
            # 关闭 HTTP 会话
            if self.session:
                await self.session.close()
                self.session = None
            
            # 终止进程
            import sys
            if sys.platform == 'win32':
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.process.pid)])
            else:
                import signal
                try:
                    import os as os_module
                    pgid = os_module.getpgid(self.process.pid)
                    os_module.killpg(pgid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                self.process.terminate()
            
            self.process = None
            self.node.get_logger().info('Copaw 已停止')
            return True
            
        except Exception as e:
            self.node.get_logger().error(f'停止 copaw 失败: {e}')
            return False
    
    async def chat(self, message: str, conversation_id: Optional[str] = None) -> Optional[str]:
        """
        与 copaw 对话
        
        Args:
            message: 用户消息
            conversation_id: 对话 ID（用于保持上下文）
        
        Returns:
            copaw 的回复文本
        """
        if not await self._check_health():
            self.node.get_logger().error('Copaw API 不可用')
            return None
        
        url = f"http://{self.config.api_host}:{self.config.api_port}/api/chat"
        
        payload = {
            "message": message,
            "conversation_id": conversation_id or "default"
        }
        
        try:
            async with self.session.post(url, json=payload, timeout=30) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    response_text = result.get('response', '')
                    
                    # 发布响应
                    msg = String()
                    msg.data = response_text
                    self.response_pub.publish(msg)
                    
                    return response_text
                else:
                    self.node.get_logger().error(f'Copaw API 错误: {resp.status}')
                    return None
                    
        except Exception as e:
            self.node.get_logger().error(f'Copaw 对话失败: {e}')
            return None
    
    async def execute_skill(self, skill_name: str, parameters: Dict[str, Any] = None) -> Optional[Dict]:
        """
        执行 copaw skill
        
        Args:
            skill_name: Skill 名称
            parameters: Skill 参数
        
        Returns:
            执行结果
        """
        if not await self._check_health():
            return None
        
        url = f"http://{self.config.api_host}:{self.config.api_port}/api/skills/{skill_name}/execute"
        
        try:
            async with self.session.post(
                url, 
                json=parameters or {}, 
                timeout=60
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    self.node.get_logger().error(f'Skill 执行错误: {resp.status}')
                    return None
                    
        except Exception as e:
            self.node.get_logger().error(f'Skill 执行失败: {e}')
            return None
    
    async def get_status(self) -> Optional[Dict]:
        """获取 copaw 状态"""
        try:
            url = f"http://{self.config.api_host}:{self.config.api_port}/api/status"
            async with self.session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    return await resp.json()
                return None
        except:
            return None
    
    async def _check_health(self) -> bool:
        """检查 copaw API 健康状态"""
        if not self.session:
            return False
        
        try:
            url = f"http://{self.config.api_host}:{self.config.api_port}/api/health"
            async with self.session.get(url, timeout=5) as resp:
                return resp.status == 200
        except:
            return False
    
    def _find_executable(self) -> Optional[str]:
        """查找 copaw 可执行文件"""
        if self.config.executable_path and Path(self.config.executable_path).exists():
            return self.config.executable_path
        
        # 尝试常见路径
        possible_paths = [
            Path(__file__).parent.parent.parent.parent / '.venv' / 'Scripts' / 'copaw.exe',
            Path(__file__).parent.parent.parent.parent / '.venv' / 'bin' / 'copaw',
            Path.home() / 'RosPaw' / '.venv' / 'Scripts' / 'copaw.exe',
            Path('D:/githbi/RosPaw/.venv/Scripts/copaw.exe'),
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        # 尝试在 PATH 中查找
        try:
            import shutil
            copaw_path = shutil.which('copaw')
            if copaw_path:
                return copaw_path
        except:
            pass
        
        return None
    
    def is_running(self) -> bool:
        """检查 copaw 是否正在运行"""
        return self.process is not None and self.process.poll() is None
