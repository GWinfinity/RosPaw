# RosTofu 快速发布指南

支持 ROS 2 发行版: **Humble** | **Jazzy**

## ⚡ 快速开始

### 1. 环境准备 (Ubuntu/ROS 环境)

```bash
# 安装 bloom
sudo apt-get update
sudo apt-get install python3-bloom python3-catkin-pkg

# 配置 git
export GITHUB_USER=GWinfinity
export GITHUB_TOKEN=your_token_here  # 需要 GitHub Personal Access Token
```

### 2. 创建 Release 仓库

访问 https://github.com/new 创建：
- **Repository name**: `rostofu_bringup-release`
- **Visibility**: Public
- **Initialize**: 不要勾选任何选项（创建空仓库）

### 3. 执行 Bloom 发布

#### 发布到 Humble

```bash
# 首次发布（创建新 track）
bloom-release --rosdistro humble --track humble rostofu_bringup --new-track

# 或后续更新（使用已有 track）
bloom-release --rosdistro humble --track humble rostofu_bringup
```

#### 发布到 Jazzy

```bash
# 首次发布（创建新 track）
bloom-release --rosdistro jazzy --track jazzy rostofu_bringup --new-track

# 或后续更新（使用已有 track）
bloom-release --rosdistro jazzy --track jazzy rostofu_bringup
```

### 4. bloom 交互式配置

首次运行会提示配置，按以下填写：

```
Repository Name: rostofu_bringup
Upstream Repository URI: https://github.com/GWinfinity/RosTofu.git
Release Repository Push URL: https://github.com/GWinfinity/rostofu_bringup-release.git
Upstream VCS Type: git
Version: :{auto}  (或手动输入 0.2.0)
Release Tag: :{version}
Upstream Devel Branch: main
ROS Distro: humble  # 或 jazzy
Patches Directory: (留空)
```

### 5. 提交 rosdistro PR

bloom 会自动打开浏览器创建 PR，如果没有：

#### Humble

1. Fork https://github.com/ros/rosdistro
2. 编辑 `humble/distribution.yaml`，在 `repositories:` 下添加（按字母顺序）：

```yaml
  rostofu_bringup:
    source:
      type: git
      url: https://github.com/GWinfinity/RosTofu.git
      version: main
    status: developed
```

#### Jazzy

1. Fork https://github.com/ros/rosdistro
2. 编辑 `jazzy/distribution.yaml`，在 `repositories:` 下添加（按字母顺序）：

```yaml
  rostofu_bringup:
    source:
      type: git
      url: https://github.com/GWinfinity/RosTofu.git
      version: main
    status: developed
```

3. 提交 PR，标题格式：
   ```
   rostofu_bringup: 0.2.0-1 in '<distro>/distribution.yaml' [bloom]
   ```

---

## 🔍 验证发布

### 检查 PR 状态
- 访问：https://github.com/ros/rosdistro/pulls?q=is%3Apr+rostofu_bringup

### 检查构建状态

**Humble:** http://repo.ros2.org/status_page/ros_humble_default.html

**Jazzy:** http://repo.ros2.org/status_page/ros_jazzy_default.html

### 检查索引
- 访问：https://index.ros.org/p/rostofu_bringup/

---

## 📦 用户使用

发布后用户可通过以下方式安装：

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

## 🐛 故障排除

### 依赖问题
```bash
# 检查 rosdep 键
rosdep resolve python3-aiohttp
```

### bloom 权限问题
```bash
# 配置 GitHub Token
export BLOOM_GITHUB_TOKEN=your_token_here
```

### 版本号冲突
确保以下文件版本一致：
- package.xml: `<version>0.2.0</version>`
- setup.py: `version='0.2.0'`
- Git tag: `git tag 0.2.0 && git push origin 0.2.0`

---

## 📚 参考链接

- [ROS Humble 发布文档](https://docs.ros.org/en/humble/How-To-Guides/Releasing/Releasing-a-Package.html)
- [ROS 2 Jazzy 发布文档](https://docs.ros.org/en/jazzy/How-To-Guides/Releasing/Releasing-a-Package.html)
- [Bloom 文档](https://bloom.readthedocs.io/)
- [rosdistro 贡献指南](https://github.com/ros/rosdistro/blob/master/CONTRIBUTING.md)
