#!/usr/bin/env python3
"""
SpeakerValidationPreCheckSystem MCP Server 启动脚本
"""

import os
import sys
import asyncio

def check_config():
    """检查配置是否正确"""
    if not os.path.exists('.config'):
        print("❌ 未找到配置文件 .config")
        print("请先运行: cp .config.example .config")
        print("然后编辑 .config 文件填入你的 AWS 信息")
        return False
    
    try:
        from config_reader import get_config
        config = get_config()
        if not config.validate_config():
            print("❌ 配置验证失败")
            print("请检查 .config 文件中的 AWS 凭证信息")
            return False
    except Exception as e:
        print(f"❌ 配置加载失败: {str(e)}")
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 SpeakerValidationPreCheckSystem MCP Server")
    print("=" * 50)
    
    # 检查配置
    if not check_config():
        sys.exit(1)
    
    print("✅ 配置验证通过")
    print("🤖 启动 MCP Server...")
    print("=" * 50)
    
    # 启动 MCP server
    try:
        from mcp_server import main as mcp_main
        asyncio.run(mcp_main())
    except KeyboardInterrupt:
        print("\n👋 MCP Server 已停止")
    except Exception as e:
        print(f"❌ MCP Server 启动失败: {str(e)}")
        print("请检查依赖是否正确安装: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
