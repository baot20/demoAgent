#!/usr/bin/env python3
"""
测试 SpeakerValidationPreCheckSystem MCP Server - 讲者身份验证系统
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
    print("讲者身份验证系统")
    print("=" * 60)
    
    # 测试配置获取
    print("\n1. 测试配置获取:")
    try:
        config = get_current_config()
        print(json.dumps(config, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"配置获取失败: {e}")
    
    # 测试用例
    test_cases = [
        {
            "name": "包含鲍娜的情况（直接通过）",
            "content": "本次活动我请到了鲍娜医生，目前就职demo医院demo科室，职称为副主任医生。"
        },
        {
            "name": "完整讲者信息（需要验证）",
            "content": "本次活动我请到了张三医生，目前就职北京协和医院心内科，职称为主任医师。"
        },
        {
            "name": "信息不完整的情况",
            "content": "今天有个医生来讲课。"
        }
    ]
    
    # 测试讲者身份验证
    print("\n2. 测试讲者身份验证:")
    for i, case in enumerate(test_cases, 1):
        print(f"\n  测试用例 {i}: {case['name']}")
        print(f"  输入内容: {case['content']}")
        try:
            result = check_string_content(case['content'])
            print(f"  验证结果: {result['verification_passed']}")
            print(f"  验证方法: {result['verification_method']}")
            if result['extracted_info']:
                print(f"  提取信息: {json.dumps(result['extracted_info'], ensure_ascii=False)}")
            print(f"  详细信息: {result['verification_details']['message']}")
        except Exception as e:
            print(f"  验证失败: {e}")
        print("  " + "-" * 50)
    
    # 测试 S3 支撑文档检查
    print("\n3. 测试支撑文档检查:")
    try:
        result = list_s3_files()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"文档检查失败: {e}")
    
    # 测试完整预审流程
    print("\n4. 测试完整预审流程:")
    for i, case in enumerate(test_cases, 1):
        print(f"\n  预审用例 {i}: {case['name']}")
        try:
            result = perform_preaudit(case['content'])
            print(f"  预审结果: {result}")
        except Exception as e:
            print(f"  预审失败: {e}")
        print("  " + "-" * 50)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_tools())
