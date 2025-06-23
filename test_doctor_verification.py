#!/usr/bin/env python3
"""
测试医生身份验证功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import check_string_content

def test_doctor_verification():
    """测试医生身份验证功能"""
    
    print("=" * 60)
    print("测试医生身份验证功能")
    print("=" * 60)
    
    # 测试用例1：包含"鲍娜"的情况（应该直接通过）
    test_case_1 = "本次活动我请到了鲍娜医生，目前就职demo医院demo科室，职称为副主任医生。"
    print("\n测试用例1：包含'鲍娜'的情况")
    print(f"输入: {test_case_1}")
    
    result_1 = check_string_content(test_case_1)
    print(f"验证结果: {result_1['verification_passed']}")
    print(f"验证方法: {result_1['verification_method']}")
    print(f"详细信息: {result_1['verification_details']}")
    
    # 测试用例2：其他医生的情况（需要网络搜索）
    test_case_2 = "本次活动我请到了张三医生，目前就职北京协和医院心内科，职称为主任医师。"
    print("\n测试用例2：其他医生的情况")
    print(f"输入: {test_case_2}")
    
    result_2 = check_string_content(test_case_2)
    print(f"验证结果: {result_2['verification_passed']}")
    print(f"验证方法: {result_2['verification_method']}")
    print(f"提取的信息: {result_2['extracted_info']}")
    print(f"搜索结果数量: {len(result_2['search_results'])}")
    print(f"详细信息: {result_2['verification_details']}")
    
    # 测试用例3：信息不完整的情况
    test_case_3 = "今天有个医生来讲课。"
    print("\n测试用例3：信息不完整的情况")
    print(f"输入: {test_case_3}")
    
    result_3 = check_string_content(test_case_3)
    print(f"验证结果: {result_3['verification_passed']}")
    print(f"验证方法: {result_3['verification_method']}")
    print(f"详细信息: {result_3['verification_details']}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_doctor_verification()
