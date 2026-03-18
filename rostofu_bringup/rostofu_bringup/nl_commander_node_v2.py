#!/usr/bin/env python3
"""
RosPaw NL Commander Node v2
集成 Copaw Bridge 的完整自然语言控制节点
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import String, Bool
from std_srvs.srv import Trigger, SetBool
from geometry_msgs.msg import Twist, PoseStamped
from nav2_msgs.action import NavigateToPose

# 导入 copaw bridge
from .copaw_bridge import CopawBridge, CopawConfig


class CommandType(Enum):
    """支持的命令类型"""
    COPAW_CHAT = "copaw_chat"
    NAVIGATE = "navigate"
    MOVE = "move"
    STOP = "stop"
    TAKE_PHOTO = "take_photo"
    ARM_CONTROL = "arm_control"
    STATUS_CHECK = "status_check"
    UNKNOWN = "unknown"


class LLMProvider:
    """LLM 提供商基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def parse_command(self, text: str) -> Dict:
        raise NotImplementedError


class OllamaProvider(LLMProvider):
    """本地 Ollama LLM"""
    
    SYSTEM_PROMPT = """你是一个机器人命令解析助手。将用户的自然语言指令解析为结构化命令。

可用命令类型:
- copaw_chat: 需要AI助手回答的问题
- navigate: 导航到指定位置
- move: 移动控制 (forward/backward/left/right)
- stop: 紧急停止
- take_photo: 拍照
- arm_control: 机械臂控制
- status_check: 状态查询

输出严格的JSON格式:
{"command_type": "navigate", "parameters": {"location": "厨房"}, "confidence": 0.95, "response_text": "好的，正在前往厨房"}"""

    async def parse_command(self, text: str) -> Dict:
        try:
            import aiohttp
            
            url = f"{self.config.get('host', 'http://localhost:11434')}/api/generate"
            payload = {
                "model": self.config.get('model', 'qwen2.5:7b'),
                "prompt": f"{self.SYSTEM_PROMPT}\n\n用户: {text}\n输出:",
                "stream": False,
                "format": "json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=30) as resp:
                    result = await resp.json()
                    return json.loads(result['response'])
        except Exception as e:
            return {
                "command_type": "copaw_chat",
                "parameters": {"message": text},
                "confidence": 0.5,
                "response_text": f"我会将这个请求转发给AI助手"
            }


class OpenAIStyleProvider(LLMProvider):
    """OpenAI / DashScope / 智谱AI"""
    
    SYSTEM_PROMPT = OllamaProvider.SYSTEM_PROMPT
    
    async def parse_command(self, text: str) -> Dict:
        try:
            import aiohttp
            
            headers = {
                "Authorization": f"Bearer {self.config['api_key']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.config.get('model', 'gpt-3.5-turbo'),
                "messages": [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": text}
                ],
                "response_format": {"type": "json_object"}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config['base_url']}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                ) as resp:
                    result = await resp.json()
                    content = result['choices'][0]['message']['content']
                    return json.loads(content)
        except Exception as e:
            return {
                "command_type": "copaw_chat",
                "parameters": {"message": text},
                "confidence": 0.5,
                "response_text": f"我会将这个请求转发给AI助手"
            }


