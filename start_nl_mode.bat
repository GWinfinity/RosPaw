@echo off
chcp 65001 >nul
title RosPaw NL Mode
cd /d "%~dp0"

echo ╔═══════════════════════════════════════════════════════════╗
echo ║                    RosPaw NL 模式启动器                    ║
echo ║              自然语言控制 + Copaw AI 助手                  ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

:: 检查虚拟环境
if not exist ".venv\Scripts\python.exe" (
    echo [错误] 虚拟环境不存在，请先运行安装脚本
    pause
    exit /b 1
)

:: 检查 ROS2 环境
if not defined ROS_DISTRO (
    echo [提示] ROS2 环境未加载，尝试自动加载...
    if exist "C:\dev\ros2_humble\local_setup.bat" (
        call "C:\dev\ros2_humble\local_setup.bat"
    ) else if exist "C:\opt\ros\humble\local_setup.bat" (
        call "C:\opt\ros\humble\local_setup.bat"
    ) else (
        echo [警告] 未找到 ROS2 环境，请手动 source ROS2
    )
)

:: 选择启动模式
echo 请选择启动模式:
echo   [1] 基础 NL 模式 (Ollama 本地 LLM)
echo   [2] 云端 NL 模式 (需要配置 API Key)
echo   [3] 完整模式 (NL + 语音输入)
echo   [4] 仅 Copaw (无自然语言控制)
echo.

set /p choice="选择 [1-4]: "

if "%choice%"=="1" goto basic
if "%choice%"=="2" goto cloud
if "%choice%"=="3" goto full
if "%choice%"=="4" goto copaw_only

echo 无效选择，默认启动基础模式
goto basic

:basic
echo.
echo [1/3] 启动 Copaw...
start "Copaw" cmd /k ".venv\Scripts\copaw.exe"
timeout /t 3 >nul

echo [2/3] 启动 NL Commander (Ollama)...
ros2 run rostofu_bringup nl_commander_node --ros-args -p llm_provider:=ollama -p ollama_model:=qwen2.5:7b
goto end

:cloud
echo.
echo 请选择云端 LLM:
echo   [1] 阿里云 DashScope
echo   [2] OpenAI
echo   [3] 智谱 AI
echo.
set /p cloud_choice="选择 [1-3]: "

if "%cloud_choice%"=="1" set PROVIDER=dashscope
if "%cloud_choice%"=="2" set PROVIDER=openai
if "%cloud_choice%"=="3" set PROVIDER=zhipu

set /p API_KEY="请输入 API Key: "

echo.
echo [1/3] 启动 Copaw...
start "Copaw" cmd /k ".venv\Scripts\copaw.exe"
timeout /t 3 >nul

echo [2/3] 启动 NL Commander (%PROVIDER%)...
ros2 run rostofu_bringup nl_commander_node --ros-args -p llm_provider:=%PROVIDER% -p %PROVIDER%_api_key:=%API_KEY%
goto end

:full
echo.
echo [1/4] 启动 Copaw...
start "Copaw" cmd /k ".venv\Scripts\copaw.exe"
timeout /t 3 >nul

echo [2/4] 启动 NL Commander...
start "NL Commander" cmd /k "ros2 run rostofu_bringup nl_commander_node"
timeout /t 2 >nul

echo [3/4] 启动 Voice Input...
ros2 run rostofu_bringup voice_input_node
goto end

:copaw_only
echo.
echo 启动 Copaw (无自然语言控制)...
.venv\Scripts\copaw.exe
goto end

:end
echo.
echo 启动完成!
pause
