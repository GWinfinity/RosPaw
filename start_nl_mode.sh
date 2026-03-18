#!/bin/bash
#===============================================================================
# RosPaw NL Mode Launcher for Linux
# 自然语言控制模式启动脚本 (Linux/macOS/ROS2原生环境)
#
# Usage:
#   ./start_nl_mode.sh              # 交互式选择模式
#   ./start_nl_mode.sh --basic      # 基础 NL 模式 (Ollama)
#   ./start_nl_mode.sh --cloud      # 云端 NL 模式
#   ./start_nl_mode.sh --full       # 完整模式 (NL + 语音)
#   ./start_nl_mode.sh --copaw      # 仅 Copaw 模式
#===============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COXIAHUA_HOME="$SCRIPT_DIR"

# Functions
print_header() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                  RosPaw NL Mode Launcher                      ║"
    echo "║          ROS2 × Natural Language × Linux Native               ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_ros2() {
    if [ -z "$ROS_DISTRO" ]; then
        print_warning "ROS2 environment not sourced"
        
        # Try common ROS2 installation paths
        if [ -f "/opt/ros/humble/setup.bash" ]; then
            print_info "Sourcing ROS2 Humble..."
            source /opt/ros/humble/setup.bash
        elif [ -f "/opt/ros/jazzy/setup.bash" ]; then
            print_info "Sourcing ROS2 Jazzy..."
            source /opt/ros/jazzy/setup.bash
        elif [ -f "/opt/ros/iron/setup.bash" ]; then
            print_info "Sourcing ROS2 Iron..."
            source /opt/ros/iron/setup.bash
        else
            print_error "ROS2 installation not found. Please source ROS2 manually:"
            echo "  source /opt/ros/<distro>/setup.bash"
            exit 1
        fi
    fi
    
    print_success "ROS2 $ROS_DISTRO detected"
}

check_venv() {
    if [ ! -f "$COXIAHUA_HOME/.venv/bin/python" ]; then
        print_error "Virtual environment not found at $COXIAHUA_HOME/.venv"
        echo "Please create venv first:"
        echo "  cd $COXIAHUA_HOME && python3 -m venv .venv"
        exit 1
    fi
    
    print_success "Virtual environment found"
}

check_copaw() {
    if [ ! -f "$COXIAHUA_HOME/.venv/bin/copaw" ]; then
        print_warning "copaw not found in venv, attempting to install..."
        "$COXIAHUA_HOME/.venv/bin/pip" install copaw
    fi
    
    print_success "copaw ready"
}

check_ollama() {
    if ! command -v ollama &> /dev/null; then
        print_warning "Ollama not installed"
        echo "Install from: https://ollama.com/download"
        echo "Or run: curl -fsSL https://ollama.com/install.sh | sh"
        return 1
    fi
    
    # Check if model is available
    if ! ollama list | grep -q "qwen2.5"; then
        print_info "Pulling Ollama model (qwen2.5:7b)..."
        ollama pull qwen2.5:7b
    fi
    
    print_success "Ollama ready"
}

start_copaw() {
    print_info "Starting Copaw..."
    
    # Start copaw in background
    "$COXIAHUA_HOME/.venv/bin/copaw" &
    COPAW_PID=$!
    
    # Wait for copaw to initialize
    sleep 3
    
    if ps -p $COPAW_PID > /dev/null; then
        print_success "Copaw started (PID: $COPAW_PID)"
        echo $COPAW_PID > /tmp/rospaw_copaw.pid
    else
        print_error "Failed to start Copaw"
        exit 1
    fi
}

stop_copaw() {
    if [ -f /tmp/rospaw_copaw.pid ]; then
        PID=$(cat /tmp/rospaw_copaw.pid)
        if ps -p $PID > /dev/null 2>&1; then
            print_info "Stopping Copaw (PID: $PID)..."
            kill $PID 2>/dev/null || true
            rm -f /tmp/rospaw_copaw.pid
        fi
    fi
}

cleanup() {
    print_warning "Shutting down..."
    stop_copaw
    exit 0
}

# Trap signals for cleanup
trap cleanup SIGINT SIGTERM

mode_basic() {
    print_header
    check_ros2
    check_venv
    check_copaw
    check_ollama || print_warning "Ollama not available, will use fallback"
    
    # Source workspace
    if [ -f "$COXIAHUA_HOME/install/setup.bash" ]; then
        source "$COXIAHUA_HOME/install/setup.bash"
    fi
    
    print_info "Starting Basic NL Mode (Ollama)..."
    print_info "Features:"
    echo "  • Local LLM (Ollama)"
    echo "  • Text-based NL control"
    echo "  • Copaw integration"
    echo ""
    
    # Start Copaw
    start_copaw
    
    print_success "Starting NL Commander..."
    print_info "You can now send commands via:"
    echo "  ros2 topic pub /nl_command std_msgs/msg/String '{data: \"go to kitchen\"}'"
    echo "  ./rostofu_cli.py \"go to kitchen\""
    echo ""
    
    # Start NL Commander
    ros2 run rostofu_bringup nl_commander_node \
        --ros-args \
        -p llm_provider:=ollama \
        -p ollama_model:=qwen2.5:7b \
        -p copaw_enabled:=true \
        -p copaw_auto_start:=false
}

