# 🎙️ RosPaw NL (Natural Language) 自然语言控制

RosPaw NL 为 RosPaw 添加了自然语言交互和控制能力，让用户可以通过日常语言与机器人交互。

---

## ✨ 功能特性

| 功能 | 描述 | 状态 |
|------|------|------|
| 🗣️ **自然语言理解** | LLM 解析用户意图 | ✅ |
| 🎤 **语音输入** | 支持语音识别 (Whisper/云端) | ✅ |
| 🔊 **语音合成** | TTS 回复 (Edge/Azure) | ✅ |
| 🤖 **Copaw 集成** | 与 AI 助手深度集成 | ✅ |
| 🧭 **导航控制** | "去厨房"、"去客厅" | ✅ |
| 🎮 **运动控制** | "向前1米"、"左转" | ✅ |
| 📷 **视觉功能** | "拍照"、"查看" | ✅ |
| 🦾 **机械臂控制** | "抓取杯子"、"放置" | ✅ |
| 🛡️ **安全机制** | 紧急停止、确认机制 | ✅ |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 基础依赖
pip install aiohttp

# 语音功能 (可选)
pip install openai-whisper sounddevice edge-tts pygame

# 本地 LLM (推荐)
# 安装 Ollama: https://ollama.com
ollama pull qwen2.5:7b  # 或其他模型
```

### 2. 启动自然语言控制

#### 方式一: 启动脚本 (Windows)
```batch
double click: start_nl_mode.bat
```

#### 方式二: 命令行
```bash
# 终端 1: 启动 Copaw
copaw

# 终端 2: 启动 NL Commander
ros2 run rostofu_bringup nl_commander_node

# 终端 3 (可选): 启动语音输入
ros2 run rostofu_bringup voice_input_node
```

### 3. 发送自然语言命令

```bash
# 使用 CLI 工具
python rostofu_cli.py "去厨房拿杯水"

# 或使用 ROS2 话题
ros2 topic pub /nl_command std_msgs/msg/String '{data: "去厨房"}'

# 交互模式
python rostofu_cli.py --interactive
```

---

## 📖 支持的命令

### 导航命令
| 自然语言 | 执行动作 |
|----------|----------|
| "去厨房" | 导航到预定义位置"厨房" |
| "导航到客厅" | 导航到"客厅" |
| "去坐标 1.5 2.0" | 导航到指定坐标 |
| "回来" | 返回原点/充电座 |

### 运动控制
| 自然语言 | 执行动作 |
|----------|----------|
| "向前移动1米" | 向前直行1米 |
| "后退0.5米" | 向后退0.5米 |
| "向左转" | 原地左转90度 |
| "向右转" | 原地右转90度 |
| "停止" / "停下" | 立即停止 |

### 视觉与感知
| 自然语言 | 执行动作 |
|----------|----------|
| "拍照" | 拍摄当前画面 |
| "查看前方" | 开启摄像头预览 |
| "扫描环境" | 执行360度扫描 |

### 机械臂操作
| 自然语言 | 执行动作 |
|----------|----------|
| "抓取桌上的杯子" | 识别并抓取物体 |
| "把物品放到右边" | 放置到指定位置 |
| "放下" | 释放当前物体 |

### AI 对话
| 自然语言 | 响应方式 |
|----------|----------|
| "你能做什么" | Copaw AI 回答能力范围 |
| "帮我规划路径" | AI 路径规划建议 |
| "电池还剩多少" | 查询并报告状态 |

---

## ⚙️ 配置

### 配置文件: `rostofu_bringup/config/rospaw_nl.yaml`

```yaml
nl_commander:
  ros__parameters:
    # LLM 选择: ollama, openai, dashscope, zhipu
    llm_provider: "ollama"
    
    # Ollama 本地配置
    ollama_host: "http://localhost:11434"
    ollama_model: "qwen2.5:7b"
    
    # 阿里云 DashScope (推荐国内用户)
    dashscope_api_key: "your-api-key"
    dashscope_model: "qwen-turbo"
    
    # 执行设置
    auto_execute: true        # 自动执行命令
    require_confirmation: false  # 需要确认
    tts_enabled: false        # 语音合成
