#!/usr/bin/env python3
"""
示例: 使用自然语言控制导航

功能:
- 发送导航命令
- 接收响应
- 简单的命令循环
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time


class NLNavigator(Node):
    def __init__(self):
        super().__init__('nl_navigator')
        
        # 发布命令
        self.command_pub = self.create_publisher(String, '/nl_command', 10)
        
        # 订阅响应
        self.create_subscription(String, '/nl_response', self._on_response, 10)
        
        # 等待发布者就绪
        time.sleep(1)
    
    def _on_response(self, msg: String):
        print(f"🤖 机器人回复: {msg.data}")
    
    def send(self, text: str):
        msg = String()
        msg.data = text
        self.command_pub.publish(msg)
        print(f"👤 我说: {text}")


def main():
    rclpy.init()
    node = NLNavigator()
    
    # 示例命令序列
    commands = [
        "去厨房",
        "拍照",
        "向前移动1米",
        "停止",
        "你能做什么",
    ]
    
    print("=" * 50)
    print("自然语言导航示例")
    print("=" * 50)
    
    for cmd in commands:
        node.send(cmd)
        time.sleep(3)  # 等待响应
    
    print("\n示例完成!")
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
