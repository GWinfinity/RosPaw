#!/usr/bin/env python3
"""
RosPaw CLI - 自然语言控制命令行工具

用法:
    python rostofu_cli.py "去厨房拿杯水"
    python rostofu_cli.py --voice
    python rostofu_cli.py --interactive
"""

import sys
import argparse
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger
import time


class RosPawCLI(Node):
    """RosPaw 命令行客户端"""
    
    def __init__(self):
        super().__init__('rostofu_cli')
        
        # 发布者
        self.command_pub = self.create_publisher(String, '/nl_command', 10)
        
        # 订阅响应
        self.response_sub = self.create_subscription(
            String, '/nl_response', self._on_response, 10)
        
        self.last_response = None
        self.response_received = False
    
    def _on_response(self, msg: String):
        """接收响应"""
        self.last_response = msg.data
        self.response_received = True
        print(f"\n🤖 {msg.data}")
    
    def send_command(self, text: str, wait_response: bool = True, timeout: float = 10.0) -> bool:
        """发送自然语言命令"""
        msg = String()
        msg.data = text
        self.command_pub.publish(msg)
        
        print(f"📝 发送: {text}")
        
        if wait_response:
            self.response_received = False
            start_time = time.time()
            
            while not self.response_received and time.time() - start_time < timeout:
                rclpy.spin_once(self, timeout_sec=0.1)
            
            if not self.response_received:
                print("⚠️ 等待响应超时")
                return False
        
        return True
    
    def interactive_mode(self):
        """交互模式"""
        print("""
╔═══════════════════════════════════════════════════════════╗
║                    RosPaw NL 交互模式                      ║
║                                                           ║
║  输入自然语言命令控制机器人，例如：                        ║
║    - "去厨房"                                             ║
║    - "向前移动1米"                                         ║
║    - "停止"                                               ║
║    - "拍照"                                               ║
║                                                           ║
║  特殊命令:                                                ║
║    /quit  - 退出                                          ║
║    /help  - 显示帮助                                      ║
╚═══════════════════════════════════════════════════════════╝
        """)
        
        while True:
            try:
                text = input("\n👤 你: ").strip()
                
                if not text:
                    continue
                
                if text.lower() in ['/quit', '/exit', '退出']:
                    print("👋 再见!")
                    break
                
                if text.lower() in ['/help', '帮助']:
                    self._show_help()
                    continue
                
                if text.lower() == '/status':
                    self._check_status()
                    continue
                
                self.send_command(text)
                
            except KeyboardInterrupt:
                print("\n👋 再见!")
                break
            except Exception as e:
                print(f"错误: {e}")
    
    def _show_help(self):
        """显示帮助信息"""
        print("""
📖 命令示例:
  导航:
    - "去厨房" / "导航到客厅" / "去坐标 1.5 2.0"
  
  移动:
    - "向前移动1米" / "向左转" / "后退0.5米"
  
  控制:
    - "停止" / "紧急停止"
  
  视觉:
    - "拍照" / "查看摄像头"
  
  机械臂:
    - "抓取桌上的杯子" / "把物品放到右边"
  
  状态:
    - "电池还剩多少" / "你在哪里"
  
  AI对话:
    - "你能做什么" / "帮我规划路径"
        """)
    
    def _check_status(self):
        """检查系统状态"""
        client = self.create_client(Trigger, '/nl_enable')
        if client.wait_for_service(timeout_sec=1.0):
            print("✅ NL Commander 服务可用")
        else:
            print("❌ NL Commander 服务不可用")


def main():
    parser = argparse.ArgumentParser(
        description='RosPaw 自然语言控制 CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s "去厨房"
  %(prog)s "向前移动1米"
  %(prog)s --interactive
  %(prog)s --voice
        """
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        help='自然语言命令 (例如: "去厨房")'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='进入交互模式'
    )
    
    parser.add_argument(
        '-v', '--voice',
        action='store_true',
        help='启用语音输入 (需要麦克风)'
    )
    
    parser.add_argument(
        '-t', '--timeout',
        type=float,
        default=10.0,
        help='等待响应的超时时间 (秒)'
    )
    
    parser.add_argument(
        '--no-wait',
        action='store_true',
        help='不等待响应，发送后立即退出'
    )
    
    args = parser.parse_args()
    
    # 初始化 ROS2
    rclpy.init(args=sys.argv)
    
    node = RosPawCLI()
    
    try:
        if args.interactive:
            node.interactive_mode()
        elif args.voice:
            print("🎤 语音模式 (按 Ctrl+C 退出)")
            # TODO: 实现语音循环
            print("提示: 请确保 voice_input_node 已启动")
        elif args.command:
            node.send_command(
                args.command, 
                wait_response=not args.no_wait,
                timeout=args.timeout
            )
            if not args.no_wait:
                # 等待一会儿接收响应
                time.sleep(2)
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"错误: {e}")
    
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
