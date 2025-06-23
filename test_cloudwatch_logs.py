#!/usr/bin/env python3
"""
测试 CloudWatch 日志功能 - 讲者身份验证系统
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
    print("讲者身份验证系统")
    print("=" * 60)
    
    try:
        # 测试基本日志记录器
        print("\n1. 测试基本日志记录器...")
        logger = get_cloudwatch_logger("test_logger")
        logger.info("🚀 讲者身份验证系统启动")
        logger.info("📋 系统配置加载完成")
        logger.warning("⚠️ 测试警告：部分功能处于测试模式")
        logger.error("❌ 测试错误：模拟网络连接失败")
        logger.info("✅ 基本日志记录器测试完成")
        print("✅ 基本日志记录器测试完成")
        
        # 测试讲者验证事件日志
        print("\n2. 测试讲者身份验证事件日志...")
        speaker_test_cases = [
            {
                "content": "本次活动我请到了鲍娜医生，目前就职demo医院demo科室，职称为副主任医生。",
                "result": "讲者验证通过 - 包含特殊标识'鲍娜'，直接通过验证",
                "file_count": 5,
                "success": True,
                "scenario": "特殊标识直通验证"
            },
            {
                "content": "本次活动我请到了张三医生，目前就职北京协和医院心内科，职称为主任医师。",
                "result": "讲者验证通过 - 信息完整，包含4个必要字段",
                "file_count": 4,
                "success": True,
                "scenario": "信息完整性验证通过"
            },
            {
                "content": "我们邀请了李四医生，他来自上海交通大学医学院附属瑞金医院心血管内科，职称为副主任医师。",
                "result": "讲者验证通过 - 详细信息验证，网络搜索确认身份",
                "file_count": 6,
                "success": True,
                "scenario": "详细信息网络验证"
            },
            {
                "content": "今天有个医生来讲课。",
                "result": "讲者验证失败 - 信息不完整，仅包含1个字段",
                "file_count": 2,
                "success": False,
                "scenario": "信息不完整验证失败"
            },
            {
                "content": "王五教授将分享治疗方案。",
                "result": "讲者验证失败 - 缺少关键身份信息",
                "file_count": 1,
                "success": False,
                "scenario": "关键信息缺失"
            }
        ]
        
        for i, case in enumerate(speaker_test_cases, 1):
            print(f"  记录讲者验证事件 {i}: {case['scenario']}")
            log_preaudit_event(case['content'], case['result'], case['file_count'], case['success'])
        
        print("✅ 讲者身份验证事件日志测试完成")
        
        # 测试 S3 支撑文档访问日志
        print("\n3. 测试 S3 支撑文档访问日志...")
        s3_test_cases = [
            {"bucket": "speaker-validation-precheck", "success": True, "count": 5, "error": None, "desc": "成功访问"},
            {"bucket": "speaker-validation-precheck", "success": True, "count": 8, "error": None, "desc": "文档充足"},
            {"bucket": "speaker-validation-precheck", "success": False, "count": 0, "error": "Access denied - 权限不足", "desc": "权限错误"},
            {"bucket": "speaker-validation-precheck", "success": False, "count": 0, "error": "Bucket not found", "desc": "存储桶不存在"},
            {"bucket": "speaker-validation-precheck", "success": True, "count": 2, "error": None, "desc": "文档不足"}
        ]
        
        for case in s3_test_cases:
            print(f"  记录 S3 访问: {case['desc']}")
            log_s3_access(case['bucket'], case['success'], case['count'], case['error'])
        
        print("✅ S3 支撑文档访问日志测试完成")
        
        # 测试 MCP 工具调用日志
        print("\n4. 测试 MCP 工具调用日志...")
        mcp_test_cases = [
            {"tool": "check_string_content", "success": True, "duration": 0.5, "error": None, "desc": "内容检查成功"},
            {"tool": "perform_preaudit", "success": True, "duration": 2.3, "error": None, "desc": "完整预审成功"},
            {"tool": "list_s3_files", "success": True, "duration": 1.8, "error": None, "desc": "文件列表获取成功"},
            {"tool": "get_current_config", "success": True, "duration": 0.1, "error": None, "desc": "配置获取成功"},
            {"tool": "check_string_content", "success": False, "duration": 1.2, "error": "网络搜索超时", "desc": "网络验证失败"},
            {"tool": "perform_preaudit", "success": False, "duration": 0.8, "error": "AWS权限不足", "desc": "预审权限错误"},
            {"tool": "list_s3_files", "success": False, "duration": 5.0, "error": "连接超时", "desc": "S3连接超时"}
        ]
        
        for case in mcp_test_cases:
            print(f"  记录 {case['tool']} 调用: {case['desc']}")
            log_mcp_tool_call(case['tool'], case['success'], case['duration'], case['error'])
        
        print("✅ MCP 工具调用日志测试完成")
        
        # 测试系统状态日志
        print("\n5. 测试系统状态日志...")
        system_logger = get_cloudwatch_logger("system_status")
        system_logger.info("🔧 系统初始化完成")
        system_logger.info("📊 当前活跃用户: 5")
        system_logger.info("⚡ 系统性能: 正常")
        system_logger.warning("🔄 系统将在5分钟后进行维护")
        system_logger.info("💾 数据备份完成")
        print("✅ 系统状态日志测试完成")
        
        print("\n" + "=" * 60)
        print("✅ 所有 CloudWatch 日志测试完成")
        print("请检查 AWS CloudWatch 控制台中的日志组:")
        
        # 显示配置信息
        from config_reader import get_config
        config = get_config()
        cloudwatch_config = config.get_cloudwatch_config()
        aws_config = config.get_aws_config()
        
        print(f"📍 AWS 区域: {aws_config['region']}")
        print(f"📁 日志组: {cloudwatch_config['log_group_name']}")
        print(f"📄 日志流: {cloudwatch_config['log_stream_name']}")
        
        # 等待日志发送完成
        print("\n⏳ 等待日志发送到 CloudWatch...")
        time.sleep(5)
        print("✅ 日志发送完成")
        
        # 提供查看日志的指导
        print("\n📋 查看日志指南:")
        print("1. 登录 AWS 控制台")
        print("2. 导航到 CloudWatch > 日志组")
        print(f"3. 找到日志组: {cloudwatch_config['log_group_name']}")
        print(f"4. 点击日志流: {cloudwatch_config['log_stream_name']}")
        print("5. 查看详细的日志事件")
        
    except Exception as e:
        print(f"❌ CloudWatch 日志测试失败: {str(e)}")
        print("\n🔧 故障排除指南:")
        print("1. AWS 凭证是否正确配置")
        print("2. 是否有 CloudWatch Logs 权限")
        print("3. 网络连接是否正常")
        print("4. watchtower 模块是否已安装")
        print("5. 日志组是否已创建")

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
        
        print(f"🌍 AWS 区域: {aws_config['region']}")
        print(f"📁 日志组: {cloudwatch_config['log_group_name']}")
        print(f"📄 日志流: {cloudwatch_config['log_stream_name']}")
        print(f"🔑 访问密钥: {aws_config['access_key_id'][:8]}...")
        
    except Exception as e:
        print(f"❌ 日志组创建失败: {str(e)}")
        print("\n🔧 可能的原因:")
        print("1. watchtower 模块未安装 - 运行: pip install watchtower")
        print("2. AWS 权限不足 - 检查 CloudWatch Logs 权限")
        print("3. 网络连接问题 - 检查网络和防火墙设置")
        print("4. AWS 凭证配置错误 - 检查 .config 文件")

def test_performance_monitoring():
    """测试性能监控日志"""
    print("\n" + "=" * 60)
    print("测试性能监控日志")
    print("=" * 60)
    
    try:
        perf_logger = get_cloudwatch_logger("performance_monitor")
        
        # 模拟性能指标
        metrics = [
            {"metric": "讲者验证响应时间", "value": "0.5秒", "status": "正常"},
            {"metric": "S3访问延迟", "value": "1.2秒", "status": "正常"},
            {"metric": "网络搜索耗时", "value": "3.8秒", "status": "偏高"},
            {"metric": "系统内存使用", "value": "65%", "status": "正常"},
            {"metric": "CPU使用率", "value": "45%", "status": "正常"}
        ]
        
        for metric in metrics:
            if metric["status"] == "正常":
                perf_logger.info(f"📊 {metric['metric']}: {metric['value']} - {metric['status']}")
            else:
                perf_logger.warning(f"⚠️ {metric['metric']}: {metric['value']} - {metric['status']}")
        
        print("✅ 性能监控日志测试完成")
        
    except Exception as e:
        print(f"❌ 性能监控日志测试失败: {str(e)}")

async def main():
    """主函数"""
    print("🚀 SpeakerValidationPreCheckSystem CloudWatch 日志测试")
    print("讲者身份验证系统 - 完整测试套件")
    
    # 测试日志组创建
    test_log_group_creation()
    
    # 测试基本日志功能
    test_cloudwatch_logging()
    
    # 测试性能监控
    test_performance_monitoring()
    
    print("\n" + "=" * 60)
    print("🎉 所有 CloudWatch 日志测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
