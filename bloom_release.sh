#!/bin/bash
# RosTofu Bloom 发布脚本
# 支持 ROS 2 Humble 和 Jazzy

set -e

# 配置
PACKAGE_NAME="rostofu_bringup"
SOURCE_URL="https://github.com/GWinfinity/RosTofu.git"
RELEASE_URL="https://github.com/GWinfinity/rostofu_bringup-release.git"

echo "========================================"
echo "  RosTofu Bloom 发布脚本"
echo "  支持发行版: humble, jazzy"
echo "========================================"
echo ""

# 检查 bloom 是否安装
if ! command -v bloom-release &> /dev/null; then
    echo "❌ bloom 未安装，请先安装:"
    echo "   sudo apt-get install python3-bloom"
    exit 1
fi

echo "✓ bloom 已安装"

# 检查 git 配置
if [ -z "$(git config --global user.name)" ] || [ -z "$(git config --global user.email)" ]; then
    echo "❌ git 用户配置不完整，请先配置:"
    echo "   git config --global user.name 'Your Name'"
    echo "   git config --global user.email 'your@email.com'"
    exit 1
fi

echo "✓ git 配置正确"

# 选择发行版
echo ""
echo "请选择要发布的 ROS 2 发行版:"
echo "1) humble (LTS, 推荐)"
echo "2) jazzy"
echo "3) 同时发布到 humble 和 jazzy"
echo ""
read -p "请输入选项 (1/2/3): " choice

case $choice in
    1)
        DISTROS=("humble")
        ;;
    2)
        DISTROS=("jazzy")
        ;;
    3)
        DISTROS=("humble" "jazzy")
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

# 检查当前目录
cd rostofu_bringup

# 检查 package.xml
if [ ! -f "package.xml" ]; then
    echo "❌ package.xml 不存在"
    exit 1
fi

echo "✓ package.xml 存在"

# 获取版本号
VERSION=$(grep -oP '(?<=<version>)[^<]+' package.xml)
echo "📦 包版本: $VERSION"

# 检查 setup.py 版本是否一致
if [ -f "setup.py" ]; then
    SETUP_VERSION=$(grep -oP "(?<=version=')[^']+" setup.py)
    if [ "$VERSION" != "$SETUP_VERSION" ]; then
        echo "⚠️ 警告: package.xml 版本 ($VERSION) 与 setup.py 版本 ($SETUP_VERSION) 不一致"
        echo "   请统一版本号后再发布"
        exit 1
    fi
    echo "✓ 版本号一致"
fi

cd ..

echo ""
echo "========================================"
echo "  开始 Bloom 发布流程"
echo "========================================"
echo ""

# 检查是否有现有 track
for DISTRO in "${DISTROS[@]}"; do
    echo ""
    echo "📦 处理发行版: $DISTRO"
    echo "----------------------------------------"
    
    if bloom-release "$DISTRO" --list-tracks 2>/dev/null | grep -q "^${PACKAGE_NAME}$"; then
        echo "✓ 已存在 track，执行更新发布"
        bloom-release --rosdistro "$DISTRO" --track "$DISTRO" "$PACKAGE_NAME"
    else
        echo "🆕 未找到 track，创建新 track"
        
        if [ "$DISTRO" == "humble" ]; then
            echo "提示: Humble 是 LTS 版本，推荐作为默认目标"
        fi
        
        bloom-release --rosdistro "$DISTRO" --track "$DISTRO" "$PACKAGE_NAME" --new-track
    fi
    
    if [ $? -eq 0 ]; then
        echo "✓ $DISTRO 发布成功"
    else
        echo "❌ $DISTRO 发布失败"
        exit 1
    fi
done

echo ""
echo "========================================"
echo "  发布完成！"
echo "========================================"
echo ""
echo "后续步骤:"
echo "1. 检查生成的 PR: https://github.com/ros/rosdistro/pulls"
echo "2. 等待 ROS Boss 审核"
echo ""
echo "构建状态:"
for DISTRO in "${DISTROS[@]}"; do
    echo "  - $DISTRO: http://repo.ros2.org/status_page/ros_${DISTRO}_default.html"
done
echo ""
