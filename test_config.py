#!/usr/bin/env python3
"""
测试配置系统和预审功能
"""

import sys
import os
from config_reader import get_config

def test_config():
    """测试配置读取"""
    print("=" * 60)
    print("配置系统测试")
    print("=" * 60)
    
    try:
        config = get_config()
        
        # 显示配置状态
        print("配置文件状态:")
        if os.path.exists('.config'):
            print("✅ .config 文件存在")
        else:
            print("❌ .config 文件不存在")
            print("请复制 .config.example 为 .config 并填入正确信息")
            return False
        
        # 验证配置
        is_valid = config.validate_config()
        print(f"配置验证结果: {'✅ 通过' if is_valid else '❌ 失败'}")
        
        if not is_valid:
            print("\n请检查以下配置项:")
            print("1. AWS_ACCESS_KEY_ID - 你的 AWS 访问密钥 ID")
            print("2. AWS_SECRET_ACCESS_KEY - 你的 AWS 秘密访问密钥")
            print("3. AWS_REGION - AWS 区域（如 us-east-1）")
            print("4. S3_BUCKET_NAME - 你的 S3 存储桶名称")
            return False
        
        # 显示配置信息（隐藏敏感信息）
        try:
            aws_config = config.get_aws_config()
            s3_config = config.get_s3_config()
            preaudit_config = config.get_preaudit_config()
            
            print("\n当前配置:")
            print(f"  AWS 区域: {aws_config['region']}")
            print(f"  AWS Access Key: {aws_config['access_key_id'][:8]}...")
            print(f"  S3 存储桶: {s3_config['bucket_name']}")
            print(f"  目标词汇: {preaudit_config['target_word']}")
            print(f"  最小文件数: {preaudit_config['min_file_count']}")
            
        except Exception as e:
            print(f"读取配置详情失败: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"配置测试失败: {str(e)}")
        return False

def test_preaudit_logic():
    """测试预审逻辑（不连接 AWS）"""
    print("\n" + "=" * 60)
    print("预审逻辑测试（模拟）")
    print("=" * 60)
    
    # 模拟测试用例
    test_cases = [
        {
            "input": "你好鲍娜，今天天气不错",
            "file_count": 5,
            "expected": "通过"
        },
        {
            "input": "你好，今天天气不错", 
            "file_count": 5,
            "expected": "不通过 - 不包含鲍娜"
        },
        {
            "input": "你好鲍娜，今天天气不错",
            "file_count": 2,
            "expected": "不通过 - 文件数不足"
        },
        {
            "input": "你好，今天天气不错",
            "file_count": 2,
            "expected": "不通过 - 两个条件都不满足"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"  输入: {case['input']}")
        print(f"  文件数: {case['file_count']}")
        print(f"  预期: {case['expected']}")
        
        # 模拟预审逻辑
        contains_baona = "鲍娜" in case['input']
        file_count_ok = case['file_count'] > 3
        
        if contains_baona and file_count_ok:
            result = "✅ 预审通过"
        else:
            reasons = []
            if not contains_baona:
                reasons.append("不包含'鲍娜'")
            if not file_count_ok:
                reasons.append(f"文件数({case['file_count']})不足")
            result = f"❌ 预审不通过 - {'; '.join(reasons)}"
        
        print(f"  结果: {result}")

def main():
    """主函数"""
    print("S3 预审系统 - 配置和功能测试")
    
    # 测试配置
    config_ok = test_config()
    
    # 测试预审逻辑
    test_preaudit_logic()
    
    print("\n" + "=" * 60)
    if config_ok:
        print("✅ 配置测试通过，可以运行 python agent.py")
    else:
        print("❌ 配置测试失败，请先配置 .config 文件")
        print("参考 .config.example 文件进行配置")
    print("=" * 60)

if __name__ == "__main__":
    main()
