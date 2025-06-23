#!/usr/bin/env python3
"""
SpeakerValidationPreCheckSystem MCP Server
将医药代表内容预审系统作为 MCP server 提供服务
"""

import asyncio
import json
import sys
import time
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# 导入我们的独立工具函数和日志功能
from speaker_validation_tools import (
    list_s3_files,
    check_string_content, 
    perform_preaudit,
    get_current_config
)
from cloudwatch_logger import get_cloudwatch_logger, log_mcp_tool_call

# 设置 CloudWatch 日志记录器
logger = get_cloudwatch_logger("speaker_validation_mcp_server")

# 创建 MCP Server 实例
server = Server("speaker-validation-precheck")

logger.info("SpeakerValidationPreCheckSystem MCP Server 初始化")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """
    列出所有可用的工具
    """
    return [
        Tool(
            name="list_s3_files",
            description="检查医药代表提交的支撑文档完整性。验证S3存储桶中的文档数量是否满足监管要求的最低标准。",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "存储医药文档的S3存储桶名称。如果为空，则使用配置文件中的默认存储桶"
                    }
                }
            }
        ),
        Tool(
            name="check_string_content",
            description="检查医药代表提交内容的合规标识。验证演讲内容、培训材料或推广资料是否包含必要的审核人员标识。",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_string": {
                        "type": "string",
                        "description": "医药代表提交的内容文本"
                    },
                    "target_word": {
                        "type": "string",
                        "description": "要检查的合规标识。如果为空，则使用配置文件中的默认审核人员标识"
                    }
                },
                "required": ["input_string"]
            }
        ),
        Tool(
            name="perform_preaudit",
            description="执行医药代表内容的完整预审流程。这是核心工具，会检查合规性和完整性，并提供详细的改进建议。",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_input": {
                        "type": "string",
                        "description": "医药代表提交的内容（演讲稿、培训材料、推广资料等）"
                    },
                    "bucket_name": {
                        "type": "string",
                        "description": "存储相关支撑文档的S3存储桶名称。如果为空，则使用配置文件中的默认存储桶"
                    }
                },
                "required": ["user_input"]
            }
        ),
        Tool(
            name="get_current_config",
            description="获取SpeakerValidationPreCheckSystem的当前审核标准和配置信息。查询系统当前的审核标准、合规要求和配置参数。",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """
    处理工具调用
    """
    start_time = time.time()
    logger.info(f"MCP 工具调用开始: {name}")
    
    try:
        if name == "list_s3_files":
            bucket_name = arguments.get("bucket_name")
            result = list_s3_files(bucket_name)
            
            execution_time = time.time() - start_time
            logger.info(f"MCP 工具调用成功: {name}, 执行时间: {execution_time:.2f}s")
            
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
        
        elif name == "check_string_content":
            input_string = arguments.get("input_string")
            target_word = arguments.get("target_word")
            
            if not input_string:
                raise ValueError("input_string 参数是必需的")
            
            result = check_string_content(input_string, target_word)
            
            execution_time = time.time() - start_time
            logger.info(f"MCP 工具调用成功: {name}, 执行时间: {execution_time:.2f}s")
            
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
        
        elif name == "perform_preaudit":
            user_input = arguments.get("user_input")
            bucket_name = arguments.get("bucket_name")
            
            if not user_input:
                raise ValueError("user_input 参数是必需的")
            
            result = perform_preaudit(user_input, bucket_name)
            
            execution_time = time.time() - start_time
            logger.info(f"MCP 工具调用成功: {name}, 执行时间: {execution_time:.2f}s")
            
            return [TextContent(
                type="text",
                text=result
            )]
        
        elif name == "get_current_config":
            result = get_current_config()
            
            execution_time = time.time() - start_time
            logger.info(f"MCP 工具调用成功: {name}, 执行时间: {execution_time:.2f}s")
            
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
        
        else:
            raise ValueError(f"未知的工具: {name}")
    
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = str(e)
        log_mcp_tool_call(name, False, execution_time, error_msg)
        logger.error(f"MCP 工具调用失败 {name}: {error_msg}, 执行时间: {execution_time:.2f}s")
        
        return [TextContent(
            type="text",
            text=f"错误: {error_msg}"
        )]

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """
    列出可用的资源
    """
    return [
        Resource(
            uri="speaker-validation://config",
            name="系统配置",
            description="SpeakerValidationPreCheckSystem 的当前配置信息",
            mimeType="application/json"
        ),
        Resource(
            uri="speaker-validation://help",
            name="使用帮助",
            description="医药代表内容预审系统的使用指南",
            mimeType="text/plain"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """
    读取资源内容
    """
    if uri == "speaker-validation://config":
        try:
            config = get_current_config()
            return json.dumps(config, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"配置读取失败: {str(e)}"
    
    elif uri == "speaker-validation://help":
        return """
SpeakerValidationPreCheckSystem - 医药代表内容预审系统使用指南

主要功能：
1. 检查医药代表提交的内容是否包含必要的合规标识
2. 验证相关支撑文档的完整性（S3存储桶中的文件数量）
3. 综合评估内容的合规性和完整性
4. 为销售代表提供具体的改进建议和反馈意见

可用工具：
- list_s3_files: 检查支撑文档完整性
- check_string_content: 检查内容合规标识
- perform_preaudit: 执行完整预审流程（推荐使用）
- get_current_config: 获取当前审核标准

使用示例：
1. 获取配置: get_current_config()
2. 预审内容: perform_preaudit("您的演讲内容...")
3. 单独检查: check_string_content("内容", "审核标识")
4. 检查文档: list_s3_files("存储桶名称")

适用场景：
- 医药代表演讲内容预审
- 学术推广材料合规检查
- 培训资料完整性验证
- 销售支持文档审核
"""
    
    else:
        raise ValueError(f"未知的资源: {uri}")

async def main():
    """
    启动 MCP server
    """
    logger.info("启动 SpeakerValidationPreCheckSystem MCP Server")
    
    # 设置初始化选项
    options = InitializationOptions(
        server_name="speaker-validation-precheck",
        server_version="1.0.0",
        capabilities={
            "tools": {},
            "resources": {}
        }
    )
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("MCP Server 已启动，等待连接...")
            await server.run(
                read_stream,
                write_stream,
                options
            )
    except Exception as e:
        logger.error(f"MCP Server 运行失败: {str(e)}")
        raise
    finally:
        logger.info("MCP Server 已停止")

if __name__ == "__main__":
    asyncio.run(main())
