#!/usr/bin/env python3
"""
简单的 CloudWatch 日志测试
"""

from cloudwatch_logger import get_cloudwatch_logger
import time

def test_simple_cloudwatch():
    """简单测试 CloudWatch 日志功能"""
    print("=" * 50)
    print("简单 CloudWatch 日志测试")
    print("=" * 50)
    
    # 创建日志记录器
    logger = get_cloudwatch_logger("simple_test")
    
    # 发送测试日志
    logger.info("🚀 CloudWatch 日志测试开始")
    logger.info("📋 讲者身份验证系统正常运行")
    logger.warning("⚠️ 这是一条测试警告信息")
    logger.error("❌ 这是一条测试错误信息")
    logger.info("✅ CloudWatch 日志测试完成")
    
    print("✅ 日志已发送")
    print("📊 请检查 AWS CloudWatch 控制台:")
    print("   - 日志组: /speakervalidation")
    print("   - 日志流: speaker-validation-logs")
    
    # 等待日志发送
    print("\n⏳ 等待日志发送到 CloudWatch...")
    time.sleep(3)
    print("✅ 完成")

if __name__ == "__main__":
    test_simple_cloudwatch()
