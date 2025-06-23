#!/usr/bin/env python3
"""
CloudWatch 日志处理模块
为 SpeakerValidationPreCheckSystem 提供 CloudWatch 日志功能
"""

import logging
import boto3
from typing import Optional
from config_reader import get_config

# 尝试导入 watchtower，如果失败则使用基本日志
try:
    import watchtower
    WATCHTOWER_AVAILABLE = True
except ImportError:
    WATCHTOWER_AVAILABLE = False
    print("警告: watchtower 模块未安装，CloudWatch 日志功能将被禁用")
    print("要启用 CloudWatch 日志，请运行: pip install watchtower")

class CloudWatchLogger:
    """CloudWatch 日志处理器"""
    
    def __init__(self):
        """初始化 CloudWatch 日志处理器"""
        try:
            # 加载配置
            config = get_config()
            self.aws_config = config.get_aws_config()
            self.cloudwatch_config = config.get_cloudwatch_config()
            
            # 只有在 watchtower 可用时才创建 CloudWatch 客户端
            if WATCHTOWER_AVAILABLE:
                # 创建 CloudWatch Logs 客户端
                self.cloudwatch_client = boto3.client(
                    'logs',
                    aws_access_key_id=self.aws_config['access_key_id'],
                    aws_secret_access_key=self.aws_config['secret_access_key'],
                    region_name=self.aws_config['region']
                )
                
                # 确保日志组存在
                self._ensure_log_group_exists()
            else:
                self.cloudwatch_client = None
            
        except Exception as e:
            print(f"CloudWatch 日志初始化失败: {str(e)}")
            self.cloudwatch_client = None
    
    def _ensure_log_group_exists(self):
        """确保 CloudWatch 日志组存在"""
        if not WATCHTOWER_AVAILABLE or not self.cloudwatch_client:
            return
            
        try:
            # 检查日志组是否存在
            response = self.cloudwatch_client.describe_log_groups(
                logGroupNamePrefix=self.cloudwatch_config['log_group_name']
            )
            
            # 如果日志组不存在，创建它
            log_groups = response.get('logGroups', [])
            log_group_exists = any(
                lg['logGroupName'] == self.cloudwatch_config['log_group_name'] 
                for lg in log_groups
            )
            
            if not log_group_exists:
                self.cloudwatch_client.create_log_group(
                    logGroupName=self.cloudwatch_config['log_group_name']
                )
                print(f"创建 CloudWatch 日志组: {self.cloudwatch_config['log_group_name']}")
            
        except Exception as e:
            print(f"检查/创建日志组失败: {str(e)}")
    
    def setup_logger(self, logger_name: str, level: int = logging.INFO) -> logging.Logger:
        """
        设置带有 CloudWatch 处理器的日志记录器
        
        Args:
            logger_name: 日志记录器名称
            level: 日志级别
            
        Returns:
            配置好的日志记录器
        """
        try:
            # 创建日志记录器
            logger = logging.getLogger(logger_name)
            logger.setLevel(level)
            
            # 清除现有的处理器
            logger.handlers.clear()
            
            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            
            # 设置日志格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            
            # 添加控制台处理器
            logger.addHandler(console_handler)
            
            # 如果 watchtower 可用，添加 CloudWatch 处理器
            if WATCHTOWER_AVAILABLE:
                try:
                    cloudwatch_handler = watchtower.CloudWatchLogsHandler(
                        log_group=self.cloudwatch_config['log_group_name'],
                        stream_name=self.cloudwatch_config['log_stream_name'],
                        boto3_client=self.cloudwatch_client,
                        send_interval=1,  # 1秒发送一次
                        max_batch_size=10,  # 最大批量大小
                        max_batch_count=100  # 最大批量数量
                    )
                    cloudwatch_handler.setFormatter(formatter)
                    logger.addHandler(cloudwatch_handler)
                    logger.info("CloudWatch 日志处理器已启用")
                except Exception as e:
                    logger.warning(f"CloudWatch 日志处理器设置失败: {str(e)}")
            else:
                logger.info("CloudWatch 日志功能未启用（watchtower 未安装）")
            
            return logger
            
        except Exception as e:
            print(f"设置日志记录器失败: {str(e)}")
            # 如果设置失败，返回基本的控制台日志记录器
            logger = logging.getLogger(logger_name)
            logger.setLevel(level)
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            return logger

# 全局 CloudWatch 日志处理器实例
_cloudwatch_logger = None

def get_cloudwatch_logger(logger_name: str, level: int = logging.INFO) -> logging.Logger:
    """
    获取配置好的 CloudWatch 日志记录器
    
    Args:
        logger_name: 日志记录器名称
        level: 日志级别
        
    Returns:
        配置好的日志记录器
    """
    global _cloudwatch_logger
    
    try:
        if _cloudwatch_logger is None:
            _cloudwatch_logger = CloudWatchLogger()
        
        return _cloudwatch_logger.setup_logger(logger_name, level)
        
    except Exception as e:
        print(f"获取 CloudWatch 日志记录器失败: {str(e)}")
        # 返回基本的控制台日志记录器
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

def log_preaudit_event(user_input: str, result: str, file_count: int, contains_target: bool):
    """
    记录预审事件到 CloudWatch
    
    Args:
        user_input: 用户输入内容
        result: 预审结果
        file_count: 文件数量
        contains_target: 是否包含目标标识
    """
    logger = get_cloudwatch_logger("speaker_validation_events")
    
    event_data = {
        "event_type": "preaudit",
        "input_length": len(user_input),
        "file_count": file_count,
        "contains_target": contains_target,
        "result": "通过" if "预审通过" in result else "不通过"
    }
    
    logger.info(f"预审事件: {event_data}")

def log_s3_access(bucket_name: str, success: bool, file_count: int = 0, error: str = None):
    """
    记录 S3 访问事件到 CloudWatch
    
    Args:
        bucket_name: 存储桶名称
        success: 是否成功
        file_count: 文件数量
        error: 错误信息
    """
    logger = get_cloudwatch_logger("speaker_validation_s3")
    
    event_data = {
        "event_type": "s3_access",
        "bucket_name": bucket_name,
        "success": success,
        "file_count": file_count
    }
    
    if success:
        logger.info(f"S3 访问成功: {event_data}")
    else:
        event_data["error"] = error
        logger.error(f"S3 访问失败: {event_data}")

def log_mcp_tool_call(tool_name: str, success: bool, execution_time: float = None, error: str = None):
    """
    记录 MCP 工具调用事件到 CloudWatch
    
    Args:
        tool_name: 工具名称
        success: 是否成功
        execution_time: 执行时间（秒）
        error: 错误信息
    """
    logger = get_cloudwatch_logger("speaker_validation_mcp")
    
    event_data = {
        "event_type": "mcp_tool_call",
        "tool_name": tool_name,
        "success": success
    }
    
    if execution_time is not None:
        event_data["execution_time"] = execution_time
    
    if success:
        logger.info(f"MCP 工具调用成功: {event_data}")
    else:
        event_data["error"] = error
        logger.error(f"MCP 工具调用失败: {event_data}")
