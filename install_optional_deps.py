#!/usr/bin/env python3
"""
安装可选依赖脚本
"""

import subprocess
import sys

def install_watchtower():
    """安装 watchtower 用于 CloudWatch 日志"""
    print("=" * 60)
    print("安装 CloudWatch 日志支持")
    print("=" * 60)
    
    try:
        print("正在安装 watchtower...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "watchtower>=3.0.0"])
        print("✅ watchtower 安装成功")
        
        # 测试导入
        import watchtower
        print("✅ watchtower 导入测试成功")
        print("🎉 CloudWatch 日志功能现在可用！")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ watchtower 安装失败: {e}")
        print("请手动运行: pip install watchtower")
    except ImportError as e:
        print(f"❌ watchtower 导入失败: {e}")
        print("请检查安装是否成功")

def install_mcp():
    """安装 MCP 依赖"""
    print("\n" + "=" * 60)
    print("安装 MCP 协议支持")
    print("=" * 60)
    
    try:
        print("正在安装 mcp...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp>=1.0.0"])
        print("✅ mcp 安装成功")
        
        # 测试导入
        import mcp
        print("✅ mcp 导入测试成功")
        print("🎉 MCP 协议支持现在可用！")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ mcp 安装失败: {e}")
        print("请手动运行: pip install mcp")
    except ImportError as e:
        print(f"❌ mcp 导入失败: {e}")
        print("请检查安装是否成功")

def main():
    """主函数"""
    print("🚀 SpeakerValidationPreCheckSystem 可选依赖安装")
    
    # 检查当前已安装的依赖
    print("\n检查当前依赖状态:")
    
    # 检查 watchtower
    try:
        import watchtower
        print("✅ watchtower: 已安装")
    except ImportError:
        print("❌ watchtower: 未安装（CloudWatch 日志功能将被禁用）")
        
        response = input("\n是否要安装 watchtower 以启用 CloudWatch 日志功能？(y/n): ")
        if response.lower() in ['y', 'yes']:
            install_watchtower()
    
    # 检查 mcp
    try:
        import mcp
        print("✅ mcp: 已安装")
    except ImportError:
        print("❌ mcp: 未安装（MCP Server 功能将不可用）")
        
        response = input("\n是否要安装 mcp 以启用 MCP Server 功能？(y/n): ")
        if response.lower() in ['y', 'yes']:
            install_mcp()
    
    print("\n" + "=" * 60)
    print("依赖检查完成")
    print("=" * 60)
    
    # 最终测试
    print("\n最终功能测试:")
    
    try:
        from speaker_validation_tools import get_current_config
        config = get_current_config()
        print("✅ 核心功能: 可用")
    except Exception as e:
        print(f"❌ 核心功能: 不可用 - {e}")
    
    try:
        import mcp_server
        print("✅ MCP Server: 可用")
    except Exception as e:
        print(f"❌ MCP Server: 不可用 - {e}")
    
    try:
        import watchtower
        print("✅ CloudWatch 日志: 可用")
    except ImportError:
        print("⚠️  CloudWatch 日志: 不可用（功能已降级为控制台日志）")

if __name__ == "__main__":
    main()
