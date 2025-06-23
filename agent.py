#!/usr/bin/env python3
"""
Strands Agent - S3 文件预审系统
使用 Strands Agent 框架检查 S3 存储桶文件数量和用户输入内容的预审 Agent
"""

import boto3
import os
from strands import Agent, tool
from strands_tools import current_time
from typing import Dict, Any
import logging
from config_reader import get_config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载配置
try:
    config = get_config()
    if not config.validate_config():
        logger.error("配置验证失败，请检查 .config 文件")
        exit(1)
    
    # 获取配置信息
    aws_config = config.get_aws_config()
    s3_config = config.get_s3_config()
    preaudit_config = config.get_preaudit_config()
    
    logger.info("配置加载成功")
    
except Exception as e:
    logger.error(f"配置加载失败: {str(e)}")
    logger.error("请确保 .config 文件存在并正确配置")
    exit(1)

def create_s3_client():
    """创建配置好的 S3 客户端"""
    return boto3.client(
        's3',
        aws_access_key_id=aws_config['access_key_id'],
        aws_secret_access_key=aws_config['secret_access_key'],
        region_name=aws_config['region']
    )

@tool
def list_s3_files(bucket_name: str = None) -> Dict[str, Any]:
    """
    检查医药代表提交的支撑文档完整性
    
    此工具用于验证医药代表提交的相关支撑文档是否完整，包括产品资料、
    临床数据、合规文件等。系统会统计S3存储桶中的文档数量，确保满足
    监管要求的最低文档数量标准。
    
    Args:
        bucket_name (str, optional): 存储医药文档的S3存储桶名称。如果为 None，则使用配置文件中的默认存储桶
        
    Returns:
        Dict[str, Any]: 包含以下信息的字典：
            - success (bool): 文档检查是否成功
            - file_count (int): 支撑文档总数量
            - files (List[str]): 文档名称列表（显示前10个）
            - bucket_name (str): 实际检查的存储桶名称
            - error (str, optional): 如果失败，包含错误信息
    
    使用场景：
        - 验证产品推广材料的支撑文档完整性
        - 检查学术演讲的参考资料数量
        - 确保培训材料的配套文档齐全
        - 合规审核前的文档完整性预检
    
    审核标准：
        - 支撑文档数量必须满足监管要求的最低标准
        - 文档类型应包括产品信息、临床数据、安全性资料等
        - 大型推广活动可能需要更多的支撑文档
    
    注意事项：
        - 需要有效的AWS凭证和文档存储访问权限
        - 文档数量仅为初步检查，具体内容质量需人工审核
        - 返回的文档列表仅包含文件名，不涉及具体内容
    """
    if bucket_name is None:
        bucket_name = s3_config['bucket_name']
    
    try:
        s3_client = create_s3_client()
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        files = []
        if 'Contents' in response:
            files = [obj['Key'] for obj in response['Contents']]
        
        return {
            "success": True,
            "file_count": len(files),
            "files": files[:10],  # 只显示前10个文件名
            "bucket_name": bucket_name
        }
    except Exception as e:
        logger.error(f"列出 S3 文件失败: {str(e)}")
        return {
            "success": False,
            "file_count": 0,
            "files": [],
            "error": str(e),
            "bucket_name": bucket_name
        }

@tool
def check_string_content(input_string: str, target_word: str = None) -> Dict[str, Any]:
    """
    检查医药代表提交内容的合规标识
    
    此工具用于验证医药代表提交的演讲内容、培训材料或推广资料是否包含
    必要的合规标识。在医药行业，所有对外材料都必须经过指定审核人员
    的审查，并包含相应的审核标识。
    
    Args:
        input_string (str): 医药代表提交的内容文本
        target_word (str, optional): 要检查的合规标识。如果为 None，则使用配置文件中的默认审核人员标识（通常是审核人员姓名）
        
    Returns:
        Dict[str, Any]: 包含以下信息的字典：
            - input_string (str): 原始提交内容
            - target_word (str): 实际检查的合规标识
            - contains_target (bool): 是否包含必要的合规标识
            - string_length (int): 提交内容的字符长度
    
    使用场景：
        - 演讲内容合规性预检
        - 学术推广材料审核标识验证
        - 培训资料合规要素检查
        - 销售支持文档标识确认
    
    合规要求：
        - 所有对外材料必须包含审核人员的标识
        - 标识通常为审核人员的姓名或工号
        - 缺少合规标识的材料不能用于对外推广
        - 标识的存在表明内容已经过初步审核
    
    检查逻辑：
        - 使用精确的字符串匹配检查
        - 区分大小写，确保标识准确性
        - 支持中文审核人员姓名
        - 不进行模糊匹配，确保合规严格性
    """
    if target_word is None:
        target_word = preaudit_config['target_word']
    
    contains_target = target_word in input_string
    
    return {
        "input_string": input_string,
        "target_word": target_word,
        "contains_target": contains_target,
        "string_length": len(input_string)
    }

