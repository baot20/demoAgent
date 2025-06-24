#!/usr/bin/env python3
"""
测试 SpeakerValidationPreCheckSystem MCP Server - 讲者身份验证系统 v2.1.0
"""

import asyncio
import json
from speaker_validation_tools import (
    list_s3_files,
    list_s3_files_with_prefix,
    check_string_content,
    perform_preaudit,
    get_current_config
)

async def test_tools():
    """测试所有工具函数"""
    print("=" * 60)
    print("SpeakerValidationPreCheckSystem MCP Server 测试")
    print("讲者身份验证系统 v2.1.0 - EXA集成版本")
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
            "name": "鲍娜医生（内部验证，不触发EXA搜索）",
            "content": "本次活动我请到了鲍娜医生，目前就职长海医院demo科室，职称为副主任医生。",
            "expected_method": "direct_pass",
            "expected_folder": "tinabao/"
        },
        {
            "name": "张三医生（专属文件夹验证）",
            "content": "本次活动我请到了张三医生，目前就职长海医院心内科，职称为主任医师。",
            "expected_method": "exa_search",
            "expected_folder": "张三-长海医院-心内科/"
        },
        {
            "name": "钟南山院士（知名医生，EXA搜索应该成功）",
            "content": "钟南山 广州医科大学附属第一医院 呼吸内科 院士",
            "expected_method": "exa_search",
            "expected_folder": "钟南山-广州医科大学附属第一医院-呼吸内科/"
        },
        {
            "name": "张丹医生（一般医生，EXA搜索可能失败）",
            "content": "张丹 上海市长海医院 皮肤科 主任",
            "expected_method": "exa_search_failed",
            "expected_folder": "张丹-上海市长海医院-皮肤科/"
        },
        {
            "name": "信息不完整的情况",
            "content": "今天有个医生来讲课。",
            "expected_method": "",
            "expected_folder": "无法确定"
        }
    ]
    
    # 测试讲者身份验证
    print("\n2. 测试讲者身份验证:")
    for i, case in enumerate(test_cases, 1):
        print(f"\n  测试用例 {i}: {case['name']}")
        print(f"  输入内容: {case['content']}")
        print(f"  预期验证方法: {case['expected_method']}")
        print(f"  预期检查文件夹: {case['expected_folder']}")
        
        try:
            result = check_string_content(case['content'])
            print(f"  验证结果: {'✅ 通过' if result['verification_passed'] else '❌ 失败'}")
            print(f"  实际验证方法: {result['verification_method']}")
            print(f"  提取信息: {result['extracted_info']}")
            
            # 显示EXA搜索结果
            if 'exa_search_results' in result and result['exa_search_results']:
                exa_result = result['exa_search_results']
                if exa_result.get('success'):
                    print(f"  EXA搜索: 成功，匹配分数 {exa_result.get('match_score', 0)}/10")
                else:
                    print(f"  EXA搜索: 失败，{exa_result.get('error', '未知错误')}")
            
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
    
    # 测试S3文件列表功能
    print("\n3. 测试S3文件列表功能:")
    
    # 测试默认文件夹（tinabao）
    print("\n  3.1 测试默认文件夹 (tinabao/):")
    try:
        result = list_s3_files()
        print(f"  成功: {result['success']}")
        print(f"  文件数量: {result['file_count']}")
        if result['files']:
            print(f"  文件列表: {result['files'][:5]}...")  # 只显示前5个
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
    
    # 测试专属文件夹
    test_prefixes = [
        "张三-长海医院-心内科/",
        "宋智钢-上海长海医院-心血管外科/",
        "钟南山-广州医科大学附属第一医院-呼吸内科/"
    ]
    
    for prefix in test_prefixes:
        print(f"\n  3.2 测试专属文件夹 ({prefix}):")
        try:
            result = list_s3_files_with_prefix(prefix=prefix)
            print(f"  成功: {result['success']}")
            print(f"  文件数量: {result['file_count']}")
            if result['files']:
                print(f"  文件列表: {result['files']}")
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
    
    # 测试完整预审流程
    print("\n4. 测试完整预审流程:")
    for i, case in enumerate(test_cases[:3], 1):  # 只测试前3个案例
        print(f"\n  预审测试 {i}: {case['name']}")
        try:
            result = perform_preaudit(case['content'])
            
            # 显示结果摘要
            if "预审通过" in result:
                print("  结果: ✅ 通过")
            elif "预审部分通过" in result:
                print("  结果: 🔶 部分通过")
            else:
                print("  结果: ❌ 不通过")
            
            # 显示关键信息
            lines = result.split('\n')[:10]  # 只显示前10行
            for line in lines:
                if line.strip():
                    print(f"  {line}")
            
            if len(result.split('\n')) > 10:
                print("  ...")
                
        except Exception as e:
            print(f"  ❌ 预审测试失败: {e}")

def main():
    """主函数"""
    print("🚀 启动 MCP Server 工具测试")
    asyncio.run(test_tools())
    print("\n✨ 测试完成！")
    print("\n💡 提示:")
    print("- 确保 .config 文件中的 EXA_API_KEY 已正确设置")
    print("- 检查 AWS 凭证和 S3 存储桶配置")
    print("- 上传测试文档到对应的 S3 文件夹")

if __name__ == "__main__":
    main()
