#!/usr/bin/env python3
"""
测试 pharma_demo.py 的核心功能（不依赖strands）
"""

import re

def extract_speaker_info(content: str) -> dict:
    """从文本中提取讲者信息"""
    info = {
        'name': '',
        'hospital': '',
        'department': '',
        'title': ''
    }
    
    # 简化的信息提取逻辑
    name_patterns = [
        r'请到了([^，。！？\s]{2,4})医生',
        r'邀请了([^，。！？\s]{2,4})医生',
        r'([^，。！？\s]{2,4})医生',
        r'([^，。！？\s]{2,4})教授'
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, content)
        if match:
            name = match.group(1)
            if name not in ['本次', '今天', '明天', '昨天', '活动', '会议']:
                info['name'] = name
                break
    
    if '医院' in content:
        hospital_match = re.search(r'([^，。！？\s]*医院)', content)
        if hospital_match:
            info['hospital'] = hospital_match.group(1)
    
    if any(dept in content for dept in ['科', '科室', '部门']):
        dept_match = re.search(r'([^，。！？\s]*科)', content)
        if dept_match:
            info['department'] = dept_match.group(1)
    
    if any(title in content for title in ['主任医师', '副主任医师', '主治医师', '教授']):
        title_match = re.search(r'([^，。！？\s]*(?:主任医师|副主任医师|主治医师|教授))', content)
        if title_match:
            info['title'] = title_match.group(1)
    
    return info

def speaker_verification(content: str, target_word: str = "鲍娜") -> dict:
    """讲者身份验证"""
    # 检查特殊标识
    contains_target = target_word in content
    
    if contains_target:
        return {
            "verification_passed": True,
            "verification_method": "direct_pass",
            "message": f"包含特殊标识'{target_word}'，直接通过验证",
            "confidence_score": 10
        }
    
    # 提取讲者信息
    extracted_info = extract_speaker_info(content)
    complete_fields = sum(1 for field in extracted_info.values() if field)
    
    if complete_fields >= 3:
        return {
            "verification_passed": True,
            "verification_method": "info_extraction",
            "message": f"讲者信息完整，包含{complete_fields}个字段",
            "confidence_score": complete_fields * 2,
            "extracted_info": extracted_info
        }
    else:
        return {
            "verification_passed": False,
            "verification_method": "info_extraction", 
            "message": f"讲者信息不完整，仅包含{complete_fields}个字段",
            "confidence_score": complete_fields,
            "extracted_info": extracted_info
        }

def test_speaker_validation_demo():
    """测试讲者身份验证演示功能"""
    print("=" * 60)
    print("讲者身份验证系统 - 演示功能测试")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        {
            "content": "本次活动我请到了鲍娜医生，目前就职demo医院demo科室，职称为副主任医生。",
            "scenario": "包含特殊标识的讲者信息（直接通过）",
            "expected": "应该直接通过验证"
        },
        {
            "content": "本次活动我请到了张三医生，目前就职北京协和医院心内科，职称为主任医师。",
            "scenario": "完整的讲者信息（需要验证）", 
            "expected": "信息完整，应该通过验证"
        },
        {
            "content": "我们邀请了李四医生，他来自上海交通大学医学院附属瑞金医院心血管内科，职称为副主任医师。",
            "scenario": "详细的讲者资质信息",
            "expected": "信息详细，应该通过验证"
        },
        {
            "content": "今天有个医生来讲课。",
            "scenario": "信息不完整的讲者描述",
            "expected": "信息不足，应该验证失败"
        },
        {
            "content": "王五教授将为我们分享最新的治疗方案，他是某医院的专家。",
            "scenario": "模糊的讲者信息",
            "expected": "信息不够具体，可能验证失败"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n演示 {i}: {case['scenario']}")
        print(f"讲者信息: {case['content']}")
        print(f"预期结果: {case['expected']}")
        print("-" * 40)
        
        # 执行验证
        result = speaker_verification(case['content'])
        
        print(f"验证结果: {'✅ 通过' if result['verification_passed'] else '❌ 失败'}")
        print(f"验证方法: {result['verification_method']}")
        print(f"详细信息: {result['message']}")
        
        if 'extracted_info' in result:
            extracted = result['extracted_info']
            print(f"提取信息:")
            print(f"  - 姓名: {extracted.get('name', '未提取')}")
            print(f"  - 医院: {extracted.get('hospital', '未提取')}")
            print(f"  - 科室: {extracted.get('department', '未提取')}")
            print(f"  - 职称: {extracted.get('title', '未提取')}")
        
        print(f"置信度: {result['confidence_score']}/10")
        print("=" * 60)

if __name__ == "__main__":
    test_speaker_validation_demo()
