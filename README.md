# RosPaw

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ROS2 封装包 for [copaw](https://github.com/copilot-extensions/copaw) - 将 copaw 应用程序集成到 ROS2 生态系统中。

## 项目简介

RosPaw 是一个 ROS2 包，用于在 ROS2 环境中启动和管理 copaw 应用程序。它提供了：

- 🤖 **ROS2 节点封装** - 将 copaw 作为 ROS2 节点运行
- 🎛️ **服务接口** - 通过 ROS2 服务控制 copaw (启动/停止/重启)
- 📡 **状态监控** - 实时发布 copaw 运行状态
- 🖥️ **跨平台支持** - 支持 Windows 和 Linux/Ubuntu

## 目录结构

```
RosPaw/
├── .venv/                    # Python 虚拟环境 (不推送到 git)
├── .gitignore               # Git 忽略配置
├── pyproject.toml           # Python 项目配置
├── main.py                  # 示例入口文件
├── README.md                # 本文件
└── rospaw_bringup/          # ROS2 包
    ├── package.xml          # ROS2 包描述
    ├── setup.py             # Python 包配置
    ├── README.md            # ROS2 包使用说明
    ├── launch/
    │   └── copaw_launch.py  # Launch 文件
    ├── resource/
    │   └── rospaw_bringup   # 资源标记文件
    └── rospaw_bringup/
        ├── __init__.py
        └── copaw_node.py    # 主要的 ROS2 节点
```

## 快速开始

### 1. 克隆仓库

```bash
git clone git@github.com:GWinfinity/RosPaw.git
cd RosPaw
```

### 2. 创建虚拟环境并安装 copaw

本项目使用 [uv](https://docs.astral.sh/uv/) 进行 Python 环境管理：

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 安装 copaw (如果 copaw 在 PyPI 上)
uv pip install copaw

# 或从源码安装 copaw
git clone https://github.com/copilot-extensions/copaw.git
cd copaw
uv pip install -e .
```

### 3. 安装 ROS2 依赖

确保系统已安装 ROS2 (Humble 或 Jazzy)：

```bash
# Ubuntu
sudo apt install ros-humble-desktop
# 或
sudo apt install ros-jazzy-desktop
```

### 4. 构建 ROS2 包

```bash
# 激活 ROS2 环境
source /opt/ros/humble/setup.bash

# 构建包
colcon build --packages-select rospaw_bringup

# 激活工作空间
source install/setup.bash
```

### 5. 启动服务

```bash
# 使用 launch 文件启动
ros2 launch rospaw_bringup copaw_launch.py
```

## 使用方法

### 启动/停止/重启 copaw

```bash
# 启动 copaw
ros2 service call /start_copaw std_srvs/srv/Trigger

# 停止 copaw
ros2 service call /stop_copaw std_srvs/srv/Trigger

# 重启 copaw
ros2 service call /restart_copaw std_srvs/srv/Trigger
```

### 查看运行状态

```bash
# 查看 copaw 状态
ros2 topic echo /copaw_status
```

### 可选参数

```bash
# 指定 copaw 路径
ros2 launch rospaw_bringup copaw_launch.py copaw_path:="/path/to/copaw"

# 禁用自动启动
ros2 launch rospaw_bringup copaw_launch.py auto_start:=false
```

## 开发指南

### 项目配置

`pyproject.toml` 包含项目元数据：

```toml
[project]
name = "rospaw"
version = "0.1.0"
description = "ROS2 package for copaw application"
requires-python = ">=3.9"
```

### 添加依赖

```bash
# 添加到 pyproject.toml
uv add <package-name>

# 或手动编辑 pyproject.toml 后同步
uv pip sync
```

### 本地测试

```bash
# 运行节点
ros2 run rospaw_bringup copaw_node

# 查看日志
ros2 node info /copaw_node
```

## 平台支持

| 平台 | 状态 | 说明 |
|------|------|------|
| Windows | ✅ 支持 | PowerShell, cmd.exe |
| Ubuntu | ✅ 支持 | 20.04, 22.04, 24.04 |
| macOS | ⚠️ 未测试 | 理论上支持 |

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

- [copaw](https://github.com/copilot-extensions/copaw) - GitHub Copilot 扩展框架
- [ROS2](https://docs.ros.org/) - 机器人操作系统
- [uv](https://docs.astral.sh/uv/) - 极速 Python 包管理器

## 联系方式

- 项目主页: https://github.com/GWinfinity/RosPaw
- Issue 追踪: https://github.com/GWinfinity/RosPaw/issues
