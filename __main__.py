#!/usr/bin/env python3
"""
MCP Server启动入口点
支持通过 python -m 方式启动
"""

import sys
import os

# 确保项目路径在Python路径中
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# 启动MCP server
if __name__ == "__main__":
    from mcp_server import main
    main()
