# RosTofu 安装指南

支持 ROS 2 发行版: **Humble** | **Jazzy**

## 依赖说明

本包提供 ROS2 与 copaw AI 助手的集成，但**不包含 copaw 本身**。

### 依赖清单

| 依赖 | 安装方式 | 说明 |
|------|----------|------|
| ROS2 Humble/Jazzy | apt | ROS2 运行环境 |
| copaw | pip | AI 助手核心 (需单独安装) |
| aiohttp | pip/ rosdep | HTTP 客户端 |

---

## 安装步骤

### 1. 安装 ROS2

#### Humble (Ubuntu 22.04)
```bash
# 按照官方文档安装
# https://docs.ros.org/en/humble/Installation.html
```

#### Jazzy (Ubuntu 24.04)
```bash
# 按照官方文档安装
# https://docs.ros.org/en/jazzy/Installation.html
```

### 2. 安装 copaw (重要)

```bash
# 创建虚拟环境（推荐）
python3 -m venv ~/.copaw_env
source ~/.copaw_env/bin/activate

# 安装 copaw
pip install copaw

# 初始化 copaw
copaw init --defaults
```

### 3. 安装 rostofu_bringup

#### 从源码安装（当前）

```bash
# 创建工作空间
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/GWinfinity/RosTofu.git

# 安装依赖
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -y

# 编译
colcon build --packages-select rostofu_bringup

# source
source install/setup.bash
```

#### 从 apt 安装（发布后）

**Humble:**
```bash
sudo apt update
sudo apt install ros-humble-rostofu-bringup
```

**Jazzy:**
```bash
sudo apt update
sudo apt install ros-jazzy-rostofu-bringup
```

---

## 配置

### 配置 copaw 路径

编辑 `~/ros2_ws/src/RosTofu/rostofu_bringup/config/rospaw_nl.yaml`:

```yaml
rostofu_bringup:
  ros__parameters:
    copaw_executable: "/home/username/.copaw_env/bin/copaw"
    copaw_working_dir: "/home/username/.copaw"
    api_host: "127.0.0.1"
    api_port: 8088
    auto_start: true
```

### 启动

```bash
# 启动 copaw + ROS2 桥接
ros2 launch rostofu_bringup copaw_launch.py

# 或仅启动自然语言控制
ros2 launch rostofu_bringup rospaw_nl_launch.py
```

---

## 故障排除

### copaw 未找到
```bash
# 检查 copaw 安装
which copaw

# 如果没有，激活虚拟环境后添加 PATH
export PATH="$HOME/.copaw_env/bin:$PATH"
```

### API 连接失败
```bash
# 检查 copaw 是否运行
curl http://127.0.0.1:8088/api/health

# 手动启动 copaw
copaw app
```

---

## 关于 ROS 二进制包限制

由于 copaw 只能通过 pip 安装（不在 Ubuntu apt 仓库中），rostofu_bringup 的二进制 deb 包**不会自动安装 copaw**。

用户必须手动安装 copaw，这是当前架构的限制。

未来可能：
1. 将 copaw 打包为 snap/flatpak
2. 提供包含 copaw 的 Docker 镜像
3. 将 copaw 核心功能嵌入本包
