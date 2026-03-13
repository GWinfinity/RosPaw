# rospaw_bringup

ROS2 包，用于封装和启动 copaw 应用程序。
支持 Windows 和 Linux/Ubuntu 双平台。

## 目录结构

```
rospaw_bringup/
├── package.xml          # ROS2 包描述
├── setup.py             # Python 包配置
├── README.md            # 本文件
├── launch/
│   └── copaw_launch.py  # Launch 文件
├── resource/
│   └── rospaw_bringup   # 资源标记文件
└── rospaw_bringup/
    ├── __init__.py
    └── copaw_node.py    # 主要的 ROS2 节点
```

## 使用步骤

### 1. 激活 ROS2 环境

**Windows (PowerShell):**
```powershell
# 根据你的 ROS2 安装路径
& C:\opt\ros\humble\local_setup.ps1
# 或
& C:\opt\ros\jazzy\local_setup.ps1
```

**Linux/Ubuntu (Bash):**
```bash
# 根据你的 ROS2 版本
source /opt/ros/humble/setup.bash
# 或
source /opt/ros/jazzy/setup.bash
```

### 2. 构建包

**Windows:**
```powershell
cd D:\githbi\RosPaw
colcon build --packages-select rospaw_bringup
```

**Linux/Ubuntu:**
```bash
cd ~/RosPaw  # 或你的项目路径
colcon build --packages-select rospaw_bringup
```

### 3. 激活工作空间

**Windows:**
```powershell
.\install\local_setup.ps1
```

**Linux/Ubuntu:**
```bash
source install/setup.bash
```

### 4. 启动 copaw 服务

**方法1：使用 ros2 run**

**Windows:**
```powershell
ros2 run rospaw_bringup copaw_node
```

**Linux/Ubuntu:**
```bash
ros2 run rospaw_bringup copaw_node
```

**方法2：使用 launch 文件**

**Windows:**
```powershell
ros2 launch rospaw_bringup copaw_launch.py
```

**Linux/Ubuntu:**
```bash
ros2 launch rospaw_bringup copaw_launch.py
```

**指定参数启动：**

**Windows:**
```powershell
ros2 launch rospaw_bringup copaw_launch.py copaw_path:="D:\\githbi\\RosPaw\\.venv\\Scripts\\copaw.exe"
```

**Linux/Ubuntu:**
```bash
ros2 launch rospaw_bringup copaw_launch.py copaw_path:="/home/username/RosPaw/.venv/bin/copaw"
```

## 服务接口

启动节点后，可以使用以下 ROS2 服务控制 copaw：

```bash
# 启动 copaw
ros2 service call /start_copaw std_srvs/srv/Trigger

# 停止 copaw
ros2 service call /stop_copaw std_srvs/srv/Trigger

# 重启 copaw
ros2 service call /restart_copaw std_srvs/srv/Trigger
```

## 话题

- `/copaw_status` (std_msgs/String): 发布 copaw 的运行状态

```bash
# 查看状态
ros2 topic echo /copaw_status
```

## 参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `copaw_path` | string | `""` | copaw 可执行文件的路径，留空则自动检测 |
| `working_directory` | string | `""` | copaw 工作目录 |
| `auto_start` | bool | `true` | 节点启动时自动启动 copaw |

## 可执行文件路径

包会自动检测以下位置的 copaw 可执行文件：

**Windows:**
- `.venv\Scripts\copaw.exe`
- `venv\Scripts\copaw.exe`
- PATH 环境变量中的 `copaw`

**Linux/Ubuntu:**
- `.venv/bin/copaw`
- `venv/bin/copaw`
- `~/RosPaw/.venv/bin/copaw`
- `/opt/rospaw/.venv/bin/copaw`
- PATH 环境变量中的 `copaw`

如果无法自动检测到，请通过参数 `copaw_path` 显式指定。

## 注意事项

1. **ROS2 环境**：确保 ROS2 已正确安装和配置
2. **copaw 可执行文件**：必须在虚拟环境中可用或存在于 PATH 中
3. **权限**：在 Linux 上，确保 copaw 有执行权限 (`chmod +x copaw`)
4. **进程管理**：
   - Windows：使用进程组管理
   - Linux：使用进程组和会话管理，支持优雅关闭
