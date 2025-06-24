#!/usr/bin/env python3
"""
测试 Strands Agent 版本的讲者身份验证系统
"""

import sys
import os
from strands import Agent, tool
from strands_tools import current_time

# 简单的测试工具
@tool
def test_speaker_verification(input_string: str, target_word: str = "鲍娜") -> str:
    """
    测试讲者身份验证功能
    
    Args:
        input_string: 输入的讲者信息
        target_word: 特殊标识词汇
        
    Returns:
        验证结果
    """
    contains_target = target_word in input_string
    
    if contains_target:
        return f"讲者验证通过 - 包含特殊标识'{target_word}'，直接通过验证"
    
    # 简单的信息提取逻辑
    has_name = any(word in input_string for word in ['医生', '教授', '主任'])
    has_hospital = '医院' in input_string
    has_department = any(word in input_string for word in ['科', '科室', '部门'])
    has_title = any(word in input_string for word in ['主任医师', '副主任医师', '主治医师'])
    
    info_count = sum([has_name, has_hospital, has_department, has_title])
    
    if info_count >= 3:
        return f"讲者验证通过 - 信息完整度高（{info_count}/4个字段）"
    else:
        return f"讲者验证失败 - 信息不完整（仅{info_count}/4个字段）"

@tool
def simulate_s3_check(file_count: int = 5) -> str:
    """
    模拟 S3 支撑文档检查
    
    Args:
        file_count: 模拟的文件数量
        
    Returns:
        检查结果
    """
    min_count = 3
    return f"S3 存储桶中有 {file_count} 个支撑文档，{'满足' if file_count > min_count else '不满足'}最小要求（>{min_count}个）"

@tool
def simulate_speaker_preaudit(input_string: str, file_count: int = 5) -> str:
    """
    模拟完整的讲者预审流程
    
    Args:
        input_string: 讲者信息输入
        file_count: 支撑文档数量
        
    Returns:
        预审结果
    """
    target_word = "鲍娜"
    min_file_count = 3
    
    # 检查特殊标识
    contains_target = target_word in input_string
    if contains_target:
        return f"讲者预审通过 - 包含特殊标识'{target_word}'，直接通过验证"
    
    # 检查信息完整性
    has_name = any(word in input_string for word in ['医生', '教授', '主任'])
    has_hospital = '医院' in input_string
    has_department = any(word in input_string for word in ['科', '科室', '部门'])
    has_title = any(word in input_string for word in ['主任医师', '副主任医师', '主治医师'])
    
    info_count = sum([has_name, has_hospital, has_department, has_title])
    info_complete = info_count >= 3
    
    # 检查文档数量
    file_count_ok = file_count > min_file_count
    
    if info_complete and file_count_ok:
        return f"讲者预审通过 - 信息完整({info_count}/4)且支撑文档充足({file_count}>{min_file_count})"
    else:
        reasons = []
        if not info_complete:
            reasons.append(f"信息不完整({info_count}/4)")
        if not file_count_ok:
            reasons.append(f"支撑文档不足({file_count}<={min_file_count})")
        return f"讲者预审不通过 - {'; '.join(reasons)}"

# 创建测试 Agent
test_agent = Agent(
    tools=[
        test_speaker_verification,
        simulate_s3_check, 
        simulate_speaker_preaudit,
        current_time
    ]
)

def test_strands_agent():
    """测试 Strands Agent 功能"""
    print("=" * 60)
    print("Strands Agent 讲者身份验证测试")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        {
            "input": "本次活动我请到了鲍娜医生，目前就职demo医院demo科室，职称为副主任医生。",
            "files": 5,
            "expected": "直接通过"
        },
        {
            "input": "本次活动我请到了张三医生，目前就职北京协和医院心内科，职称为主任医师。",
            "files": 5, 
            "expected": "信息完整，通过"
        },
        {
            "input": "今天有个医生来讲课。",
            "files": 2,
            "expected": "信息不完整，不通过"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"讲者信息: {case['input']}")
        print(f"支撑文档数: {case['files']}")
        print("-" * 40)
        
        message = f"""
        请对以下讲者信息进行身份验证：
        - 讲者信息: "{case['input']}"
        - 支撑文档数量: {case['files']}
        
        请使用以下工具进行检查：
        1. test_speaker_verification - 检查讲者身份信息
        2. simulate_s3_check - 检查支撑文档数量
        3. simulate_speaker_preaudit - 执行完整预审
        
        请给出详细的验证过程和最终结果。
        """
        
        try:
            print("Agent 执行结果:")
            response = test_agent(message)
            print("-" * 40)
        except Exception as e:
            print(f"测试失败: {str(e)}")

def main():
    """主函数"""
    print("Strands Agent 讲者身份验证系统测试")
    
    # 检查 strands 是否可用
    try:
        from strands import Agent, tool
        print("✅ Strands 框架导入成功")
    except ImportError as e:
        print(f"❌ Strands 框架导入失败: {str(e)}")
        print("请确保已安装 strands 相关包")
        return
    
    # 运行测试
    test_strands_agent()

if __name__ == "__main__":
    main()