class NLCommanderNode(Node):
    """自然语言指挥官节点"""
    
    def __init__(self):
        super().__init__('nl_commander')
        
        # 参数
        self.declare_parameters(namespace='', parameters=[
            ('llm_provider', 'ollama'),
            ('ollama_host', 'http://localhost:11434'),
            ('ollama_model', 'qwen2.5:7b'),
            ('openai_api_key', ''),
            ('openai_base_url', 'https://api.openai.com/v1'),
            ('openai_model', 'gpt-3.5-turbo'),
            ('dashscope_api_key', ''),
            ('dashscope_model', 'qwen-turbo'),
            ('auto_execute', True),
            ('tts_enabled', False),
            ('copaw_enabled', True),
            ('copaw_auto_start', True),
        ])
        
        # 初始化 LLM
        self.llm = self._init_llm()
        
        # 初始化 Copaw Bridge
        self.copaw = None
        if self.get_parameter('copaw_enabled').value:
            copaw_config = CopawConfig(
                auto_start=self.get_parameter('copaw_auto_start').value
            )
            self.copaw = CopawBridge(self, copaw_config)
        
        # ROS2 接口
        self.create_subscription(String, '/nl_command', self._on_command, 10)
        self.response_pub = self.create_publisher(String, '/nl_response', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.goal_pub = self.create_publisher(PoseStamped, 'goal_pose', 10)
        
        self.create_service(Trigger, '/nl/start_copaw', self._start_copaw)
        self.create_service(Trigger, '/nl/stop_copaw', self._stop_copaw)
        
        # 状态
        self.enabled = True
        
        # 启动 copaw
        if self.copaw and self.get_parameter('copaw_auto_start').value:
            asyncio.create_task(self.copaw.start())
        
        self.get_logger().info('🎙️ NL Commander 已启动')
    
    def _init_llm(self) -> LLMProvider:
        provider = self.get_parameter('llm_provider').value
        
        if provider == 'ollama':
            return OllamaProvider({
                'host': self.get_parameter('ollama_host').value,
                'model': self.get_parameter('ollama_model').value
            })
        
        api_key = self.get_parameter(f'{provider}_api_key').value
        if not api_key:
            self.get_logger().warn(f'{provider} API key 未配置，使用 Ollama')
            return OllamaProvider({'host': 'http://localhost:11434', 'model': 'qwen2.5:7b'})
        
        base_urls = {
            'openai': self.get_parameter('openai_base_url').value,
            'dashscope': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
            'zhipu': 'https://open.bigmodel.cn/api/paas/v4'
        }
        
        return OpenAIStyleProvider({
            'api_key': api_key,
            'base_url': base_urls.get(provider, base_urls['openai']),
            'model': self.get_parameter(f'{provider}_model').value
        })
    
    def _on_command(self, msg: String):
        if not self.enabled:
            self._respond("自然语言控制已禁用")
            return
        
        asyncio.create_task(self._process(msg.data.strip()))
    
    async def _process(self, text: str):
        try:
            # 解析命令
            parsed = await self.llm.parse_command(text)
            self.get_logger().info(f"解析: {parsed['command_type']}")
            
            # 执行
            cmd_type = CommandType(parsed.get('command_type', 'unknown'))
            params = parsed.get('parameters', {})
            response = parsed.get('response_text', '收到')
            
            if cmd_type == CommandType.COPAW_CHAT and self.copaw:
                # 转发给 copaw
                copaw_response = await self.copaw.chat(params.get('message', text))
                if copaw_response:
                    self._respond(copaw_response)
                else:
                    self._respond(response)
            
            elif cmd_type == CommandType.NAVIGATE:
                await self._navigate(params)
                self._respond(response)
            
            elif cmd_type == CommandType.MOVE:
                await self._move(params)
                self._respond(response)
            
            elif cmd_type == CommandType.STOP:
                await self._stop()
                self._respond(response)
            
            else:
                self._respond(response)
        
        except Exception as e:
            self.get_logger().error(f'处理失败: {e}')
            self._respond('处理命令时出错')
    
    async def _navigate(self, params: Dict):
        """导航"""
        goal = PoseStamped()
        goal.header.frame_id = 'map'
        goal.header.stamp = self.get_clock().now().to_msg()
        coords = params.get('coordinates', {})
        goal.pose.position.x = coords.get('x', 0.0)
        goal.pose.position.y = coords.get('y', 0.0)
        goal.pose.orientation.w = 1.0
        self.goal_pub.publish(goal)
    
    async def _move(self, params: Dict):
        """移动"""
        twist = Twist()
        direction = params.get('direction', 'forward')
        speed = params.get('speed', 0.5)
        
        if direction == 'forward':
            twist.linear.x = speed
        elif direction == 'backward':
            twist.linear.x = -speed
        elif direction == 'left':
            twist.angular.z = speed
        elif direction == 'right':
            twist.angular.z = -speed
        
        self.cmd_vel_pub.publish(twist)
        await asyncio.sleep(params.get('distance', 1.0) / speed)
        self.cmd_vel_pub.publish(Twist())  # 停止
    
    async def _stop(self):
        """停止"""
        self.cmd_vel_pub.publish(Twist())
    
    def _respond(self, text: str):
        msg = String()
        msg.data = text
        self.response_pub.publish(msg)
        self.get_logger().info(f'💬 {text}')
    
    async def _start_copaw(self, request, response):
        if self.copaw:
            success = await self.copaw.start()
            response.success = success
            response.message = 'Copaw 已启动' if success else '启动失败'
        else:
            response.success = False
            response.message = 'Copaw 未启用'
        return response
    
    async def _stop_copaw(self, request, response):
        if self.copaw:
            success = await self.copaw.stop()
            response.success = success
            response.message = 'Copaw 已停止'
        else:
            response.success = False
            response.message = 'Copaw 未启用'
        return response
    
    def destroy_node(self):
        if self.copaw:
            asyncio.create_task(self.copaw.stop())
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = NLCommanderNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
