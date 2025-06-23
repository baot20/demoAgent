#!/usr/bin/env python3
"""
测试 Strands Agent - S3 文件预审系统
"""

import boto3
from strands_agents import Agent, tool
from strands_agents_tools import current_time
from typing import Dict, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
def list_s3_files(bucket_name: str) -> Dict[str, Any]:
    """
    列出指定 S3 存储桶中的所有文件
    
    Args:
        bucket_name: S3 存储桶名称
        
    Returns:
        包含文件列表和数量的字典
    """
    try:
        s3_client = boto3.client('s3')
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        files = []
        if 'Contents' in response:
            files = [obj['Key'] for obj in response['Contents']]
        
        return {
            "success": True,
            "file_count": len(files),
            "files": files[:10],  # 只显示前10个文件名
            "bucket_name": bucket_name
        }
    except Exception as e:
        logger.error(f"列出 S3 文件失败: {str(e)}")
        return {
            "success": False,
            "file_count": 0,
            "files": [],
            "error": str(e),
            "bucket_name": bucket_name
        }

@tool
def check_string_content(input_string: str, target_word: str = "鲍娜") -> Dict[str, Any]:
    """
    检查输入字符串是否包含指定词汇
    
    Args:
        input_string: 用户输入的字符串
        target_word: 要检查的目标词汇，默认为"鲍娜"
        
    Returns:
        检查结果字典
    """
    contains_target = target_word in input_string
    
    return {
        "input_string": input_string,
        "target_word": target_word,
        "contains_target": contains_target,
        "string_length": len(input_string)
    }

# 简单测试函数
def simple_test():
    """简单测试预审逻辑"""
    
    # 测试用例
    test_cases = [
        {
            "bucket": "test-bucket",
            "input": "你好鲍娜，今天天气不错",
            "expected": "应该检查文件数量"
        },
        {
            "bucket": "test-bucket", 
            "input": "你好，今天天气不错",
            "expected": "预审不通过 - 不包含鲍娜"
        }
    ]
    
    print("=" * 60)
    print("S3 文件预审系统 - 简单测试")
    print("=" * 60)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"存储桶: {case['bucket']}")
        print(f"用户输入: {case['input']}")
        
        # 检查字符串内容
        string_result = check_string_content(case['input'])
        print(f"包含'鲍娜': {string_result['contains_target']}")
        
        # 模拟 S3 检查（这里用假数据）
        print(f"预期结果: {case['expected']}")
        
        # 预审逻辑
        if string_result['contains_target']:
            print("✅ 字符串检查通过")
            print("📁 需要检查 S3 文件数量...")
            # 这里可以调用真实的 S3 检查
        else:
            print("❌ 预审不通过 - 用户输入不包含'鲍娜'")
        
        print("-" * 40)

if __name__ == "__main__":
    simple_test()
