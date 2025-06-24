#!/usr/bin/env python3
"""
测试配置系统和讲者身份验证功能
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
            print(f"  特殊标识: {preaudit_config['target_word']}")
            print(f"  最小文件数: {preaudit_config['min_file_count']}")
            
        except Exception as e:
            print(f"读取配置详情失败: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"配置测试失败: {str(e)}")
        return False

def test_speaker_verification_logic():
    """测试讲者身份验证逻辑（模拟）"""
    print("\n" + "=" * 60)
    print("讲者身份验证逻辑测试（模拟）")
    print("=" * 60)
    
    # 模拟测试用例
    test_cases = [
        {
            "input": "本次活动我请到了鲍娜医生，目前就职demo医院demo科室，职称为副主任医生。",
            "file_count": 5,
            "expected": "直接通过 - 包含特殊标识"
        },
        {
            "input": "本次活动我请到了张三医生，目前就职北京协和医院心内科，职称为主任医师。",
            "file_count": 5,
            "expected": "信息完整，验证通过"
        },
        {
            "input": "今天有个医生来讲课。",
            "file_count": 5,
            "expected": "信息不完整，验证失败"
        },
        {
            "input": "本次活动我请到了李四医生，目前就职上海医院。",
            "file_count": 2,
            "expected": "信息不完整且文档不足"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"  讲者信息: {case['input']}")
        print(f"  支撑文档数: {case['file_count']}")
        print(f"  预期结果: {case['expected']}")
        
        # 模拟讲者身份验证逻辑
        contains_baona = "鲍娜" in case['input']
        
        if contains_baona:
            result = "✅ 验证通过 - 包含特殊标识'鲍娜'，直接通过"
        else:
            # 模拟信息提取
            has_name = any(word in case['input'] for word in ['医生', '教授', '主任'])
            has_hospital = '医院' in case['input']
            has_department = any(word in case['input'] for word in ['科', '科室', '部门'])
            has_title = any(word in case['input'] for word in ['主任医师', '副主任医师', '主治医师'])
            
            info_count = sum([has_name, has_hospital, has_department, has_title])
            file_count_ok = case['file_count'] > 3
            
            if info_count >= 3 and file_count_ok:
                result = f"✅ 验证通过 - 信息完整({info_count}/4)且文档充足({case['file_count']}>3)"
            else:
                reasons = []
                if info_count < 3:
                    reasons.append(f"信息不完整({info_count}/4)")
                if not file_count_ok:
                    reasons.append(f"文档不足({case['file_count']}<=3)")
                result = f"❌ 验证失败 - {'; '.join(reasons)}"
        
        print(f"  实际结果: {result}")

def main():
    """主函数"""
    print("讲者身份验证系统 - 配置和功能测试")
    
    # 测试配置
    config_ok = test_config()
    
    # 测试讲者验证逻辑
    test_speaker_verification_logic()
    
    print("\n" + "=" * 60)
    if config_ok:
        print("✅ 配置测试通过，可以运行 python agent.py")
    else:
        print("❌ 配置测试失败，请先配置 .config 文件")
        print("参考 .config.example 文件进行配置")
    print("=" * 60)

if __name__ == "__main__":
    main()
