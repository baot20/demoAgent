#!/usr/bin/env python3
"""
EXA集成测试脚本
演示如何设置EXA API key并测试网络搜索功能
"""

import os
from speaker_validation_tools import perform_preaudit, check_string_content, exa_config

def test_exa_integration():
    """测试EXA集成功能"""
    
    print("=" * 60)
    print("EXA集成测试")
    print("=" * 60)
    
    # 检查EXA API key（优先从配置文件，然后从环境变量）
    exa_api_key = exa_config.get('api_key', '')
    if not exa_api_key:
        exa_api_key = os.getenv('EXA_API_KEY', '')
    
    if not exa_api_key:
        print("⚠️  EXA API key未设置")
        print("请在 .config 文件中设置:")
        print("[EXA]")
        print("EXA_API_KEY = your_actual_exa_api_key_here")
        print()
        print("或者设置环境变量:")
        print("export EXA_API_KEY='your_actual_exa_api_key_here'")
        print()
        print("继续测试回退逻辑...")
    else:
        print(f"✅ EXA API key已设置: {exa_api_key[:10]}...")
        print("   来源: 配置文件" if exa_config.get('api_key') else "环境变量")
    
    print()
    
    # 测试用例
    test_cases = [
        {
            "name": "鲍娜医生（不触发EXA搜索）",
            "input": "我请到了鲍娜医生，目前就职长海医院demo科室",
            "expected_method": "direct_pass"
        },
        {
            "name": "张丹医生（触发EXA搜索）",
            "input": "张丹 上海市长海医院 皮肤科 主任",
            "expected_method": "exa_search" if exa_api_key else "exa_search_failed"
        },
        {
            "name": "完整格式输入",
            "input": "我请到了上海市长海医院皮肤科主任张丹医生",
            "expected_method": "exa_search" if exa_api_key else "exa_search_failed"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. 测试: {test_case['name']}")
        print(f"   输入: {test_case['input']}")
        
        try:
            result = check_string_content(test_case['input'])
            
            print(f"   验证结果: {'✅ 通过' if result['verification_passed'] else '❌ 失败'}")
            print(f"   验证方法: {result['verification_method']}")
            print(f"   提取信息: {result['extracted_info']}")
            
            if 'exa_search_results' in result and result['exa_search_results']:
                exa_result = result['exa_search_results']
                if exa_result.get('success'):
                    print(f"   EXA搜索: 成功，匹配分数 {exa_result.get('match_score', 0)}")
                    print(f"   搜索结果: {exa_result.get('total_results', 0)}个结果")
                else:
                    print(f"   EXA搜索: 失败，错误 {exa_result.get('error', '未知')}")
            
            print()
            
        except Exception as e:
            print(f"   ❌ 测试失败: {str(e)}")
            print()
    
    print("=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_exa_integration()
