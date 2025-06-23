#!/usr/bin/env python3
"""
测试 SpeakerValidationPreCheckSystem MCP Server
"""

import asyncio
import json
from speaker_validation_tools import (
    list_s3_files,
    check_string_content,
    perform_preaudit,
    get_current_config
)

async def test_tools():
    """测试所有工具函数"""
    print("=" * 60)
    print("SpeakerValidationPreCheckSystem MCP Server 测试")
    print("=" * 60)
    
    # 测试配置获取
    print("\n1. 测试配置获取:")
    try:
        config = get_current_config()
        print(json.dumps(config, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"配置获取失败: {e}")
    
    # 测试内容检查
    print("\n2. 测试内容合规检查:")
    test_content = "各位医生，今天我要为大家介绍我们公司的新产品。本次演讲内容已经过鲍娜审核。"
    try:
        result = check_string_content(test_content)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"内容检查失败: {e}")
    
    # 测试 S3 文档检查
    print("\n3. 测试支撑文档检查:")
    try:
        result = list_s3_files()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"文档检查失败: {e}")
    
    # 测试完整预审
    print("\n4. 测试完整预审流程:")
    try:
        result = perform_preaudit(test_content)
        print(result)
    except Exception as e:
        print(f"预审失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")

if __name__ == "__main__":
    asyncio.run(test_tools())
