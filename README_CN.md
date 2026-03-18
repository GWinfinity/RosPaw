<div align="center">

# 🧊 RosTofu

**ROS2 × Tofu — 让你的应用进入机器人世界**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ROS2](https://img.shields.io/badge/ROS2-Humble%20%7C%20Jazzy-blue.svg)](https://docs.ros.org/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey.svg)]()

[English](README.md) | [中文](README_CN.md) | [🐧 Linux 优势](LINUX_ADVANTAGES.md)

</div>

---

## 🤔 RosTofu 是什么？

**RosTofu** 通过 ROS2 将你的应用程序接入机器人世界。它将可执行文件封装为 ROS2 节点，让你能够：

- 🚀 **启动与控制** — 通过 ROS2 服务启动/停止/重启你的应用
- 📊 **状态监控** — 通过 ROS2 话题实时获取运行状态
- 🔗 **ROS2 集成** — 将你的应用无缝集成到机器人技术栈
- 🖥️ **跨平台** — 支持 Windows 和 Ubuntu

无论你是构建智能机器人应用，还是将软件集成到 ROS2 工作流中，RosTofu 都提供了所需的桥梁。

---

## ✨ 功能特性

| 功能 | 描述 |
|---------|-------------|
| 🎛️ **服务接口** | 通过 `/start_copaw`, `/stop_copaw`, `/restart_copaw` 服务控制 copaw |
| 📡 **状态监控** | 通过 `/copaw_status` 话题追踪 copaw 状态 |
| 🔍 **自动检测** | 自动在 `.venv` 或系统 PATH 中查找可执行文件 |
| ⚡ **启动文件** | 开箱即用的 ROS2 启动配置 |
| 🐧 **多平台** | 原生支持 Windows 和 Linux |

---

## 🚀 快速开始

### 前置条件

- [ROS2 Humble](https://docs.ros.org/en/humble/Installation.html) 或 [Jazzy](https://docs.ros.org/en/jazzy/Installation.html)
- [Python](https://www.python.org/) 3.9+
- [uv](https://docs.astral.sh/uv/)（推荐）或 pip

### 1️⃣ 克隆与设置

```bash
git clone git@github.com:GWinfinity/RosTofu.git
cd RosTofu
```

### 2️⃣ 创建虚拟环境

```bash
# 使用 uv（推荐）
uv venv

# 激活
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows
```

### 3️⃣ 安装你的应用程序

```bash
# 安装你的应用（示例：tofu）
uv pip install tofu
# 或
pip install tofu
```

### 4️⃣ 构建 ROS2 包

```bash
# 加载 ROS2
source /opt/ros/humble/setup.bash

# 构建
colcon build --packages-select rostofu_bringup

# 加载工作空间
source install/setup.bash
```

### 5️⃣ 启动 🎉

```bash
ros2 launch rostofu_bringup copaw_launch.py
```

---

## 📖 使用方法

### 通过服务控制

```bash
# 启动 copaw
ros2 service call /start_copaw std_srvs/srv/Trigger

# 停止 copaw  
ros2 service call /stop_copaw std_srvs/srv/Trigger

# 重启 copaw
ros2 service call /restart_copaw std_srvs/srv/Trigger
```

### 监控状态

```bash
# 实时查看 copaw 状态
ros2 topic echo /copaw_status
```

### 不使用启动文件运行

```bash
# 直接运行节点
ros2 run rostofu_bringup copaw_node

# 指定自定义路径
ros2 run rostofu_bringup copaw_node --ros-args -p copaw_path:="/path/to/copaw"
```

---

## ⚙️ 配置

### 参数

| 参数 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `copaw_path` | string | `""` | copaw 可执行文件路径（留空则自动检测） |
| `working_directory` | string | `""` | 进程工作目录 |
| `auto_start` | bool | `true` | 节点启动时自动启动 |

### 使用自定义参数启动

```bash
# Linux
ros2 launch rostofu_bringup copaw_launch.py \
  copaw_path:="/home/user/RosTofu/.venv/bin/copaw" \
  auto_start:=true

# Windows
ros2 launch rostofu_bringup copaw_launch.py ^
  copaw_path:="D:\\RosTofu\\.venv\\Scripts\\copaw.exe" ^
  auto_start:=true
```

---

## 🏗️ 项目结构

```
RosTofu/
├── 📁 rostofu_bringup/          # ROS2 包
│   ├── 📁 launch/
│   │   └── copaw_launch.py      # 启动文件
│   ├── 📁 rostofu_bringup/
│   │   └── copaw_node.py        # 主节点实现
│   ├── package.xml              # ROS2 清单
│   └── setup.py                 # 包配置
├── 📄 pyproject.toml            # Python 项目配置
└── 📄 README.md                 # 英文文档
```

---

## 💻 平台支持

| 平台 | 状态 | ROS2 版本 |
|----------|--------|--------------|
| Ubuntu 22.04 | ✅ 完全支持 | Humble, Jazzy |
| Ubuntu 24.04 | ✅ 完全支持 | Jazzy |
| Windows 10/11 | ✅ 完全支持 | Humble |
| macOS | ⚠️ 未测试 | — |

---

## 🤝 贡献指南

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 许可证

基于 MIT 许可证分发。详见 [LICENSE](LICENSE)。

---

## 🙏 致谢

- [ROS2](https://docs.ros.org/) — 机器人操作系统
- [uv](https://docs.astral.sh/uv/) — 极速 Python 包管理器

---

<div align="center">

**[⬆ 返回顶部](#-rostofu)**

用 ❤️ 制作 by GWinfinity

</div>
