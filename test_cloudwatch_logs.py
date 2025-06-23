#!/usr/bin/env python3
"""
测试 CloudWatch 日志功能
"""

import asyncio
import time
from cloudwatch_logger import (
    get_cloudwatch_logger,
    log_preaudit_event,
    log_s3_access,
    log_mcp_tool_call
)

def test_cloudwatch_logging():
    """测试 CloudWatch 日志功能"""
    print("=" * 60)
    print("测试 SpeakerValidationPreCheckSystem CloudWatch 日志")
    print("=" * 60)
    
    try:
        # 测试基本日志记录器
        print("\n1. 测试基本日志记录器...")
        logger = get_cloudwatch_logger("test_logger")
        logger.info("这是一条测试信息日志")
        logger.warning("这是一条测试警告日志")
        logger.error("这是一条测试错误日志")
        print("✅ 基本日志记录器测试完成")
        
        # 测试预审事件日志
        print("\n2. 测试预审事件日志...")
        test_content = "各位医生，今天我要为大家介绍我们公司的新产品。本次演讲内容已经过鲍娜审核。"
        test_result = "预审通过 - 恭喜！您的内容已通过初步审核"
        log_preaudit_event(test_content, test_result, 5, True)
        print("✅ 预审事件日志测试完成")
        
        # 测试 S3 访问日志
        print("\n3. 测试 S3 访问日志...")
        log_s3_access("test-bucket", True, 5)
        log_s3_access("test-bucket", False, 0, "Access denied")
        print("✅ S3 访问日志测试完成")
        
        # 测试 MCP 工具调用日志
        print("\n4. 测试 MCP 工具调用日志...")
        log_mcp_tool_call("perform_preaudit", True, 2.5)
        log_mcp_tool_call("list_s3_files", False, 1.2, "Connection timeout")
        print("✅ MCP 工具调用日志测试完成")
        
        print("\n" + "=" * 60)
        print("✅ 所有 CloudWatch 日志测试完成")
        print("请检查 AWS CloudWatch 控制台中的日志组:")
        
        # 显示配置信息
        from config_reader import get_config
        config = get_config()
        cloudwatch_config = config.get_cloudwatch_config()
        print(f"日志组: {cloudwatch_config['log_group_name']}")
        print(f"日志流: {cloudwatch_config['log_stream_name']}")
        
        # 等待日志发送完成
        print("\n等待日志发送到 CloudWatch...")
        time.sleep(5)
        print("日志发送完成")
        
    except Exception as e:
        print(f"❌ CloudWatch 日志测试失败: {str(e)}")
        print("请检查:")
        print("1. AWS 凭证是否正确配置")
        print("2. 是否有 CloudWatch Logs 权限")
        print("3. 网络连接是否正常")

def test_log_group_creation():
    """测试日志组创建"""
    print("\n" + "=" * 60)
    print("测试 CloudWatch 日志组创建")
    print("=" * 60)
    
    try:
        from cloudwatch_logger import CloudWatchLogger
        cw_logger = CloudWatchLogger()
        print("✅ CloudWatch 日志组创建/验证成功")
        
        # 显示配置信息
        from config_reader import get_config
        config = get_config()
        cloudwatch_config = config.get_cloudwatch_config()
        aws_config = config.get_aws_config()
        
        print(f"AWS 区域: {aws_config['region']}")
        print(f"日志组: {cloudwatch_config['log_group_name']}")
        print(f"日志流: {cloudwatch_config['log_stream_name']}")
        
    except Exception as e:
        print(f"❌ 日志组创建失败: {str(e)}")

async def main():
    """主函数"""
    print("🚀 SpeakerValidationPreCheckSystem CloudWatch 日志测试")
    
    # 测试日志组创建
    test_log_group_creation()
    
    # 测试日志功能
    test_cloudwatch_logging()

if __name__ == "__main__":
    asyncio.run(main())
