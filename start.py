#!/usr/bin/env python3
"""
SpeakerValidationPreCheckSystem 快速启动脚本
"""

import os
import sys

def main():
    """主函数"""
    print("🚀 SpeakerValidationPreCheckSystem - Strands Agent 版本")
    print("=" * 50)
    
    # 检查配置
    if not os.path.exists('.config'):
        print("❌ 未找到配置文件")
        print("请先运行: cp .config.example .config")
        print("然后编辑 .config 文件填入你的 AWS 信息")
        return
    
    try:
        from config_reader import get_config
        config = get_config()
        if not config.validate_config():
            print("❌ 配置验证失败")
            print("请检查 .config 文件中的 AWS 凭证信息")
            print("运行 'python test_config.py' 查看详细错误")
            return
    except Exception as e:
        print(f"❌ 配置加载失败: {str(e)}")
        return
    
    print("✅ 配置验证通过")
    print("🤖 启动 Strands Agent...")
    print("=" * 50)
    
    # 启动主程序
    try:
        from agent import main as agent_main
        agent_main()
    except KeyboardInterrupt:
        print("\n👋 再见！")
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        print("请检查依赖是否正确安装: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
