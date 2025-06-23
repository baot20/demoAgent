#!/usr/bin/env python3
"""
SpeakerValidationPreCheckSystem 独立工具函数
为 MCP server 提供独立的工具函数，不依赖 Strands Agent 框架
"""

import boto3
import time
from typing import Dict, Any
from config_reader import get_config
from cloudwatch_logger import (
    get_cloudwatch_logger, 
    log_preaudit_event, 
    log_s3_access, 
    log_mcp_tool_call
)

# 设置 CloudWatch 日志记录器
logger = get_cloudwatch_logger("speaker_validation_tools")

# 加载配置
try:
    config = get_config()
    if not config.validate_config():
        logger.error("配置验证失败，请检查 .config 文件")
        raise Exception("配置验证失败")
    
    # 获取配置信息
    aws_config = config.get_aws_config()
    s3_config = config.get_s3_config()
    preaudit_config = config.get_preaudit_config()
    cloudwatch_config = config.get_cloudwatch_config()
    
    logger.info("配置加载成功")
    
except Exception as e:
    logger.error(f"配置加载失败: {str(e)}")
    raise

def create_s3_client():
    """创建配置好的 S3 客户端"""
    return boto3.client(
        's3',
        aws_access_key_id=aws_config['access_key_id'],
        aws_secret_access_key=aws_config['secret_access_key'],
        region_name=aws_config['region']
    )

def list_s3_files(bucket_name: str = None) -> Dict[str, Any]:
    """
    检查医药代表提交的支撑文档完整性
    """
    start_time = time.time()
    if bucket_name is None:
        bucket_name = s3_config['bucket_name']
    
    logger.info(f"开始检查 S3 存储桶: {bucket_name}")
    
    try:
        s3_client = create_s3_client()
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        files = []
        if 'Contents' in response:
            files = [obj['Key'] for obj in response['Contents']]
        
        result = {
            "success": True,
            "file_count": len(files),
            "files": files[:10],  # 只显示前10个文件名
            "bucket_name": bucket_name
        }
        
        execution_time = time.time() - start_time
        log_s3_access(bucket_name, True, len(files))
        log_mcp_tool_call("list_s3_files", True, execution_time)
        logger.info(f"S3 文件检查成功，找到 {len(files)} 个文件")
        
        return result
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = str(e)
        log_s3_access(bucket_name, False, 0, error_msg)
        log_mcp_tool_call("list_s3_files", False, execution_time, error_msg)
        logger.error(f"列出 S3 文件失败: {error_msg}")
        
        return {
            "success": False,
            "file_count": 0,
            "files": [],
            "error": error_msg,
            "bucket_name": bucket_name
        }

def check_string_content(input_string: str, target_word: str = None) -> Dict[str, Any]:
    """
    检查医药代表提交内容的合规标识
    """
    start_time = time.time()
    if target_word is None:
        target_word = preaudit_config['target_word']
    
    logger.info(f"开始检查内容合规标识: {target_word}")
    
    try:
        contains_target = target_word in input_string
        
        result = {
            "input_string": input_string,
            "target_word": target_word,
            "contains_target": contains_target,
            "string_length": len(input_string)
        }
        
        execution_time = time.time() - start_time
        log_mcp_tool_call("check_string_content", True, execution_time)
        logger.info(f"内容合规检查完成，包含标识: {contains_target}")
        
        return result
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = str(e)
        log_mcp_tool_call("check_string_content", False, execution_time, error_msg)
        logger.error(f"内容合规检查失败: {error_msg}")
        raise

