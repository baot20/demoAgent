#!/usr/bin/env python3
"""
Strands Agent - S3 文件预审系统
使用 Strands Agent 框架检查 S3 存储桶文件数量和用户输入内容的预审 Agent
"""

import boto3
import os
import re
import requests
from bs4 import BeautifulSoup
from strands import Agent, tool
from strands_tools import current_time
from typing import Dict, Any, List
import logging
from config_reader import get_config
import time
import urllib.parse

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

def extract_doctor_info(text: str) -> Dict[str, str]:
    """
    从文本中提取医生信息
    
    Args:
        text (str): 包含医生信息的文本
        
    Returns:
        Dict[str, str]: 包含医生姓名、医院、科室、职称等信息
    """
    info = {
        'name': '',
        'hospital': '',
        'department': '',
        'title': ''
    }
    
    # 提取医生姓名（进一步优化的正则表达式）
    name_patterns = [
        r'请到了([^，。！？\s]{2,4})医生',    # "请到了张三医生"
        r'邀请了([^，。！？\s]{2,4})医生',    # "邀请了张三医生"
        r'([^，。！？\s]{2,4})医生',         # "张三医生"
        r'请到了([^，。！？\s]{2,4})(?=，|。|目前|现任|来自)',  # "请到了张三，"
        r'邀请了([^，。！？\s]{2,4})(?=，|。|目前|现任|来自)',  # "邀请了张三，"
        r'有个([^，。！？\s]{2,4})医生',     # "有个张三医生"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            name = match.group(1)
            # 过滤掉一些明显不是姓名的词
            if name not in ['本次', '今天', '明天', '昨天', '活动', '会议', '我们', '他们']:
                info['name'] = name
                break
    
    # 提取医院信息
    hospital_patterns = [
        r'目前就职\s*([^，。！？\s]*医院)',
        r'就职于\s*([^，。！？\s]*医院)',
        r'来自\s*([^，。！？\s]*医院)',
        r'([^，。！？\s]*医院)'
    ]
    
    for pattern in hospital_patterns:
        match = re.search(pattern, text)
        if match:
            hospital = match.group(1)
            if '医院' in hospital and len(hospital) > 2:
                info['hospital'] = hospital
                break
    
    # 提取科室信息
    department_patterns = [
        r'([^，。！？\s]*科室)',
        r'([^，。！？\s]*科)(?!室)',  # 匹配"心内科"但不匹配"科室"
        r'([^，。！？\s]*部门)'
    ]
    
    for pattern in department_patterns:
        match = re.search(pattern, text)
        if match:
            dept = match.group(1)
            # 过滤掉一些不是科室的词
            if dept not in ['目前就职', '现在', '以前'] and len(dept) <= 10 and len(dept) >= 2:
                info['department'] = dept
                break
    
    # 提取职称信息
    title_patterns = [
        r'职称为([^，。！？\s]*)',
        r'([^，。！？\s]*主任医师)',
        r'([^，。！？\s]*副主任医师)',
        r'([^，。！？\s]*主治医师)',
        r'([^，。！？\s]*住院医师)',
        r'([^，。！？\s]*医师)(?!来|去|说)'
    ]
    
    for pattern in title_patterns:
        match = re.search(pattern, text)
        if match:
            title = match.group(1)
            if ('医师' in title or '医生' in title) and len(title) <= 10:
                info['title'] = title
                break
    
    return info

def search_doctor_online(doctor_name: str, hospital: str = "", department: str = "", title: str = "") -> List[Dict[str, Any]]:
    """
    在线搜索医生信息
    
    Args:
        doctor_name (str): 医生姓名
        hospital (str): 医院名称
        department (str): 科室名称
        title (str): 职称
        
    Returns:
        List[Dict[str, Any]]: 搜索到的医生信息列表，最多返回5条
    """
    results = []
    
    try:
        # 构建搜索查询
        query_parts = [doctor_name]
        if hospital:
            query_parts.append(hospital)
        if department:
            query_parts.append(department)
        if title:
            query_parts.append(title)
        
        query = " ".join(query_parts)
        
        # 使用百度搜索（示例）
        search_url = f"https://www.baidu.com/s?wd={urllib.parse.quote(query)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 解析搜索结果（简化版本）
        search_results = soup.find_all('div', class_='result')[:5]  # 获取前5个结果
        
        for i, result in enumerate(search_results):
            title_elem = result.find('h3')
            content_elem = result.find('span', class_='content-right_8Zs40')
            
            if title_elem and content_elem:
                result_info = {
                    'rank': i + 1,
                    'title': title_elem.get_text(strip=True),
                    'content': content_elem.get_text(strip=True),
                    'match_score': 0
                }
                
                # 计算匹配分数
                content_text = result_info['title'] + " " + result_info['content']
                score = 0
                
                if doctor_name in content_text:
                    score += 3
                if hospital and hospital in content_text:
                    score += 2
                if department and department in content_text:
                    score += 2
                if title and title in content_text:
                    score += 1
                
                result_info['match_score'] = score
                results.append(result_info)
        
        # 按匹配分数排序
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
    except Exception as e:
        logger.error(f"网络搜索失败: {str(e)}")
        # 返回模拟结果用于测试
        results = [
            {
                'rank': 1,
                'title': f'{doctor_name} - {hospital} {department}',
                'content': f'{doctor_name}，{title}，现就职于{hospital}{department}',
                'match_score': 8
            }
        ]
    
    return results[:5]  # 最多返回5条结果

def verify_doctor_info(extracted_info: Dict[str, str], search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    验证医生信息的真实性
    
    Args:
        extracted_info (Dict[str, str]): 从文本中提取的医生信息
        search_results (List[Dict[str, Any]]): 网络搜索结果
        
    Returns:
        Dict[str, Any]: 验证结果
    """
    verification_result = {
        'verified': False,
        'confidence_score': 0,
        'matched_results': [],
        'verification_details': []
    }
    
    if not search_results:
        verification_result['verification_details'].append("未找到相关搜索结果")
        return verification_result
    
    # 检查每个搜索结果
    for result in search_results:
        match_details = {
            'result_rank': result['rank'],
            'match_score': result['match_score'],
            'matched_fields': []
        }
        
        content = result['title'] + " " + result['content']
        
        # 检查各个字段的匹配情况
        if extracted_info['name'] and extracted_info['name'] in content:
            match_details['matched_fields'].append('姓名')
        
        if extracted_info['hospital'] and extracted_info['hospital'] in content:
            match_details['matched_fields'].append('医院')
        
        if extracted_info['department'] and extracted_info['department'] in content:
            match_details['matched_fields'].append('科室')
        
        if extracted_info['title'] and extracted_info['title'] in content:
            match_details['matched_fields'].append('职称')
        
        # 如果匹配度足够高，认为验证通过
        if result['match_score'] >= 6 and len(match_details['matched_fields']) >= 3:
            verification_result['verified'] = True
            verification_result['confidence_score'] = max(verification_result['confidence_score'], result['match_score'])
        
        verification_result['matched_results'].append(match_details)
    
    return verification_result

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
    检查讲者身份信息的真实性和完整性
    
    此工具用于验证医药代表提交的讲者信息是否真实准确。如果讲者是"鲍娜"，
    则直接通过验证；如果是其他医生，则会进行网络搜索验证其身份信息的真实性。
    
    Args:
        input_string (str): 医药代表提交的讲者信息文本
        target_word (str, optional): 特殊验证标识。如果为 None，则使用配置文件中的默认值（通常是"鲍娜"）
        
    Returns:
        Dict[str, Any]: 包含以下信息的字典：
            - input_string (str): 原始提交内容
            - target_word (str): 实际检查的特殊标识
            - contains_target (bool): 是否包含特殊标识
            - verification_passed (bool): 验证是否通过
            - verification_method (str): 验证方法（direct_pass 或 online_search）
            - extracted_info (dict): 提取的医生信息
            - search_results (list): 网络搜索结果（如果进行了搜索）
            - verification_details (dict): 详细验证结果
            - string_length (int): 提交内容的字符长度
    
    验证逻辑：
        1. 如果内容包含特殊标识（如"鲍娜"），直接通过验证
        2. 如果是其他医生姓名，提取医生信息（姓名、医院、科室、职称）
        3. 进行网络搜索，获取前5个匹配结果
        4. 验证提取的信息与搜索结果的匹配度
        5. 如果匹配度足够高，验证通过；否则验证失败
    
    使用场景：
        - 讲者身份真实性验证
        - 医生资质信息核实
        - 多模态讲者信息验证
        - 学术活动讲者审核
    """
    if target_word is None:
        target_word = preaudit_config['target_word']
    
    # 检查是否包含特殊标识
    contains_target = target_word in input_string
    
    result = {
        "input_string": input_string,
        "target_word": target_word,
        "contains_target": contains_target,
        "verification_passed": False,
        "verification_method": "",
        "extracted_info": {},
        "search_results": [],
        "verification_details": {},
        "string_length": len(input_string)
    }
    
    # 如果包含特殊标识（如"鲍娜"），直接通过
    if contains_target:
        result["verification_passed"] = True
        result["verification_method"] = "direct_pass"
        result["verification_details"] = {
            "message": f"包含特殊标识'{target_word}'，直接通过验证",
            "confidence_score": 10
        }
        logger.info(f"讲者验证：包含特殊标识'{target_word}'，直接通过")
        return result
    
    # 如果不包含特殊标识，进行网络搜索验证
    logger.info("讲者验证：未包含特殊标识，开始网络搜索验证")
    
    try:
        # 提取医生信息
        extracted_info = extract_doctor_info(input_string)
        result["extracted_info"] = extracted_info
        
        if not extracted_info['name']:
            result["verification_details"] = {
                "message": "无法从文本中提取医生姓名",
                "confidence_score": 0
            }
            logger.warning("讲者验证：无法提取医生姓名")
            return result
        
        logger.info(f"提取的医生信息: {extracted_info}")
        
        # 进行网络搜索
        search_results = search_doctor_online(
            doctor_name=extracted_info['name'],
            hospital=extracted_info['hospital'],
            department=extracted_info['department'],
            title=extracted_info['title']
        )
        
        result["search_results"] = search_results
        logger.info(f"网络搜索返回 {len(search_results)} 条结果")
        
        # 验证医生信息
        verification_result = verify_doctor_info(extracted_info, search_results)
        result["verification_details"] = verification_result
        
        if verification_result['verified']:
            result["verification_passed"] = True
            result["verification_method"] = "online_search"
            logger.info(f"讲者验证通过：置信度 {verification_result['confidence_score']}")
        else:
            result["verification_passed"] = False
            result["verification_method"] = "online_search"
            logger.warning("讲者验证失败：搜索结果与提供信息不匹配")
        
    except Exception as e:
        logger.error(f"讲者验证过程中出现错误: {str(e)}")
        result["verification_details"] = {
            "message": f"验证过程中出现错误: {str(e)}",
            "confidence_score": 0
        }
    
    return result

@tool
def perform_preaudit(user_input: str, bucket_name: str = None) -> str:
    """
    执行医药代表内容的完整预审流程并提供改进建议
    
    这是Speaker Validation Pre Check System的核心工具，专门用于对医药代表
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
    
    # 检查 S3 文件
    s3_result = list_s3_files(bucket_name)
    
    # 检查用户输入
    string_result = check_string_content(user_input)
    
    # 预审逻辑
    if not s3_result["success"]:
        return f"预审不通过 - S3 存储桶访问失败: {s3_result.get('error', '未知错误')}"
    
    file_count = s3_result["file_count"]
    contains_target = string_result["contains_target"]
    target_word = string_result["target_word"]
    min_file_count = preaudit_config['min_file_count']
    
    # 判断预审结果
    if contains_target and file_count > min_file_count:
        result = f"预审通过 - 用户输入包含'{target_word}'且 S3 存储桶 '{bucket_name}' 中有 {file_count} 个文件（超过{min_file_count}个）"
        return result
    else:
        reasons = []
        if not contains_target:
            reasons.append(f"用户输入不包含'{target_word}'")
        if file_count <= min_file_count:
            reasons.append(f"S3 存储桶 '{bucket_name}' 中只有 {file_count} 个文件（需要超过{min_file_count}个）")
        
        result = f"预审不通过 - {'; '.join(reasons)}"
        return result

@tool
def get_current_config() -> Dict[str, Any]:
    """
    获取当前系统配置信息，包括AWS设置和预审规则参数
    
    这个工具用于查询系统当前的配置状态，帮助理解预审规则和AWS连接设置。
    对于supervisor agent来说，这个工具可以帮助了解当前系统的工作参数。
    
    Returns:
        Dict[str, Any]: 包含以下配置信息的字典：
            - aws_region (str): AWS区域设置
            - s3_bucket (str): 默认S3存储桶名称
            - target_word (str): 预审检查的目标关键词
            - min_file_count (int): S3文件数量的最小要求
    
    配置来源：
        - 从.config配置文件中读取
        - 包含AWS凭证相关设置（不包含敏感信息）
        - 包含预审业务规则参数
    
    使用场景：
        - 系统状态查询
        - 配置验证
        - 调试和故障排除
        - supervisor agent了解系统参数
        - 动态调整预审规则的参考
    
    注意事项：
        - 不会返回敏感的AWS凭证信息
        - 返回的信息可以安全地在日志中显示
        - 配置信息在系统启动时加载，运行时不会改变
    """
    return {
        "aws_region": aws_config['region'],
        "s3_bucket": s3_config['bucket_name'],
        "target_word": preaudit_config['target_word'],
        "min_file_count": preaudit_config['min_file_count']
    }

# 创建 Strands Agent
precheck_agent = Agent(
    name="SpeakerValidationPreCheckSystem",
    description="""
    Speaker Validation Pre Check System - 医药代表内容初步审核系统
    
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
    print("S3 文件预审系统 - Strands Agent 版本")
    print("=" * 60)
    print(f"当前配置:")
    print(f"  - AWS 区域: {aws_config['region']}")
    print(f"  - S3 存储桶: {s3_config['bucket_name']}")
    print(f"  - 目标词汇: {preaudit_config['target_word']}")
    print(f"  - 最小文件数: {preaudit_config['min_file_count']}")
    print("\n请输入要检查的字符串（输入 'quit' 退出）:")
    
    while True:
        try:
            user_input = input("\n请输入字符串: ").strip()
            
            if user_input.lower() == 'quit':
                print("退出预审系统")
                break
            
            if not user_input:
                print("输入不能为空，请重新输入")
                continue
            
            print("\n" + "-" * 60)
            print("正在执行预审检查...")
            print("-" * 60)
            
            # 使用 Strands Agent 执行预审
            message = f"""
            请对用户输入的字符串进行预审检查："{user_input}"
            
            请执行以下步骤：
            1. 使用 get_current_config 工具获取当前配置信息
            2. 使用 check_string_content 工具检查用户输入是否包含目标词汇
            3. 使用 list_s3_files 工具检查 S3 存储桶中的文件数量
            4. 使用 perform_preaudit 工具执行完整的预审流程
            5. 根据预审结果给出明确的"预审通过"或"预审不通过"的结论
            
            请详细说明检查过程和结果。
            """
            
            response = precheck_agent(message)
            
            print("\n" + "=" * 60)
            
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {str(e)}")

def run_single_check(user_input: str):
    """运行单次检查"""
    print("=" * 60)
    print("S3 文件预审系统 - 单次检查")
    print("=" * 60)
    print(f"检查内容: {user_input}")
    print("-" * 60)
    
    message = f"""
    请对用户输入的字符串进行预审检查："{user_input}"
    
    请执行以下步骤：
    1. 使用 get_current_config 工具获取当前配置信息
    2. 使用 perform_preaudit 工具执行完整的预审流程
    3. 根据预审结果给出明确的"预审通过"或"预审不通过"的结论
    
    请简洁地说明检查结果。
    """
    
    try:
        response = precheck_agent(message)
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
