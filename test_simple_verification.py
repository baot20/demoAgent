#!/usr/bin/env python3
"""
简化的医生身份验证功能测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 直接导入需要的函数和配置
from config_reader import get_config
import re
import requests
from bs4 import BeautifulSoup
import urllib.parse
from typing import Dict, Any, List
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载配置
config = get_config()
preaudit_config = config.get_preaudit_config()

def extract_doctor_info(text: str) -> Dict[str, str]:
    """从文本中提取医生信息"""
    info = {
        'name': '',
        'hospital': '',
        'department': '',
        'title': ''
    }
    
    # 提取医生姓名（优化后的正则表达式）
    name_patterns = [
        r'请到了([^，。！？\s]{2,4})医生',  # "请到了张三医生"
        r'([^，。！？\s]{2,4})医生',       # "张三医生"
        r'请到了([^，。！？\s]{2,4})',     # "请到了张三"
        r'有个([^，。！？\s]{2,4})医生',   # "有个张三医生"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            name = match.group(1)
            # 过滤掉一些明显不是姓名的词
            if name not in ['本次', '今天', '明天', '昨天', '活动', '会议']:
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
            if '医院' in hospital:
                info['hospital'] = hospital
                break
    
    # 提取科室信息
    department_patterns = [
        r'([^，。！？\s]*科室)',
        r'([^，。！？\s]*科)(?!室)',  # 匹配"心内科"但不匹配"科室"
        r'([^，。！？\s]*部门)'
    ]
    
    for pattern in department_patterns:
        match = re.search(pattern, text)
        if match:
            dept = match.group(1)
            # 过滤掉一些不是科室的词
            if dept not in ['目前就职', '现在', '以前'] and len(dept) <= 10:
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
            if '医师' in title or '医生' in title:
                info['title'] = title
                break
    
    return info

def check_doctor_verification(input_string: str, target_word: str = None) -> Dict[str, Any]:
    """检查医生身份验证"""
    if target_word is None:
        target_word = preaudit_config['target_word']
    
    # 检查是否包含特殊标识
    contains_target = target_word in input_string
    
    result = {
        "input_string": input_string,
        "target_word": target_word,
        "contains_target": contains_target,
        "verification_passed": False,
        "verification_method": "",
        "extracted_info": {},
        "verification_details": {}
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
    
    # 如果不包含特殊标识，提取医生信息
    extracted_info = extract_doctor_info(input_string)
    result["extracted_info"] = extracted_info
    
    if not extracted_info['name']:
        result["verification_details"] = {
            "message": "无法从文本中提取医生姓名",
            "confidence_score": 0
        }
        return result
    
    # 模拟网络搜索验证（简化版）
    result["verification_method"] = "online_search"
    
    # 简单的验证逻辑：如果提取到了姓名、医院、科室、职称中的至少3个，认为信息完整
    complete_fields = sum(1 for field in extracted_info.values() if field)
    
    if complete_fields >= 3:
        result["verification_passed"] = True
        result["verification_details"] = {
            "message": f"医生信息完整，包含{complete_fields}个字段",
            "confidence_score": complete_fields * 2
        }
    else:
        result["verification_passed"] = False
        result["verification_details"] = {
            "message": f"医生信息不完整，仅包含{complete_fields}个字段",
            "confidence_score": complete_fields
        }
    
    return result

def test_doctor_verification():
    """测试医生身份验证功能"""
    
    print("=" * 60)
    print("测试医生身份验证功能")
    print("=" * 60)
    
    # 测试用例1：包含"鲍娜"的情况（应该直接通过）
    test_case_1 = "本次活动我请到了鲍娜医生，目前就职demo医院demo科室，职称为副主任医生。"
    print("\n测试用例1：包含'鲍娜'的情况")
    print(f"输入: {test_case_1}")
    
    result_1 = check_doctor_verification(test_case_1)
    print(f"验证结果: {result_1['verification_passed']}")
    print(f"验证方法: {result_1['verification_method']}")
    print(f"详细信息: {result_1['verification_details']}")
    
    # 测试用例2：其他医生的情况（需要网络搜索）
    test_case_2 = "本次活动我请到了张三医生，目前就职北京协和医院心内科，职称为主任医师。"
    print("\n测试用例2：其他医生的情况")
    print(f"输入: {test_case_2}")
    
    result_2 = check_doctor_verification(test_case_2)
    print(f"验证结果: {result_2['verification_passed']}")
    print(f"验证方法: {result_2['verification_method']}")
    print(f"提取的信息: {result_2['extracted_info']}")
    print(f"详细信息: {result_2['verification_details']}")
    
    # 测试用例3：信息不完整的情况
    test_case_3 = "今天有个张医生来讲课。"
    print("\n测试用例3：信息不完整的情况")
    print(f"输入: {test_case_3}")
    
    result_3 = check_doctor_verification(test_case_3)
    print(f"验证结果: {result_3['verification_passed']}")
    print(f"验证方法: {result_3['verification_method']}")
    print(f"提取的信息: {result_3['extracted_info']}")
    print(f"详细信息: {result_3['verification_details']}")
    
    # 测试用例4：更完整的医生信息
    test_case_4 = "我们邀请了李四医生，他来自上海交通大学医学院附属瑞金医院心血管内科，职称为副主任医师。"
    print("\n测试用例4：更完整的医生信息")
    print(f"输入: {test_case_4}")
    
    result_4 = check_doctor_verification(test_case_4)
    print(f"验证结果: {result_4['verification_passed']}")
    print(f"验证方法: {result_4['verification_method']}")
    print(f"提取的信息: {result_4['extracted_info']}")
    print(f"详细信息: {result_4['verification_details']}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_doctor_verification()
