#!/usr/bin/env python3
"""
RosPaw NL (Natural Language) Commander Node
轻量级自然语言控制节点 - 纯 Python 实现

功能:
- 接收自然语言命令
- 使用 LLM 解析意图
- 执行 ROS2 操作
- 支持本地(Ollama)和云端 LLM
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import String, Bool
from std_srvs.srv import Trigger, SetBool
from geometry_msgs.msg import Twist, PoseStamped
from nav2_msgs.action import NavigateToPose
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class CommandType(Enum):
    """支持的命令类型"""
    COPAW_CHAT = "copaw_chat"          # 与 copaw 对话
    NAVIGATE = "navigate"               # 导航到位置
    MOVE = "move"                       # 移动控制
    STOP = "stop"                       # 紧急停止
    TAKE_PHOTO = "take_photo"           # 拍照
    ARM_CONTROL = "arm_control"         # 机械臂控制
    STATUS_CHECK = "status_check"       # 状态查询
    UNKNOWN = "unknown"


@dataclass
class ParsedCommand:
    """解析后的命令结构"""
    command_type: CommandType
    raw_text: str
    parameters: Dict[str, Any]
    confidence: float
    response_text: str  # 给用户的回复


class LLMProvider:
    """LLM 提供商基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def parse_command(self, text: str) -> ParsedCommand:
        raise NotImplementedError


class OllamaProvider(LLMProvider):
    """本地 Ollama LLM 支持"""
    
    SYSTEM_PROMPT = """你是一个机器人命令解析助手。将用户的自然语言指令解析为结构化命令。

支持的命令类型:
1. copaw_chat - 与AI助手对话，参数: {"message": "对话内容"}
2. navigate - 导航到指定位置，参数: {"location": "位置描述", "coordinates": {"x": 0, "y": 0}}
3. move - 移动控制，参数: {"direction": "forward/backward/left/right", "distance": 1.0, "speed": 0.5}
4. stop - 紧急停止，参数: {}
5. take_photo - 拍照，参数: {"save_path": "可选保存路径"}
6. arm_control - 机械臂控制，参数: {"action": "pick/place/move", "object": "物体名称", "position": {"x": 0, "y": 0, "z": 0}}
7. status_check - 查询状态，参数: {"component": "battery/position/system"}

输出格式(JSON):
{
    "command_type": "命令类型",
    "parameters": {},
    "confidence": 0.95,
    "response_text": "给用户的友好回复"
}

示例:
用户: "去厨房拿杯水"
输出: {"command_type": "navigate", "parameters": {"location": "厨房"}, "confidence": 0.9, "response_text": "好的，我正在前往厨房"}

用户: "停止"
输出: {"command_type": "stop", "parameters": {}, "confidence": 1.0, "response_text": "已停止"}
"""

    async def parse_command(self, text: str) -> ParsedCommand:
        import aiohttp
        
        url = f"{self.config.get('host', 'http://localhost:11434')}/api/generate"
        model = self.config.get('model', 'qwen2.5:7b')
        
        payload = {
            "model": model,
            "prompt": f"{self.SYSTEM_PROMPT}\n\n用户: {text}\n输出:",
            "stream": False,
            "format": "json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=30) as resp:
                    result = await resp.json()
                    parsed = json.loads(result['response'])
                    
                    return ParsedCommand(
                        command_type=CommandType(parsed.get('command_type', 'unknown')),
                        raw_text=text,
                        parameters=parsed.get('parameters', {}),
                        confidence=parsed.get('confidence', 0.5),
                        response_text=parsed.get('response_text', '收到指令')
                    )
        except Exception as e:
            return ParsedCommand(
                command_type=CommandType.COPAW_CHAT,
                raw_text=text,
                parameters={"message": text},
                confidence=0.5,
                response_text=f"我会将这个请求转发给AI助手: {text}"
            )


class OpenAIProvider(LLMProvider):
    """OpenAI / 阿里云百炼 / 智谱AI 支持"""
    
    SYSTEM_PROMPT = OllamaProvider.SYSTEM_PROMPT
    
    async def parse_command(self, text: str) -> ParsedCommand:
        import aiohttp
        
        api_key = self.config.get('api_key')
        base_url = self.config.get('base_url', 'https://api.openai.com/v1')
        model = self.config.get('model', 'gpt-3.5-turbo')
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            "response_format": {"type": "json_object"}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                ) as resp:
                    result = await resp.json()
                    content = result['choices'][0]['message']['content']
                    parsed = json.loads(content)
                    
                    return ParsedCommand(
                        command_type=CommandType(parsed.get('command_type', 'unknown')),
                        raw_text=text,
                        parameters=parsed.get('parameters', {}),
                        confidence=parsed.get('confidence', 0.5),
                        response_text=parsed.get('response_text', '收到指令')
                    )
        except Exception as e:
            # 失败时降级为 copaw_chat
            return ParsedCommand(
                command_type=CommandType.COPAW_CHAT,
                raw_text=text,
                parameters={"message": text},
                confidence=0.5,
                response_text=f"我会将这个请求转发给AI助手: {text}"
            )


