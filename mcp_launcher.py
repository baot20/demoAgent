#!/usr/bin/env python3
"""
MCP Server启动器
自动激活虚拟环境并启动MCP server
"""

import os
import sys
import subprocess

def main():
    """启动MCP server"""
    # 获取项目目录
    project_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(project_dir, '.venv', 'bin', 'python')
    mcp_server_path = os.path.join(project_dir, 'mcp_server.py')
    
    # 检查虚拟环境是否存在
    if not os.path.exists(venv_python):
        print(f"错误: 虚拟环境不存在: {venv_python}", file=sys.stderr)
        sys.exit(1)
    
    # 检查MCP server文件是否存在
    if not os.path.exists(mcp_server_path):
        print(f"错误: MCP server文件不存在: {mcp_server_path}", file=sys.stderr)
        sys.exit(1)
    
    # 检查配置文件是否存在
    config_file = os.path.join(project_dir, '.config')
    if not os.path.exists(config_file):
        print(f"错误: 配置文件不存在: {config_file}", file=sys.stderr)
        sys.exit(1)
    
    # 设置环境变量
    env = os.environ.copy()
    env['PYTHONPATH'] = project_dir
    
    # 切换到项目目录（重要！）
    os.chdir(project_dir)
    
    try:
        # 使用虚拟环境的Python启动MCP server
        # 使用exec替换当前进程，这样可以正确处理信号
        os.execve(venv_python, [venv_python, mcp_server_path], env)
    except Exception as e:
        print(f"MCP server启动失败: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
