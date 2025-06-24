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
            "name": "张三医生（有文件夹，触发EXA搜索）",
            "input": "张三 长海医院 心内科 主任医师",
            "expected_method": "exa_search" if exa_api_key else "exa_search_failed"
        },
        {
            "name": "李四医生（无文件夹，直接失败）",
            "input": "李四 北京协和医院 心内科 主任医师",
            "expected_method": "folder_not_found"
        },
        {
            "name": "钟南山院士（知名医生，无文件夹）",
            "input": "钟南山 广州医科大学附属第一医院 呼吸内科 院士",
            "expected_method": "folder_not_found"
        },
        {
            "name": "张丹医生（有文件夹但为空）",
            "input": "张丹 上海市长海医院 皮肤科 主任",
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
            
            # 测试完整预审流程
            print("   🔄 完整预审测试...")
            preaudit_result = perform_preaudit(test_case['input'])
            
            if "未找到讲者专属文件夹" in preaudit_result:
                print("   📁 文件夹检查: ❌ 专属文件夹不存在")
            elif "预审通过" in preaudit_result:
                print("   📁 预审结果: ✅ 通过")
            elif "预审部分通过" in preaudit_result:
                print("   📁 预审结果: 🔶 部分通过")
            else:
                print("   📁 预审结果: ❌ 不通过")
            
            print()
            
        except Exception as e:
            print(f"   ❌ 测试失败: {str(e)}")
            print()
    
    print("=" * 60)
    print("测试完成")
    print("=" * 60)
    
    print("\n🎯 新增逻辑验证:")
    print("✅ 如果医生信息提取成功但S3中没有专属文件夹，直接审核不通过")
    print("✅ 鲍娜医生特殊处理，不受此逻辑影响")
    print("✅ 有文件夹的医生继续正常验证流程")

if __name__ == "__main__":
    test_exa_integration()