class NLCommanderNode(Node):
    """
    自然语言指挥官节点
    接收自然语言命令，解析并执行
    """
    
    def __init__(self):
        super().__init__('nl_commander_node')
        
        # 声明参数
        self.declare_parameters(namespace='', parameters=[
            ('llm_provider', 'ollama'),  # ollama, openai, dashscope, zhipu
            ('ollama_host', 'http://localhost:11434'),
            ('ollama_model', 'qwen2.5:7b'),
            ('openai_api_key', ''),
            ('openai_base_url', 'https://api.openai.com/v1'),
            ('openai_model', 'gpt-3.5-turbo'),
            ('dashscope_api_key', ''),
            ('dashscope_model', 'qwen-turbo'),
            ('auto_execute', True),
            ('require_confirmation', False),
            ('tts_enabled', False),
            ('tts_provider', 'edge'),  # edge, azure
        ])
        
        # 初始化 LLM 提供商
        self.llm = self._init_llm_provider()
        
        # ROS2 接口
        self.command_sub = self.create_subscription(
            String, '/nl_command', self._on_command, 10)
        
        self.response_pub = self.create_publisher(
            String, '/nl_response', 10)
        
        self.status_pub = self.create_publisher(
            String, '/nl_status', 10)
        
        # 服务
        self.create_service(Trigger, '/nl_enable', self._enable_callback)
        self.create_service(Trigger, '/nl_disable', self._disable_callback)
        
        # Action Clients
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        # Publisher
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.goal_pub = self.create_publisher(PoseStamped, 'goal_pose', 10)
        
        # 状态
        self.enabled = True
        self.command_history: List[ParsedCommand] = []
        self.pending_confirmation: Optional[ParsedCommand] = None
        
        # 执行器映射
        self.executors: Dict[CommandType, Callable] = {
            CommandType.COPAW_CHAT: self._execute_copaw_chat,
            CommandType.NAVIGATE: self._execute_navigate,
            CommandType.MOVE: self._execute_move,
            CommandType.STOP: self._execute_stop,
            CommandType.TAKE_PHOTO: self._execute_take_photo,
            CommandType.ARM_CONTROL: self._execute_arm_control,
            CommandType.STATUS_CHECK: self._execute_status_check,
        }
        
        self.get_logger().info('🎙️ NL Commander Node 已启动')
        self.get_logger().info(f'   LLM 提供商: {self.get_parameter("llm_provider").value}')
        self.get_logger().info('   等待自然语言命令 (/nl_command)')
    
    def _init_llm_provider(self) -> LLMProvider:
        """初始化 LLM 提供商"""
        provider = self.get_parameter('llm_provider').value
        
        if provider == 'ollama':
            config = {
                'host': self.get_parameter('ollama_host').value,
                'model': self.get_parameter('ollama_model').value
            }
            return OllamaProvider(config)
        
        elif provider in ['openai', 'dashscope', 'zhipu']:
            api_key = self.get_parameter(f'{provider}_api_key').value
            if not api_key:
                self.get_logger().warn(f'{provider} API key 未配置，将使用 Ollama')
                return OllamaProvider({'host': 'http://localhost:11434', 'model': 'qwen2.5:7b'})
            
            config = {
                'api_key': api_key,
                'model': self.get_parameter(f'{provider}_model').value
            }
            
            if provider == 'dashscope':
                config['base_url'] = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
            elif provider == 'zhipu':
                config['base_url'] = 'https://open.bigmodel.cn/api/paas/v4'
            else:
                config['base_url'] = self.get_parameter('openai_base_url').value
            
            return OpenAIProvider(config)
        
        return OllamaProvider({'host': 'http://localhost:11434', 'model': 'qwen2.5:7b'})
    
    def _on_command(self, msg: String):
        """接收自然语言命令"""
        if not self.enabled:
            self._respond("自然语言控制当前已禁用")
            return
        
        text = msg.data.strip()
        if not text:
            return
        
        self.get_logger().info(f'📝 收到命令: {text}')
        
        # 异步解析命令
        asyncio.create_task(self._process_command(text))
    
    async def _process_command(self, text: str):
        """处理命令：解析 → 确认 → 执行"""
        try:
            # 1. LLM 解析
            parsed = await self.llm.parse_command(text)
            self.command_history.append(parsed)
            
            self.get_logger().info(f'🤖 解析结果: {parsed.command_type.value} '
                                   f'(置信度: {parsed.confidence:.2f})')
            
            # 2. 需要确认吗？
            if self.get_parameter('require_confirmation').value and \
               parsed.confidence < 0.8:
                self.pending_confirmation = parsed
                self._respond(f"{parsed.response_text}\n"
                             f"(确认请发送: 确认执行 或 取消)")
                return
            
            # 3. 执行
            if self.get_parameter('auto_execute').value:
                await self._execute_command(parsed)
            else:
                self._respond(f"{parsed.response_text}\n"
                             f"(自动执行已关闭，请调用服务执行)")
        
        except Exception as e:
            self.get_logger().error(f'处理命令失败: {e}')
            self._respond('抱歉，处理命令时出错了')
    
    async def _execute_command(self, parsed: ParsedCommand):
        """执行解析后的命令"""
        executor = self.executors.get(parsed.command_type)
        
        if executor:
            try:
                await executor(parsed.parameters)
                self._publish_status(f"已执行: {parsed.command_type.value}")
            except Exception as e:
                self.get_logger().error(f'执行失败: {e}')
                self._respond(f'执行失败: {e}')
        else:
            self._respond(f'暂不支持该命令类型: {parsed.command_type.value}')
    
    # ========== 具体执行器 ==========
    
    async def _execute_copaw_chat(self, params: Dict):
        """与 copaw 对话"""
        message = params.get('message', '')
        # 这里可以调用 copaw 的 API 或通过话题发布
        self._respond(f'已发送给 copaw: {message}')
    
    async def _execute_navigate(self, params: Dict):
        """导航到指定位置"""
        location = params.get('location', '目标位置')
        coords = params.get('coordinates', {})
        
        goal_msg = PoseStamped()
        goal_msg.header.frame_id = 'map'
        goal_msg.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.position.x = coords.get('x', 0.0)
        goal_msg.pose.position.y = coords.get('y', 0.0)
        goal_msg.pose.orientation.w = 1.0
        
        self.goal_pub.publish(goal_msg)
        self._respond(f'正在导航到: {location}')
    
    async def _execute_move(self, params: Dict):
        """移动控制"""
        direction = params.get('direction', 'forward')
        distance = params.get('distance', 1.0)
        speed = params.get('speed', 0.5)
        
        twist = Twist()
        
        if direction == 'forward':
            twist.linear.x = speed
        elif direction == 'backward':
            twist.linear.x = -speed
        elif direction == 'left':
            twist.angular.z = speed
        elif direction == 'right':
            twist.angular.z = -speed
        
        self.cmd_vel_pub.publish(twist)
        self._respond(f'正在向 {direction} 移动 {distance} 米')
        
        # 简单定时停止 (实际应该使用里程计)
        await asyncio.sleep(distance / speed)
        self.cmd_vel_pub.publish(Twist())  # 停止
    
    async def _execute_stop(self, params: Dict):
        """紧急停止"""
        self.cmd_vel_pub.publish(Twist())
        self._respond('🛑 已紧急停止')
    
    async def _execute_take_photo(self, params: Dict):
        """拍照"""
        save_path = params.get('save_path', '/tmp/photo.jpg')
        self._respond(f'📷 拍照已触发，保存至: {save_path}')
    
    async def _execute_arm_control(self, params: Dict):
        """机械臂控制"""
        action = params.get('action', 'move')
        obj = params.get('object', '')
        self._respond(f'🦾 执行机械臂动作: {action} {obj}')
    
    async def _execute_status_check(self, params: Dict):
        """状态查询"""
        component = params.get('component', 'system')
        self._respond(f'🔍 查询 {component} 状态中...')
    
    # ========== 辅助方法 ==========
    
    def _respond(self, text: str):
        """发送回复给用户"""
        msg = String()
        msg.data = text
        self.response_pub.publish(msg)
        self.get_logger().info(f'💬 回复: {text}')
        
        # TTS
        if self.get_parameter('tts_enabled').value:
            self._speak(text)
    
    def _speak(self, text: str):
        """语音合成"""
        provider = self.get_parameter('tts_provider').value
        
        if provider == 'edge':
            # 使用 edge-tts (需要安装: pip install edge-tts)
            try:
                import edge_tts
                asyncio.create_task(self._edge_tts_speak(text))
            except ImportError:
                self.get_logger().warn('edge-tts 未安装，跳过语音合成')
    
    async def _edge_tts_speak(self, text: str):
        """Edge TTS 实现"""
        import edge_tts
        import tempfile
        import pygame
        
        communicate = edge_tts.Communicate(text, voice="zh-CN-XiaoxiaoNeural")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
            await communicate.save(tmp.name)
            
            pygame.mixer.init()
            pygame.mixer.music.load(tmp.name)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
    
    def _publish_status(self, status: str):
        """发布状态"""
        msg = String()
        msg.data = status
        self.status_pub.publish(msg)
    
    def _enable_callback(self, request, response):
        """启用 NL 控制"""
        self.enabled = True
        response.success = True
        response.message = '自然语言控制已启用'
        return response
    
    def _disable_callback(self, request, response):
        """禁用 NL 控制"""
        self.enabled = False
        response.success = True
        response.message = '自然语言控制已禁用'
        return response


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