mode_cloud() {
    print_header
    check_ros2
    check_venv
    check_copaw
    
    # Source workspace
    if [ -f "$COXIAHUA_HOME/install/setup.bash" ]; then
        source "$COXIAHUA_HOME/install/setup.bash"
    fi
    
    echo ""
    echo "Select Cloud LLM Provider:"
    echo "  [1] Alibaba DashScope (recommended for CN users)"
    echo "  [2] OpenAI"
    echo "  [3] Zhipu AI"
    echo ""
    read -p "Choose [1-3]: " cloud_choice
    
    case $cloud_choice in
        1) PROVIDER="dashscope"; MODEL="qwen-turbo" ;;
        2) PROVIDER="openai"; MODEL="gpt-3.5-turbo" ;;
        3) PROVIDER="zhipu"; MODEL="glm-4" ;;
        *) PROVIDER="dashscope"; MODEL="qwen-turbo" ;;
    esac
    
    read -sp "Enter API Key: " API_KEY
    echo ""
    
    if [ -z "$API_KEY" ]; then
        print_error "API Key is required for cloud mode"
        exit 1
    fi
    
    print_info "Starting Cloud NL Mode ($PROVIDER)..."
    
    # Start Copaw
    start_copaw
    
    # Start NL Commander
    ros2 run rostofu_bringup nl_commander_node \
        --ros-args \
        -p llm_provider:=$PROVIDER \
        -p ${PROVIDER}_api_key:=$API_KEY \
        -p ${PROVIDER}_model:=$MODEL \
        -p copaw_enabled:=true \
        -p copaw_auto_start:=false
}

mode_full() {
    print_header
    check_ros2
    check_venv
    check_copaw
    check_ollama || print_warning "Ollama not available"
    
    # Source workspace
    if [ -f "$COXIAHUA_HOME/install/setup.bash" ]; then
        source "$COXIAHUA_HOME/install/setup.bash"
    fi
    
    print_info "Starting Full NL Mode (NL + Voice)..."
    print_info "Features:"
    echo "  • Voice input with wake word"
    echo "  • Text-to-speech response"
    echo "  • Local LLM (Ollama)"
    echo "  • Copaw integration"
    echo ""
    
    # Check voice dependencies
    if ! python3 -c "import whisper" 2>/dev/null; then
        print_warning "Whisper not installed. Install with: pip install openai-whisper"
    fi
    
    # Start Copaw
    start_copaw
    
    # Start NL Commander in background
    print_info "Starting NL Commander..."
    ros2 run rostofu_bringup nl_commander_node \
        --ros-args \
        -p llm_provider:=ollama \
        -p ollama_model:=qwen2.5:7b \
        -p tts_enabled:=true \
        -p copaw_enabled:=true \
        -p copaw_auto_start:=false &
    
    NL_PID=$!
    sleep 2
    
    # Start Voice Input
    print_info "Starting Voice Input..."
    print_info "Wake word: '你好机器人' ( configurable )"
    ros2 run rostofu_bringup voice_input_node \
        --ros-args \
        -p enabled:=true \
        -p wake_word:="你好机器人"
    
    # Cleanup
    kill $NL_PID 2>/dev/null || true
}

mode_copaw_only() {
    print_header
    check_venv
    check_copaw
    
    print_info "Starting Copaw only (no NL control)..."
    print_info "Copaw will run in foreground. Press Ctrl+C to stop."
    echo ""
    
    "$COXIAHUA_HOME/.venv/bin/copaw"
}

show_interactive_menu() {
    print_header
    
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║  Why RosPaw on Linux?                                         ║"
    echo "║  • Native ROS2 DDS performance                               ║"
    echo "║  • Real-time kernel support                                  ║"
    echo "║  • Better process management                                 ║"
    echo "║  • Native copaw integration                                  ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    
    echo "Select Launch Mode:"
    echo ""
    echo "  [1] 🏠 Basic NL Mode      - Local LLM (Ollama), Text control"
    echo "  [2] ☁️  Cloud NL Mode     - Cloud LLM (DashScope/OpenAI)"
    echo "  [3] 🎙️  Full NL Mode      - Voice + TTS + NL (Requires mic)"
    echo "  [4] 🤖 Copaw Only         - No NL, just Copaw"
    echo ""
    echo "  [q] Quit"
    echo ""
    
    read -p "Select [1-4,q]: " choice
    
    case $choice in
        1) mode_basic ;;
        2) mode_cloud ;;
        3) mode_full ;;
        4) mode_copaw_only ;;
        q|Q) exit 0 ;;
        *) 
            print_error "Invalid choice"
            exit 1
            ;;
    esac
}

show_help() {
    cat << EOF
RosPaw NL Mode Launcher for Linux

Usage: $0 [OPTION]

Options:
    --basic         Start Basic NL Mode (Ollama local LLM)
    --cloud         Start Cloud NL Mode (requires API key)
    --full          Start Full Mode (NL + Voice + TTS)
    --copaw         Start Copaw only (no NL control)
    --help          Show this help message

Environment:
    ROS_DISTRO      Automatically detected (humble/jazzy/iron)
    OLLAMA_HOST     Default: http://localhost:11434

Examples:
    $0                      # Interactive mode
    $0 --basic              # Basic mode with Ollama
    $0 --cloud              # Cloud mode with API key prompt
    $0 --full               # Full voice-enabled mode

For more info: https://github.com/yourname/RosPaw
EOF
}

# Main
main() {
    case "${1:-}" in
        --basic) mode_basic ;;
        --cloud) mode_cloud ;;
        --full) mode_full ;;
        --copaw) mode_copaw_only ;;
        --help|-h) show_help ;;
        "") show_interactive_menu ;;
        *) 
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
