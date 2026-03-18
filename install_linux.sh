#!/bin/bash
#===============================================================================
# RosPaw Linux 一键安装脚本
# 
# Usage:
#   ./install_linux.sh              # 完整安装
#   ./install_linux.sh --minimal    # 最小安装 (无语音)
#   ./install_linux.sh --dev        # 开发环境
#===============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_command() {
    if ! command -v $1 &> /dev/null; then
        return 1
    fi
    return 0
}

install_ros2() {
    print_info "Checking ROS2 installation..."
    
    if [ -d "/opt/ros" ]; then
        print_success "ROS2 found"
        ls /opt/ros/
        return 0
    fi
    
    print_warning "ROS2 not found. Installing ROS2 Humble..."
    
    # Update locale
    sudo apt update && sudo apt install -y locales
    sudo locale-gen en_US en_US.UTF-8
    sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
    export LANG=en_US.UTF-8
    
    # Setup sources
    sudo apt install -y software-properties-common
    sudo add-apt-repository universe
    sudo apt update
    
    # Add ROS2 repo
    sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
    
    # Install ROS2
    sudo apt update
    sudo apt install -y ros-humble-desktop ros-dev-tools
    
    # Setup environment
    echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
    source /opt/ros/humble/setup.bash
    
    print_success "ROS2 Humble installed"
}

install_system_deps() {
    print_info "Installing system dependencies..."
    
    sudo apt update
    sudo apt install -y \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        portaudio19-dev \
        libffi-dev \
        libssl-dev \
        git \
        wget \
        curl \
        alsa-utils \
        sox \
        libsox-fmt-all
    
    print_success "System dependencies installed"
}

install_ollama() {
    print_info "Installing Ollama (Local LLM)..."
    
    if check_command ollama; then
        print_success "Ollama already installed"
    else
        curl -fsSL https://ollama.com/install.sh | sh
        print_success "Ollama installed"
    fi
    
    # Pull default model
    print_info "Pulling default model (qwen2.5:7b)..."
    ollama pull qwen2.5:7b
    
    print_success "Ollama ready"
}

setup_venv() {
    print_info "Setting up Python virtual environment..."
    
    cd "$SCRIPT_DIR"
    
    if [ -d ".venv" ]; then
        print_warning "Virtual environment exists, skipping creation"
    else
        python3 -m venv .venv
        print_success "Virtual environment created"
    fi
    
    source .venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements-nl.txt" ]; then
        pip install -r requirements-nl.txt
    else
        # Install basic dependencies
        pip install aiohttp
    fi
    
    # Install copaw
    if ! check_command copaw; then
        pip install copaw
    fi
    
    print_success "Python environment ready"
}

build_ros2_package() {
    print_info "Building ROS2 package..."
    
    cd "$SCRIPT_DIR"
    source /opt/ros/humble/setup.bash 2>/dev/null || source /opt/ros/jazzy/setup.bash
    
    # Build
    colcon build --packages-select rostofu_bringup --symlink-install
    
    # Source the workspace
    source install/setup.bash
    
    # Add to .bashrc if not already there
    if ! grep -q "rostofu_bringup" ~/.bashrc; then
        echo "source $SCRIPT_DIR/install/setup.bash" >> ~/.bashrc
    fi
    
    print_success "ROS2 package built"
}

setup_permissions() {
    print_info "Setting up permissions..."
    
    # Serial port permissions
    sudo usermod -aG dialout $USER 2>/dev/null || true
    
    # Audio permissions
    sudo usermod -aG audio $USER 2>/dev/null || true
    
    print_success "Permissions configured (logout and login to apply)"
}

print_summary() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                  Installation Complete!                       ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Quick Start:"
    echo "  1. Logout and login again (for permission changes)"
    echo "  2. cd $SCRIPT_DIR"
    echo "  3. ./start_nl_mode.sh"
    echo ""
    echo "Manual Start:"
    echo "  source /opt/ros/humble/setup.bash"
    echo "  source $SCRIPT_DIR/install/setup.bash"
    echo "  ros2 launch rostofu_bringup rospaw_nl_launch.py"
    echo ""
    echo "Documentation:"
    echo "  NL Control:    $SCRIPT_DIR/NL_CONTROL.md"
    echo "  Linux Advantages: $SCRIPT_DIR/LINUX_ADVANTAGES.md"
    echo ""
}

# Main
main() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║              RosPaw Linux Installer                           ║"
    echo "║        ROS2 × Natural Language × Linux Native                 ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    local minimal=false
    local dev=false
    
    for arg in "$@"; do
        case $arg in
            --minimal) minimal=true ;;
            --dev) dev=true ;;
        esac
    done
    
    print_info "Starting installation..."
    print_info "Mode: $(if $minimal; then echo "minimal"; elif $dev; then echo "development"; else echo "full"; fi)"
    
    # Install steps
    install_system_deps
    install_ros2
    
    if ! $minimal; then
        install_ollama
    fi
    
    setup_venv
    build_ros2_package
    setup_permissions
    
    print_summary
}

main "$@"