@tool
def perform_preaudit(user_input: str, bucket_name: str = None) -> str:
    """
    执行医药代表内容的完整预审流程并提供改进建议
    
    这是SpeakerValidationPreCheckSystem的核心工具，专门用于对医药代表
    提交的内容进行全面的初步审核。系统会检查合规性和完整性，并为销售
    代表提供具体的改进意见和整改建议。
    
    Args:
        user_input (str): 医药代表提交的内容（演讲稿、培训材料、推广资料等）
        bucket_name (str, optional): 存储相关支撑文档的S3存储桶名称。如果为 None，则使用配置文件中的默认存储桶
        
    Returns:
        str: 详细的预审结果和改进建议，格式为：
            - 成功："预审通过 - [通过原因] + [优化建议]"
            - 失败："预审不通过 - [具体问题] + [改进建议] + [整改步骤]"
    
    预审标准：
        1. 合规性检查：内容必须包含指定的审核人员标识
        2. 完整性检查：相关支撑文档数量必须满足监管要求
        3. 综合评估：两个条件都满足才能通过初步预审
    
    可能的审核结果：
        - "预审通过" - 内容符合基本要求，可进入下一审核阶段
        - "预审不通过 - 缺少合规标识" - 需要添加审核人员标识
        - "预审不通过 - 支撑文档不足" - 需要补充相关文档材料
        - "预审不通过 - 多项问题" - 需要全面整改
        - "预审不通过 - 系统错误" - 技术问题，需要联系IT支持
    
    改进建议类型：
        - 合规性改进：如何添加必要的审核标识
        - 文档完整性：需要补充哪些类型的支撑文档
        - 内容优化：提升专业性和准确性的建议
        - 后续步骤：通过预审后的下一步操作指导
    
    使用场景：
        - 医药代表演讲内容预审
        - 学术推广材料合规检查
        - 培训资料完整性验证
        - 销售支持文档审核
        - 合规性培训和指导
    
    注意事项：
        - 这是初步预审，通过后仍需人工详细审核
        - 建议基于当前监管要求和公司政策
        - 销售代表应根据建议进行相应整改
    """
    if bucket_name is None:
        bucket_name = s3_config['bucket_name']
    
    # 检查支撑文档
    s3_result = list_s3_files(bucket_name)
    
    # 检查合规标识
    string_result = check_string_content(user_input)
    
    # 预审逻辑
    if not s3_result["success"]:
        return f"""预审不通过 - 支撑文档系统访问失败: {s3_result.get('error', '未知错误')}

改进建议：
1. 请联系IT支持检查文档存储系统连接
2. 确认您有权限访问相关文档存储区域
3. 稍后重试或联系系统管理员

后续步骤：
- 解决技术问题后重新提交审核
- 如持续出现问题，请提交技术支持工单"""
    
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
        
        return result

@tool
def get_current_config() -> Dict[str, Any]:
    """
    获取SpeakerValidationPreCheckSystem的当前审核标准和配置
    
    此工具用于查询系统当前的审核标准、合规要求和配置参数。对于医药
    代表和销售团队来说，了解当前的审核标准有助于提高内容质量和
    通过率。
    
    Returns:
        Dict[str, Any]: 包含以下配置信息的字典：
            - aws_region (str): 文档存储的AWS区域
            - s3_bucket (str): 默认的文档存储桶名称
            - target_word (str): 当前要求的合规标识（审核人员标识）
            - min_file_count (int): 支撑文档的最低数量要求
    
    配置说明：
        - aws_region: 公司文档存储的云服务区域设置
        - s3_bucket: 医药文档和资料的默认存储位置
        - target_word: 当前指定的审核人员标识，所有材料必须包含
        - min_file_count: 监管要求的最低支撑文档数量
    
    使用场景：
        - 医药代表了解当前审核标准
        - 销售团队查询合规要求
        - 系统管理员验证配置状态
        - 培训新员工了解审核流程
        - 故障排除和系统诊断
    
    合规意义：
        - 确保所有人员了解最新的审核要求
        - 帮助医药代表准备符合标准的材料
        - 提供透明的审核标准参考
        - 支持合规培训和指导工作
    
    注意事项：
        - 配置信息在系统启动时加载
        - 不包含敏感的系统凭证信息
        - 审核标准可能根据监管要求调整
        - 建议定期查询以获取最新标准
    """
    return {
        "aws_region": aws_config['region'],
        "s3_bucket": s3_config['bucket_name'],
        "target_word": preaudit_config['target_word'],
        "min_file_count": preaudit_config['min_file_count']
    }