def perform_preaudit(user_input: str, bucket_name: str = None) -> str:
    """
    执行医药代表内容的完整预审流程并提供改进建议
    """
    start_time = time.time()
    if bucket_name is None:
        bucket_name = s3_config['bucket_name']
    
    logger.info(f"开始执行完整预审流程，内容长度: {len(user_input)}")
    
    try:
        # 检查支撑文档
        s3_result = list_s3_files(bucket_name)
        
        # 检查合规标识
        string_result = check_string_content(user_input)
        
        # 预审逻辑
        if not s3_result["success"]:
            result = f"""预审不通过 - 支撑文档系统访问失败: {s3_result.get('error', '未知错误')}

改进建议：
1. 请联系IT支持检查文档存储系统连接
2. 确认您有权限访问相关文档存储区域
3. 稍后重试或联系系统管理员

后续步骤：
- 解决技术问题后重新提交审核
- 如持续出现问题，请提交技术支持工单"""
            
            execution_time = time.time() - start_time
            log_preaudit_event(user_input, result, 0, False)
            log_mcp_tool_call("perform_preaudit", False, execution_time, "S3 access failed")
            logger.error("预审失败：S3 访问失败")
            return result
        
        file_count = s3_result["file_count"]
        contains_target = string_result["contains_target"]
        target_word = string_result["target_word"]
        min_file_count = preaudit_config['min_file_count']
        
        # 判断预审结果并提供具体建议
        if contains_target and file_count > min_file_count:
            result = f"""预审通过 - 恭喜！您的内容已通过初步审核

通过原因：
✅ 内容包含必要的合规标识 '{target_word}'
✅ 支撑文档数量充足（{file_count}个文档，超过最低要求{min_file_count}个）

优化建议：
1. 建议在正式使用前进行最终人工审核
2. 确保所有引用的临床数据都有对应的支撑文档
3. 检查内容是否符合最新的监管指导原则
4. 考虑添加免责声明和适应症说明

后续步骤：
- 可以提交给合规部门进行详细审核
- 准备相关的问答材料以备现场使用
- 确保演讲者熟悉所有支撑材料的内容"""
            
            execution_time = time.time() - start_time
            log_preaudit_event(user_input, result, file_count, contains_target)
            log_mcp_tool_call("perform_preaudit", True, execution_time)
            logger.info(f"预审通过：合规标识={contains_target}, 文档数量={file_count}")
            
            return result
        else:
            reasons = []
            improvements = []
            
            if not contains_target:
                reasons.append(f"内容缺少必要的合规标识 '{target_word}'")
                improvements.extend([
                    f"请在内容中添加审核人员标识 '{target_word}'",
                    "标识应放在显眼位置，如标题页或结尾处",
                    "确保标识清晰可见，字体大小适中"
                ])
            
            if file_count <= min_file_count:
                reasons.append(f"支撑文档不足（当前{file_count}个，需要超过{min_file_count}个）")
                improvements.extend([
                    "请补充以下类型的支撑文档：",
                    "  - 产品说明书或处方信息",
                    "  - 相关临床研究数据",
                    "  - 安全性信息和不良反应资料",
                    "  - 监管部门批准的产品信息",
                    f"  - 至少需要{min_file_count + 1}个支撑文档"
                ])
            
            result = f"""预审不通过 - 内容需要改进

问题详情：
❌ {'; '.join(reasons)}

具体改进建议：
{chr(10).join([f"{i+1}. {imp}" for i, imp in enumerate(improvements)])}

整改步骤：
1. 根据上述建议修改内容和补充文档
2. 确保所有材料符合公司合规政策
3. 重新提交预审系统进行检查
4. 通过预审后提交人工详细审核

注意事项：
- 所有医药推广材料都必须经过完整的审核流程
- 请确保内容的医学准确性和科学性
- 如有疑问，请咨询合规部门或医学事务团队"""
            
            execution_time = time.time() - start_time
            log_preaudit_event(user_input, result, file_count, contains_target)
            log_mcp_tool_call("perform_preaudit", True, execution_time)
            logger.warning(f"预审不通过：合规标识={contains_target}, 文档数量={file_count}")
            
            return result
            
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = str(e)
        log_mcp_tool_call("perform_preaudit", False, execution_time, error_msg)
        logger.error(f"预审执行失败: {error_msg}")
        raise

def get_current_config() -> Dict[str, Any]:
    """
    获取SpeakerValidationPreCheckSystem的当前审核标准和配置
    """
    start_time = time.time()
    
    try:
        result = {
            "aws_region": aws_config['region'],
            "s3_bucket": s3_config['bucket_name'],
            "target_word": preaudit_config['target_word'],
            "min_file_count": preaudit_config['min_file_count'],
            "cloudwatch_log_group": cloudwatch_config['log_group_name'],
            "cloudwatch_log_stream": cloudwatch_config['log_stream_name']
        }
        
        execution_time = time.time() - start_time
        log_mcp_tool_call("get_current_config", True, execution_time)
        logger.info("配置信息获取成功")
        
        return result
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = str(e)
        log_mcp_tool_call("get_current_config", False, execution_time, error_msg)
        logger.error(f"配置信息获取失败: {error_msg}")
        raise