```

### 使用配置文件启动
```bash
ros2 launch rostofu_bringup rospaw_nl_launch.py
```

---

## 🎯 LLM 提供商对比

| 提供商 | 特点 | 延迟 | 成本 | 推荐场景 |
|--------|------|------|------|----------|
| **Ollama** | 本地运行，无需网络 | ~100ms | 免费 | 隐私敏感、离线环境 |
| **DashScope** | 阿里云，中文强 | ~200ms | 低 | 国内用户、生产环境 |
| **OpenAI** | 能力强，英文好 | ~500ms | 高 | 英文场景、复杂推理 |
| **智谱AI** | 国产，GLM系列 | ~300ms | 中 | 国内用户 |

### Ollama 推荐模型
```bash
# 轻量级 (< 4GB VRAM)
ollama pull qwen2.5:1.8b

# 标准 (4-8GB VRAM)
ollama pull qwen2.5:7b

# 高性能 (> 8GB VRAM)
ollama pull qwen2.5:14b
ollama pull llama3.1:8b
```

---

## 🎤 语音交互

### 启用语音输入
```bash
ros2 run rostofu_bringup voice_input_node --ros-args -p enabled:=true
```

### 语音命令流程
```
1. 说唤醒词: "你好机器人"
2. 听到提示音后说出命令
3. 系统自动识别并执行
```

### 自定义唤醒词
```bash
ros2 param set /voice_input wake_word "小R小R"
```

---

## 🔧 高级用法

### 1. 自定义命令解析
编辑 `nl_commander_node.py` 中的 `SYSTEM_PROMPT` 添加新的命令类型。

### 2. 添加新的执行器
在 `NLCommanderNode` 中添加新的执行方法:
```python
async def _execute_custom(self, params: Dict):
    """自定义命令执行"""
    # 实现你的逻辑
    pass
```

### 3. 与现有系统集成
```python
# 订阅 NL 响应
ros2 topic echo /nl_response

# 程序化发送命令
ros2 topic pub /nl_command std_msgs/msg/String '{data: "停止"}'
```

---

## 🐛 故障排除

### 问题: Ollama 连接失败
```
解决方案:
1. 确认 Ollama 已安装: curl http://localhost:11434
2. 拉取模型: ollama pull qwen2.5:7b
3. 检查防火墙设置
```

### 问题: Copaw 无法启动
```
解决方案:
1. 检查虚拟环境: .venv\Scripts\copaw.exe --version
2. 确认 copaw 已安装: pip install copaw
3. 查看日志: ros2 topic echo /rosout
```

### 问题: 语音识别不准确
```
解决方案:
1. 检查麦克风: 系统设置 -> 声音
2. 调整录音时长: record_seconds 参数
3. 使用云端 STT: stt_provider:=dashscope
```

### 问题: 命令执行失败
```
解决方案:
1. 查看解析结果: ros2 topic echo /nl_response
2. 检查置信度: 低置信度命令可能需要确认
3. 查看节点日志: ros2 run rostofu_bringup nl_commander_node --ros-args --log-level debug
```

---

## 📊 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户交互层                            │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐  │
│  │  文本输入   │  │  语音输入   │  │  rostofu_cli.py      │  │
│  │ /nl_command│  │ Voice Input│  │ 命令行工具           │  │
│  └─────┬──────┘  └─────┬──────┘  └──────────┬───────────┘  │
└────────┼───────────────┼────────────────────┼──────────────┘
         │               │                    │
         └───────────────┴────────────────────┘
                         │
┌────────────────────────┼────────────────────────────────────┐
│                  NL Commander Node                          │
│  ┌─────────────────────┴────────────────────────────────┐  │
│  │                  LLM Provider                         │  │
│  │  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │  │
│  │  │ Ollama  │  │DashScope │  │ OpenAI   │  │ 智谱AI │ │  │
│  │  │(本地)   │  │ (云端)   │  │ (云端)   │  │ (云端) │ │  │
│  │  └─────────┘  └──────────┘  └──────────┘  └────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                   │
│  ┌──────────────────────┼───────────────────────────────┐  │
│  │                  Command Executor                      │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │  │
│  │  │Navigate│ │  Move  │ │  Stop  │ │  Chat  │ ...    │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────┼────────────────────────────────────┐
│                    Copaw Bridge                             │
│                     │ Copaw AI                              │
└────────────────────────┼────────────────────────────────────┘
                         │
┌────────────────────────┼────────────────────────────────────┐
│                    ROS2 系统                                │
│  ┌────────┐ ┌────────┐ │ ┌────────┐ ┌────────┐            │
│  │Navigation│ │cmd_vel │ │ │ Camera │ │  Arm   │            │
│  └────────┘ └────────┘ │ └────────┘ └────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤝 贡献

欢迎提交 PR 添加新的命令类型或改进自然语言理解能力！

---

**🎙️ RosPaw NL - 让机器人听懂你说的话！**
