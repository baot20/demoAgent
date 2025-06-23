#!/usr/bin/env python3
"""
测试讲者身份验证系统 - 简化版本
"""

import boto3
import logging
import re
from typing import Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_doctor_info(text: str) -> Dict[str, str]:
    """从文本中提取医生信息"""
    info = {
        'name': '',
        'hospital': '',
        'department': '',
        'title': ''
    }
    
    # 提取医生姓名
    name_patterns = [
        r'请到了([^，。！？\s]{2,4})医生',
        r'邀请了([^，。！？\s]{2,4})医生',
        r'([^，。！？\s]{2,4})医生',
        r'请到了([^，。！？\s]{2,4})(?=，|。|目前|现任|来自)',
        r'邀请了([^，。！？\s]{2,4})(?=，|。|目前|现任|来自)',
        r'有个([^，。！？\s]{2,4})医生',
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            name = match.group(1)
            if name not in ['本次', '今天', '明天', '昨天', '活动', '会议', '我们', '他们']:
                info['name'] = name
                break
    
    # 提取医院信息
    hospital_patterns = [
        r'目前就职\s*([^，。！？\s]*医院)',
        r'就职于\s*([^，。！？\s]*医院)',
        r'来自\s*([^，。！？\s]*医院)',
        r'([^，。！？\s]*医院)'
    ]
    
    for pattern in hospital_patterns:
        match = re.search(pattern, text)
        if match:
            hospital = match.group(1)
            if '医院' in hospital and len(hospital) > 2:
                info['hospital'] = hospital
                break
    
    # 提取科室信息
    department_patterns = [
        r'([^，。！？\s]*科室)',
        r'([^，。！？\s]*科)(?!室)',
        r'([^，。！？\s]*部门)'
    ]
    
    for pattern in department_patterns:
        match = re.search(pattern, text)
        if match:
            dept = match.group(1)
            if dept not in ['目前就职', '现在', '以前'] and len(dept) <= 10 and len(dept) >= 2:
                info['department'] = dept
                break
    
    # 提取职称信息
    title_patterns = [
        r'职称为([^，。！？\s]*)',
        r'([^，。！？\s]*主任医师)',
        r'([^，。！？\s]*副主任医师)',
        r'([^，。！？\s]*主治医师)',
        r'([^，。！？\s]*住院医师)',
        r'([^，。！？\s]*医师)(?!来|去|说)'
    ]
    
    for pattern in title_patterns:
        match = re.search(pattern, text)
        if match:
            title = match.group(1)
            if ('医师' in title or '医生' in title) and len(title) <= 10:
                info['title'] = title
                break
    
    return info

def check_string_content(input_string: str, target_word: str = "鲍娜") -> Dict[str, Any]:
    """
    检查讲者身份信息的真实性和完整性
    
    Args:
        input_string: 医药代表提交的讲者信息文本
        target_word: 特殊验证标识，默认为"鲍娜"
        
    Returns:
        验证结果字典
    """
    # 检查是否包含特殊标识
    contains_target = target_word in input_string
    
    result = {
        "input_string": input_string,
        "target_word": target_word,
        "contains_target": contains_target,
        "verification_passed": False,
        "verification_method": "",
        "extracted_info": {},
        "verification_details": {},
        "string_length": len(input_string)
    }
    
    # 如果包含特殊标识（如"鲍娜"），直接通过
    if contains_target:
        result["verification_passed"] = True
        result["verification_method"] = "direct_pass"
        result["verification_details"] = {
            "message": f"包含特殊标识'{target_word}'，直接通过验证",
            "confidence_score": 10
        }
        return result
    
    # 如果不包含特殊标识，进行信息提取和验证
    extracted_info = extract_doctor_info(input_string)
    result["extracted_info"] = extracted_info
    
    if not extracted_info['name']:
        result["verification_details"] = {
            "message": "无法从文本中提取医生姓名",
            "confidence_score": 0
        }
        return result
    
    # 简单的验证逻辑：如果提取到了姓名、医院、科室、职称中的至少3个，认为信息完整
    complete_fields = sum(1 for field in extracted_info.values() if field)
    result["verification_method"] = "info_extraction"
    
    if complete_fields >= 3:
        result["verification_passed"] = True
        result["verification_details"] = {
            "message": f"讲者信息完整，包含{complete_fields}个字段",
            "confidence_score": complete_fields * 2
        }
    else:
        result["verification_passed"] = False
        result["verification_details"] = {
            "message": f"讲者信息不完整，仅包含{complete_fields}个字段",
            "confidence_score": complete_fields
        }
    
    return result

# 简单测试函数
def simple_test():
    """简单测试讲者身份验证逻辑"""
    
    # 测试用例
    test_cases = [
        {
            "bucket": "test-bucket",
            "input": "本次活动我请到了鲍娜医生，目前就职demo医院demo科室，职称为副主任医生。",
            "expected": "直接通过验证"
        },
        {
            "bucket": "test-bucket", 
            "input": "本次活动我请到了张三医生，目前就职北京协和医院心内科，职称为主任医师。",
            "expected": "信息完整，验证通过"
        },
        {
            "bucket": "test-bucket",
            "input": "今天有个医生来讲课。",
            "expected": "信息不完整，验证失败"
        }
    ]
    
    print("=" * 60)
    print("讲者身份验证系统 - 简单测试")
    print("=" * 60)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"存储桶: {case['bucket']}")
        print(f"用户输入: {case['input']}")
        
        # 检查讲者信息
        verification_result = check_string_content(case['input'])
        print(f"验证结果: {verification_result['verification_passed']}")
        print(f"验证方法: {verification_result['verification_method']}")
        print(f"提取信息: {verification_result['extracted_info']}")
        print(f"详细信息: {verification_result['verification_details']['message']}")
        print(f"预期结果: {case['expected']}")
        
        # 验证逻辑
        if verification_result['verification_passed']:
            print("✅ 讲者身份验证通过")
            if verification_result['verification_method'] == 'direct_pass':
                print("📋 特殊标识验证通过")
            else:
                print("📁 需要检查 S3 支撑文档...")
        else:
            print("❌ 讲者身份验证失败")
        
        print("-" * 40)

if __name__ == "__main__":
    simple_test()
