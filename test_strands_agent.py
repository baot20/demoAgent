#!/usr/bin/env python3
"""
测试 Strands Agent 版本的预审系统
"""

import sys
import os
from strands import Agent, tool
from strands_tools import current_time

# 简单的测试工具
@tool
def test_string_check(input_string: str, target_word: str = "鲍娜") -> str:
    """
    测试字符串检查功能
    
    Args:
        input_string: 输入字符串
        target_word: 目标词汇
        
    Returns:
        检查结果
    """
    contains_target = target_word in input_string
    return f"字符串 '{input_string}' {'包含' if contains_target else '不包含'} '{target_word}'"

@tool
def simulate_s3_check(file_count: int = 5) -> str:
    """
    模拟 S3 文件数量检查
    
    Args:
        file_count: 模拟的文件数量
        
    Returns:
        检查结果
    """
    min_count = 3
    return f"S3 存储桶中有 {file_count} 个文件，{'满足' if file_count > min_count else '不满足'}最小要求（>{min_count}个）"

@tool
def simulate_preaudit(input_string: str, file_count: int = 5) -> str:
    """
    模拟完整预审流程
    
    Args:
        input_string: 用户输入
        file_count: 文件数量
        
    Returns:
        预审结果
    """
    target_word = "鲍娜"
    min_file_count = 3
    
    contains_target = target_word in input_string
    file_count_ok = file_count > min_file_count
    
    if contains_target and file_count_ok:
        return f"预审通过 - 输入包含'{target_word}'且文件数({file_count})超过要求({min_file_count})"
    else:
        reasons = []
        if not contains_target:
            reasons.append(f"输入不包含'{target_word}'")
        if not file_count_ok:
            reasons.append(f"文件数({file_count})不足")
        return f"预审不通过 - {'; '.join(reasons)}"

# 创建测试 Agent
test_agent = Agent(
    tools=[
        test_string_check,
        simulate_s3_check, 
        simulate_preaudit,
        current_time
    ]
)

def test_strands_agent():
    """测试 Strands Agent 功能"""
    print("=" * 60)
    print("Strands Agent 功能测试")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        {
            "input": "你好鲍娜，今天天气不错",
            "files": 5,
            "expected": "通过"
        },
        {
            "input": "你好，今天天气不错",
            "files": 5, 
            "expected": "不通过"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"输入: {case['input']}")
        print(f"文件数: {case['files']}")
        print("-" * 40)
        
        message = f"""
        请对以下输入进行预审测试：
        - 用户输入: "{case['input']}"
        - 模拟文件数: {case['files']}
        
        请使用以下工具进行检查：
        1. test_string_check - 检查字符串内容
        2. simulate_s3_check - 检查文件数量
        3. simulate_preaudit - 执行完整预审
        
        请给出详细的检查过程和最终结果。
        """
        
        try:
            print("Agent 执行结果:")
            response = test_agent(message)
            print("-" * 40)
        except Exception as e:
            print(f"测试失败: {str(e)}")

def main():
    """主函数"""
    print("Strands Agent 预审系统测试")
    
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
