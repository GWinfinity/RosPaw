<div align="center">

# 🧊 RosTofu

**ROS2 × copaw — Your Application in Robotics World**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ROS2](https://img.shields.io/badge/ROS2-Humble%20%7C%20Jazzy-blue.svg)](https://docs.ros.org/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey.svg)]()

[English](README.md) | [中文](README_CN.md)

</div>

---

## 🤔 What is RosTofu?

**RosTofu** bridges the gap between your application and the robotics world through ROS2. It wraps any executable as a ROS2 node, enabling you to:

- 🚀 **Launch & Control** — Start/stop/restart your app via ROS2 services
- 📊 **Monitor Status** — Real-time status publishing on ROS2 topics  
- 🔗 **ROS2 Integration** — Seamlessly integrate your app into your robotics stack
- 🖥️ **Cross-Platform** — Works on both Windows and Ubuntu

Whether you're building a smart robot application or integrating software into your ROS2 workflow, RosTofu provides the bridge you need.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎛️ **Service Interface** | Control copaw via `/start_copaw`, `/stop_copaw`, `/restart_copaw` services |
| 📡 **Status Monitoring** | Track copaw state via `/copaw_status` topic |
| 🔍 **Auto-Detection** | Automatically finds executable in `.venv` or system PATH |
| ⚡ **Launch Files** | Ready-to-use ROS2 launch configurations |
| 🐧 **Multi-Platform** | Native support for Windows and Linux |

---

## 🚀 Quick Start

### Prerequisites

- [ROS2 Humble](https://docs.ros.org/en/humble/Installation.html) or [Jazzy](https://docs.ros.org/en/jazzy/Installation.html)
- [Python](https://www.python.org/) 3.9+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### 1️⃣ Clone & Setup

```bash
git clone git@github.com:GWinfinity/RosTofu.git
cd RosTofu
```

### 2️⃣ Create Virtual Environment

```bash
# Using uv (recommended)
uv venv

# Activate
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

### 3️⃣ Install Your Application

```bash
# Install your application (example: copaw)
uv pip install copaw
# or
pip install copaw
```

### 4️⃣ Build ROS2 Package

```bash
# Source ROS2
source /opt/ros/humble/setup.bash

# Build
colcon build --packages-select rostofu_bringup

# Source workspace
source install/setup.bash
```

### 5️⃣ Launch 🎉

```bash
ros2 launch rostofu_bringup copaw_launch.py
```

---

## 📖 Usage

### Control via Services

```bash
# Start copaw
ros2 service call /start_copaw std_srvs/srv/Trigger

# Stop copaw  
ros2 service call /stop_copaw std_srvs/srv/Trigger

# Restart copaw
ros2 service call /restart_copaw std_srvs/srv/Trigger
```

### Monitor Status

```bash
# Watch copaw status in real-time
ros2 topic echo /copaw_status
```

### Run without Launch File

```bash
# Direct node execution
ros2 run rostofu_bringup copaw_node

# With custom path
ros2 run rostofu_bringup copaw_node --ros-args -p copaw_path:="/path/to/copaw"
```

---

## ⚙️ Configuration

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `copaw_path` | string | `""` | Path to copaw executable (auto-detected if empty) |
| `working_directory` | string | `""` | Working directory for the process |
| `auto_start` | bool | `true` | Auto-start when node launches |

### Launch with Custom Parameters

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

## 🏗️ Project Structure

```
RosTofu/
├── 📁 rostofu_bringup/          # ROS2 package
│   ├── 📁 launch/
│   │   └── copaw_launch.py      # Launch file
│   ├── 📁 rostofu_bringup/
│   │   └── copaw_node.py        # Main node implementation
│   ├── package.xml              # ROS2 manifest
│   └── setup.py                 # Package setup
├── 📄 pyproject.toml            # Python project config
└── 📄 README.md                 # This file
```

---

## 💻 Platform Support

| Platform | Status | ROS2 Version |
|----------|--------|--------------|
| Ubuntu 22.04 | ✅ Fully Supported | Humble, Jazzy |
| Ubuntu 24.04 | ✅ Fully Supported | Jazzy |
| Windows 10/11 | ✅ Fully Supported | Humble |
| macOS | ⚠️ Not Tested | — |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

---

## 🙏 Acknowledgments

- [ROS2](https://docs.ros.org/) — Robot Operating System
- [uv](https://docs.astral.sh/uv/) — Fast Python package manager

---

<div align="center">

**[⬆ Back to Top](#-rostofu)**

Made with ❤️ by GWinfinity

</div>