# 创建 Strands Agent
preaudit_agent = Agent(
    name="SpeakerValidationPreCheckSystem",
    description="""
    SpeakerValidationPreCheckSystem - 医药代表内容初步审核系统
    
    专门用于对医药代表提交的演讲内容、培训材料和推广资料进行初步审核的智能系统。
    
    主要功能：
    1. 检查医药代表提交的内容是否包含必要的合规标识（如审核人员标识"鲍娜"）
    2. 验证相关支撑文档的完整性（S3存储桶中的文件数量是否满足要求）
    3. 综合评估内容的合规性和完整性
    4. 为销售代表提供具体的改进建议和反馈意见
    
    适用场景：
    - 医药代表演讲内容预审
    - 学术推广材料合规检查
    - 培训资料完整性验证
    - 销售支持文档审核
    - 合规性初步筛查
    
    审核标准：
    - 内容必须包含指定的合规标识
    - 支撑文档数量必须满足最低要求
    - 只有同时满足两个条件才能通过初步审核
    
    输出结果：
    - "预审通过" + 详细通过原因和建议
    - "预审不通过" + 具体改进意见和整改建议
    """,
    instructions="""
    你是一个专业的医药行业内容审核系统。当医药代表提交内容进行预审时，请按以下步骤执行：
    
    1. 首先使用 get_current_config 工具获取当前审核标准和配置信息
    2. 使用 check_string_content 工具检查提交内容是否包含必要的合规标识
    3. 使用 list_s3_files 工具检查相关支撑文档的数量和完整性
    4. 使用 perform_preaudit 工具执行完整的预审判断流程
    5. 根据审核结果为销售代表提供具体的改进建议
    
    审核重点：
    - 合规性：确保内容包含必要的审核标识和合规要素
    - 完整性：验证支撑文档数量是否满足监管要求
    - 专业性：评估内容的医学准确性和专业水准
    
    反馈原则：
    - 如果预审通过：说明通过原因，提供优化建议
    - 如果预审不通过：明确指出问题所在，提供具体的整改建议
    - 始终以帮助销售代表改进内容质量为目标
    - 使用专业但友好的医药行业术语
    
    输出格式：
    - 详细的审核过程说明
    - 明确的预审结论（通过/不通过）
    - 针对性的改进建议和整改指导
    - 后续步骤建议
    """,
    tools=[
        list_s3_files, 
        check_string_content, 
        perform_preaudit, 
        get_current_config,
        current_time
    ]
)

def run_interactive_mode():
    """运行交互式模式"""
    print("=" * 60)
    print("SpeakerValidationPreCheckSystem")
    print("医药代表内容初步审核系统 - Strands Agent 版本")
    print("=" * 60)
    print(f"当前审核标准:")
    print(f"  - AWS 区域: {aws_config['region']}")
    print(f"  - 文档存储: {s3_config['bucket_name']}")
    print(f"  - 必需标识: {preaudit_config['target_word']}")
    print(f"  - 最低文档数: {preaudit_config['min_file_count']}个")
    print("\n请输入医药代表提交的内容进行预审（输入 'quit' 退出）:")
    
    while True:
        try:
            user_input = input("\n请输入内容: ").strip()
            
            if user_input.lower() == 'quit':
                print("退出预审系统")
                break
            
            if not user_input:
                print("输入不能为空，请重新输入")
                continue
            
            print("\n" + "-" * 60)
            print("正在执行医药内容预审检查...")
            print("-" * 60)
            
            # 使用 Strands Agent 执行预审
            message = f"""
            请对医药代表提交的内容进行预审检查："{user_input}"
            
            请执行以下步骤：
            1. 使用 get_current_config 工具获取当前审核标准
            2. 使用 check_string_content 工具检查内容是否包含必要的合规标识
            3. 使用 list_s3_files 工具检查支撑文档的完整性
            4. 使用 perform_preaudit 工具执行完整的预审流程
            5. 为销售代表提供具体的改进建议和后续步骤指导
            
            请详细说明审核过程和结果，并提供专业的医药行业建议。
            """
            
            response = preaudit_agent(message)
            
            print("\n" + "=" * 60)
            
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {str(e)}")

def run_single_check(user_input: str):
    """运行单次检查"""
    print("=" * 60)
    print("SpeakerValidationPreCheckSystem - 单次审核")
    print("=" * 60)
    print(f"审核内容: {user_input}")
    print("-" * 60)
    
    message = f"""
    请对医药代表提交的内容进行预审检查："{user_input}"
    
    请执行以下步骤：
    1. 使用 get_current_config 工具获取当前审核标准
    2. 使用 perform_preaudit 工具执行完整的预审流程
    3. 为销售代表提供具体的改进建议
    
    请简洁地说明审核结果和改进建议。
    """
    
    try:
        response = preaudit_agent(message)
        print("=" * 60)
        return response
    except Exception as e:
        print(f"预审执行失败: {str(e)}")
        return None

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        # 命令行参数模式
        user_input = " ".join(sys.argv[1:])
        run_single_check(user_input)
    else:
        # 交互式模式
        run_interactive_mode()

if __name__ == "__main__":
    main()
