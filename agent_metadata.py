#!/usr/bin/env python3
"""
S3 预审 Agent 元数据定义
为 supervisor agent 提供详细的 agent 信息和使用指南
"""

AGENT_METADATA = {
    "name": "SpeakerValidationPreCheckSystem",
    "version": "1.0",
    "type": "medical_content_preaudit",
    "category": "pharmaceutical_compliance",
    
    "description": {
        "short": "Speaker Validation Pre Check System - 医药代表内容初步审核系统",
        "detailed": """
        这是一个专门为医药行业设计的内容预审系统，主要用于对医药代表提交的讲者信息进行审核。
        对于讲者，医药代表需要提交关于讲者繁杂的信息，且格式无法统一，包括： 名字，医院，科室，
        职称，照片，发表的论文等。 数据的形式以 text结合多模态的数据(照片,PDF等)
       
        系统功能：
        1. 合规性检查 - 验证讲者的身份是否是如描述的那样
        2. 完整性验证 - 检查相关支撑文档是否满足监管要求
        3. 智能预审 - 基于多个条件进行综合判断
        4. 改进建议 - 为销售代表提供具体的整改指导
        
        该系统帮助确保所有对外材料都符合医药行业的合规要求，
        提高审核效率，降低合规风险。
        """
    },
    
    "capabilities": [
        "讲者身份真实性验证",
        "讲者资质信息完整性检查",
        "多模态数据处理（文本+图片+PDF）",
        "讲者信息交叉验证",
        "详细的改进建议生成",
        "医药行业专业术语支持",
        "合规标准配置化管理"
    ],
    
    "use_cases": [
        {
            "scenario": "讲者身份验证",
            "description": "验证医药代表提交的讲者身份信息是否真实准确"
        },
        {
            "scenario": "讲者资质审核",
            "description": "检查讲者的医院、科室、职称等资质信息的完整性和准确性"
        },
        {
            "scenario": "讲者学术背景验证",
            "description": "验证讲者发表论文、学术成就等背景信息的真实性"
        },
        {
            "scenario": "讲者照片和文档审核",
            "description": "检查讲者照片的真实性和相关支撑文档的完整性"
        },
        {
            "scenario": "多模态信息整合验证",
            "description": "整合文本、图片、PDF等多种格式的讲者信息进行综合验证"
        }
    ],
    
    "input_requirements": {
        "required": [
            {
                "name": "speaker_info",
                "type": "multimodal", 
                "description": "讲者信息（包括姓名、医院、科室、职称、照片、发表论文等多模态数据）"
            }
        ],
        "optional": [
            {
                "name": "document_bucket",
                "type": "string",
                "description": "存储讲者支撑文档的位置，如不提供则使用默认配置"
            },
            {
                "name": "verification_level",
                "type": "string",
                "description": "验证级别：basic（基础）、detailed（详细）、comprehensive（全面）"
            }
        ]
    },
    
    "output_format": {
        "success_pattern": "讲者验证通过 - [验证结果] + [可信度评估] + [建议使用场景]",
        "failure_pattern": "讲者验证不通过 - [具体问题] + [缺失信息] + [补充建议]",
        "additional_info": "包含详细的身份验证报告和多模态数据分析结果"
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
            "purpose": "检查讲者相关支撑文档的完整性",
            "input": "bucket_name (optional)",
            "output": "讲者支撑文档数量和列表信息"
        },
        {
            "name": "check_string_content", 
            "purpose": "检查讲者信息文本内容的完整性和准确性",
            "input": "input_string, target_word (optional)",
            "output": "讲者信息完整性检查结果"
        },
        {
            "name": "perform_preaudit",
            "purpose": "执行完整的讲者身份验证流程",
            "input": "speaker_info, bucket_name (optional)", 
            "output": "详细的讲者验证结果和可信度评估"
        },
        {
            "name": "get_current_config",
            "purpose": "获取当前讲者验证标准和配置信息",
            "input": "无",
            "output": "系统验证标准参数"
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
                "需要验证讲者身份信息真实性时",
                "需要检查讲者资质和学术背景时", 
                "需要处理多模态讲者信息数据时",
                "需要评估讲者可信度和适用性时"
            ],
            "how_to_call": {
                "simple_check": 'agent("请对提交的讲者信息进行身份验证")',
                "detailed_check": 'agent("请详细验证讲者的资质和学术背景")',
                "multimodal_check": 'agent("请综合分析讲者的文本信息、照片和相关文档")'
            },
            "expected_response_time": "2-5秒",
            "response_interpretation": {
                "success_indicators": ["讲者验证通过", "身份信息真实", "资质文档完整"],
                "failure_indicators": ["讲者验证不通过", "身份信息不符", "支撑文档不足"],
                "error_indicators": ["系统访问失败", "配置错误", "多模态数据处理失败"]
            }
        }
    },
    
    "monitoring": {
        "key_metrics": [
            "讲者验证通过率",
            "身份信息准确率",
            "平均响应时间", 
            "多模态数据处理成功率",
            "文档系统访问成功率"
        ],
        "log_levels": {
            "INFO": "正常验证操作和结果",
            "WARNING": "身份信息不一致和配置警告",
            "ERROR": "系统连接错误和验证失败"
        }
    },
    
    "compliance_standards": {
        "regulatory_requirements": [
            "所有讲者信息必须真实准确",
            "讲者资质必须有充足的支撑文档",
            "讲者身份必须符合医药行业监管要求",
            "多模态数据必须经过完整验证流程"
        ],
        "quality_guidelines": [
            "确保讲者医学背景的准确性",
            "验证讲者学术成就的真实性",
            "提供完整的讲者资质信息",
            "遵循公司讲者管理政策"
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
