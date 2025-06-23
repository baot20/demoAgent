#!/usr/bin/env python3
"""
S3 预审 Agent 元数据定义
为 supervisor agent 提供详细的 agent 信息和使用指南
"""

AGENT_METADATA = {
    "name": "SpeakerValidationPreCheckSystem",
    "version": "0.1",
    "type": "medical_content_preaudit",
    "category": "pharmaceutical_compliance",
    
    "description": {
        "short": "Speaker Validation Pre Check System - 医药代表内容初步审核系统",
        "detailed": """
        这是一个专门为医药行业设计的内容预审系统，主要用于对医药代表提交的
        演讲内容、培训材料和推广资料进行初步审核。
        
        系统功能：
        1. 合规性检查 - 验证内容是否包含必要的审核人员标识
        2. 完整性验证 - 检查相关支撑文档是否满足监管要求
        3. 智能预审 - 基于多个条件进行综合判断
        4. 改进建议 - 为销售代表提供具体的整改指导
        
        该系统帮助确保所有对外材料都符合医药行业的合规要求，
        提高审核效率，降低合规风险。
        """
    },
    
    "capabilities": [
        "医药内容合规性检查",
        "支撑文档完整性验证", 
        "多条件综合预审判断",
        "详细的改进建议生成",
        "医药行业专业术语支持",
        "合规标准配置化管理"
    ],
    
    "use_cases": [
        {
            "scenario": "医药代表演讲内容预审",
            "description": "对医药代表准备的学术演讲内容进行合规性和完整性检查"
        },
        {
            "scenario": "学术推广材料审核",
            "description": "验证推广材料是否包含必要的审核标识和支撑文档"
        },
        {
            "scenario": "培训资料合规检查",
            "description": "确保内部培训材料符合监管要求和公司政策"
        },
        {
            "scenario": "销售支持文档验证",
            "description": "检查销售团队使用的支持材料的合规性"
        },
        {
            "scenario": "合规培训和指导",
            "description": "为销售团队提供合规要求的培训和改进指导"
        }
    ],
    
    "input_requirements": {
        "required": [
            {
                "name": "content",
                "type": "string", 
                "description": "医药代表提交的内容（演讲稿、培训材料、推广资料等）"
            }
        ],
        "optional": [
            {
                "name": "document_bucket",
                "type": "string",
                "description": "存储支撑文档的位置，如不提供则使用默认配置"
            }
        ]
    },
    
    "output_format": {
        "success_pattern": "预审通过 - [通过原因] + [优化建议] + [后续步骤]",
        "failure_pattern": "预审不通过 - [具体问题] + [改进建议] + [整改步骤]",
        "additional_info": "包含详细的合规指导和专业建议"
    },
    
    "configuration": {
        "configurable_parameters": [
            {
                "name": "TARGET_WORD",
                "default": "鲍娜",
                "description": "必需的审核人员标识（通常为审核人员姓名）"
            },
            {
                "name": "MIN_FILE_COUNT", 
                "default": 3,
                "description": "支撑文档的最低数量要求"
            },
            {
                "name": "AWS_REGION",
                "default": "us-east-1", 
                "description": "文档存储的AWS区域"
            },
            {
                "name": "S3_BUCKET_NAME",
                "description": "医药文档的默认存储桶名称"
            }
        ]
    },
    
    "dependencies": {
        "aws_services": ["S3"],
        "permissions": [
            "s3:ListBucket - 访问医药文档存储"
        ],
        "python_packages": [
            "boto3>=1.34.0",
            "strands",
            "strands-tools"
        ]
    },
    
    "tools": [
        {
            "name": "list_s3_files",
            "purpose": "检查医药代表提交的支撑文档完整性",
            "input": "bucket_name (optional)",
            "output": "支撑文档数量和列表信息"
        },
        {
            "name": "check_string_content", 
            "purpose": "检查医药代表提交内容的合规标识",
            "input": "input_string, target_word (optional)",
            "output": "合规标识检查结果"
        },
        {
            "name": "perform_preaudit",
            "purpose": "执行完整预审流程并提供改进建议",
            "input": "user_input, bucket_name (optional)", 
            "output": "详细的预审结果和改进建议"
        },
        {
            "name": "get_current_config",
            "purpose": "获取当前审核标准和配置信息",
            "input": "无",
            "output": "系统审核标准参数"
        }
    ],
    
    "performance": {
        "typical_response_time": "2-5秒",
        "factors_affecting_performance": [
            "支撑文档存储桶大小",
            "网络延迟",
            "AWS API响应时间"
        ]
    },
    
    "error_handling": {
        "common_errors": [
            {
                "error": "AWS凭证无效",
                "solution": "检查.config文件中的AWS凭证配置"
            },
            {
                "error": "文档存储桶不存在",
                "solution": "验证存储桶名称和访问权限"
            },
            {
                "error": "网络连接问题", 
                "solution": "检查网络连接和AWS服务状态"
            }
        ]
    },
    
    "integration_guide": {
        "for_supervisor_agents": {
            "when_to_use": [
                "医药代表提交内容需要预审时",
                "需要检查合规标识和支撑文档时", 
                "需要为销售团队提供改进建议时"
            ],
            "how_to_call": {
                "simple_check": 'agent("请对医药代表提交的内容进行预审检查")',
                "detailed_check": 'agent("请详细审核内容并提供具体的改进建议")',
                "compliance_focus": 'agent("重点检查内容的合规性和文档完整性")'
            },
            "expected_response_time": "2-5秒",
            "response_interpretation": {
                "success_indicators": ["预审通过", "合规标识完整", "文档数量充足"],
                "failure_indicators": ["预审不通过", "缺少合规标识", "支撑文档不足"],
                "error_indicators": ["系统访问失败", "配置错误"]
            }
        }
    },
    
    "monitoring": {
        "key_metrics": [
            "预审通过率",
            "平均响应时间", 
            "文档系统访问成功率",
            "合规问题发现率"
        ],
        "log_levels": {
            "INFO": "正常审核操作和结果",
            "WARNING": "合规问题和配置警告",
            "ERROR": "系统连接错误和审核失败"
        }
    },
    
    "compliance_standards": {
        "regulatory_requirements": [
            "所有对外材料必须包含审核人员标识",
            "推广材料必须有充足的支撑文档",
            "内容必须符合医药行业监管要求",
            "材料使用前必须经过完整审核流程"
        ],
        "quality_guidelines": [
            "确保医学信息的准确性",
            "包含适当的免责声明",
            "提供完整的产品信息",
            "遵循公司合规政策"
        ]
    }
}

def get_agent_metadata():
    """获取Agent元数据"""
    return AGENT_METADATA

def print_agent_info():
    """打印Agent信息摘要"""
    metadata = get_agent_metadata()
    
    print("=" * 60)
    print(f"Agent: {metadata['name']} v{metadata['version']}")
    print("=" * 60)
    print(f"类型: {metadata['type']}")
    print(f"分类: {metadata['category']}")
    print(f"\n描述: {metadata['description']['short']}")
    
    print(f"\n核心能力:")
    for capability in metadata['capabilities']:
        print(f"  • {capability}")
    
    print(f"\n可用工具:")
    for tool in metadata['tools']:
        print(f"  • {tool['name']}: {tool['purpose']}")
    
    print(f"\n典型响应时间: {metadata['performance']['typical_response_time']}")
    print("=" * 60)

if __name__ == "__main__":
    print_agent_info()
