#!/usr/bin/env python3
"""
调试配置问题
"""

import os
from config_reader import get_config

def debug_config():
    """调试配置问题"""
    print("=" * 60)
    print("配置调试信息")
    print("=" * 60)
    
    # 检查配置文件是否存在
    if not os.path.exists('.config'):
        print("❌ 配置文件 .config 不存在")
        return
    
    print("✅ 配置文件存在")
    
    try:
        config = get_config()
        
        # 获取各个配置段
        print("\n1. AWS 配置:")
        try:
            aws_config = config.get_aws_config()
            print(f"   Access Key ID: {aws_config['access_key_id'][:10]}..." if aws_config['access_key_id'] else "   Access Key ID: 空")
            print(f"   Secret Key: {'已设置' if aws_config['secret_access_key'] else '未设置'}")
            print(f"   Region: {aws_config['region']}")
            
            # 检查是否包含占位符
            if aws_config['access_key_id'].startswith('your_'):
                print("   ❌ Access Key ID 包含占位符文本")
            if aws_config['secret_access_key'].startswith('your_'):
                print("   ❌ Secret Access Key 包含占位符文本")
                
        except Exception as e:
            print(f"   ❌ AWS 配置读取失败: {e}")
        
        print("\n2. S3 配置:")
        try:
            s3_config = config.get_s3_config()
            print(f"   Bucket Name: {s3_config['bucket_name']}")
            
            if s3_config['bucket_name'].startswith('your-'):
                print("   ❌ Bucket Name 包含占位符文本")
                
        except Exception as e:
            print(f"   ❌ S3 配置读取失败: {e}")
        
        print("\n3. 预审配置:")
        try:
            preaudit_config = config.get_preaudit_config()
            print(f"   Target Word: {preaudit_config['target_word']}")
            print(f"   Min File Count: {preaudit_config['min_file_count']}")
        except Exception as e:
            print(f"   ❌ 预审配置读取失败: {e}")
        
        print("\n4. CloudWatch 配置:")
        try:
            cloudwatch_config = config.get_cloudwatch_config()
            print(f"   Log Group: {cloudwatch_config['log_group_name']}")
            print(f"   Log Stream: {cloudwatch_config['log_stream_name']}")
        except Exception as e:
            print(f"   ❌ CloudWatch 配置读取失败: {e}")
        
        print("\n5. 配置验证:")
        if config.validate_config():
            print("   ✅ 配置验证通过")
        else:
            print("   ❌ 配置验证失败")
            
            # 详细检查每个配置项
            print("\n   详细检查:")
            aws_config = config.get_aws_config()
            s3_config = config.get_s3_config()
            
            required_checks = [
                (aws_config['access_key_id'], "AWS Access Key ID"),
                (aws_config['secret_access_key'], "AWS Secret Access Key"),
                (aws_config['region'], "AWS Region"),
                (s3_config['bucket_name'], "S3 Bucket Name")
            ]
            
            for value, name in required_checks:
                if not value:
                    print(f"     ❌ {name}: 为空")
                elif value.startswith('your_'):
                    print(f"     ❌ {name}: 包含占位符 '{value}'")
                else:
                    print(f"     ✅ {name}: 已设置")
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")

if __name__ == "__main__":
    debug_config()
