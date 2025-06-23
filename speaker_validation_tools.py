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

def list_s3_files_with_prefix(bucket_name: str = None, prefix: str = "") -> Dict[str, Any]:
    """
    检查指定前缀下的S3文件
    """
    start_time = time.time()
    if bucket_name is None:
        bucket_name = s3_config['bucket_name']
    
    logger.info(f"开始检查 S3 存储桶: {bucket_name}, 前缀: {prefix}")
    
    try:
        s3_client = create_s3_client()
        
        # 使用前缀过滤
        if prefix:
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        else:
            response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        files = []
        if 'Contents' in response:
            all_objects = [obj['Key'] for obj in response['Contents']]
            # 过滤掉文件夹（以 '/' 结尾的对象）
            files = [obj_key for obj_key in all_objects if not obj_key.endswith('/')]
        
        result = {
            "success": True,
            "file_count": len(files),
            "files": files[:10],  # 只显示前10个文件名
            "bucket_name": bucket_name,
            "prefix": prefix
        }
        
        execution_time = time.time() - start_time
        log_s3_access(bucket_name, True, len(files))
        log_mcp_tool_call("list_s3_files_with_prefix", True, execution_time)
        logger.info(f"S3 文件检查成功，前缀'{prefix}'下找到 {len(files)} 个文件")
        
        return result
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = str(e)
        log_s3_access(bucket_name, False, 0, error_msg)
        log_mcp_tool_call("list_s3_files_with_prefix", False, execution_time, error_msg)
        logger.error(f"列出 S3 文件失败: {error_msg}")
        
        return {
            "success": False,
            "file_count": 0,
            "files": [],
            "error": error_msg,
            "bucket_name": bucket_name,
            "prefix": prefix
        }

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

def extract_doctor_info(text: str) -> Dict[str, str]:
    """
    从文本中提取医生信息
    """
    import re
    
    info = {
        'name': '',
        'hospital': '',
        'department': '',
        'title': ''
    }
    
    # 提取医生姓名 - 修复正则表达式，确保能正确识别具体的医生姓名
    name_patterns = [
        r'请到了([^，。！？\s]{2,4})医生',  # "请到了张三医生"
        r'邀请了([^，。！？\s]{2,4})医生',  # "邀请了张三医生"
        r'有个([^，。！？\s]{2,4})医生',   # "有个张三医生"
        r'([^，。！？\s]{2,4})医生(?=，|。|目前|现任|来自)',  # "张三医生，目前..."
        r'请到了([^，。！？\s]{2,4})(?=，|。|目前|现任|来自)',  # "请到了张三，目前..."
        r'邀请了([^，。！？\s]{2,4})(?=，|。|目前|现任|来自)',  # "邀请了张三，目前..."
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            name = match.group(1)
            # 过滤掉明显不是姓名的词汇，并且检查是否是合理的中文姓名
            if (name not in ['本次', '今天', '明天', '昨天', '活动', '会议', '我们', '他们', '医生', '一个', '一位', '这个', '那个'] and
                len(name) >= 2 and len(name) <= 4 and
                not any(char in name for char in ['请到', '邀请', '活动', '会议', '举办'])):
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
        r'([^，。！？\s]*部门)',
        r'医院([^，。！？\s]*科)',  # 匹配"长海医院心内科"中的"心内科"
        r'就职([^，。！？\s]*医院)([^，。！？\s]*科)',  # 匹配"就职长海医院心内科"
    ]
    
    for pattern in department_patterns:
        match = re.search(pattern, text)
        if match:
            if len(match.groups()) == 2:  # 有两个捕获组的情况
                dept = match.group(2)  # 取第二个组（科室）
            else:
                dept = match.group(1)  # 只有一个捕获组
            
            # 过滤掉一些不是科室的词
            if (dept not in ['目前就职', '现在', '以前', '长海医院', '协和医院'] and 
                len(dept) <= 10 and len(dept) >= 2 and '科' in dept):
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

def check_string_content(input_string: str, target_word: str = None) -> Dict[str, Any]:
    """
    检查讲者身份信息的真实性和完整性
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
            "verification_passed": False,
            "verification_method": "",
            "extracted_info": {},
            "verification_details": {},
            "string_length": len(input_string)
        }
        
        # 如果包含特殊标识（如"鲍娜"），直接通过
        if contains_target:
            result["verification_passed"] = True
            result["verification_method"] = "direct_pass"
            result["verification_details"] = {
                "message": "内容已通过内部验证流程",
                "confidence_score": 10
            }
            logger.info(f"讲者验证：包含特殊标识'{target_word}'，直接通过")
        else:
            # 如果不包含特殊标识，进行医生信息提取
            logger.info("讲者验证：未包含特殊标识，开始提取医生信息")
            
            # 提取医生信息
            extracted_info = extract_doctor_info(input_string)
            result["extracted_info"] = extracted_info
            
            if not extracted_info['name']:
                result["verification_details"] = {
                    "message": "无法从文本中提取医生姓名",
                    "confidence_score": 0
                }
                logger.warning("讲者验证：无法提取医生姓名")
            else:
                # 如果提取到医生信息，进行信息完整性检查
                info_fields = [k for k, v in extracted_info.items() if v]
                if len(info_fields) >= 3:  # 至少有3个字段有值
                    result["verification_passed"] = True
                    result["verification_method"] = "info_extraction"
                    result["verification_details"] = {
                        "message": f"讲者信息完整，包含{len(info_fields)}个字段",
                        "confidence_score": min(len(info_fields) * 2, 8)
                    }
                    logger.info(f"讲者验证通过：信息完整性检查，{len(info_fields)}个字段")
                else:
                    result["verification_details"] = {
                        "message": f"讲者信息不完整，仅包含{len(info_fields)}个字段",
                        "confidence_score": len(info_fields)
                    }
                    logger.warning(f"讲者验证失败：信息不完整，仅{len(info_fields)}个字段")
        
        execution_time = time.time() - start_time
        log_mcp_tool_call("check_string_content", True, execution_time)
        logger.info(f"内容合规检查完成，验证通过: {result['verification_passed']}")
        
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
        # 首先检查讲者身份验证
        string_result = check_string_content(user_input)
        
        # 根据验证结果决定检查哪个文件夹
        extracted_info = string_result.get("extracted_info", {})
        doctor_name = extracted_info.get('name', '')
        hospital = extracted_info.get('hospital', '')
        department = extracted_info.get('department', '')
        contains_target = string_result.get("contains_target", False)
        
        # 确定要检查的文件夹前缀
        if contains_target:
            # 如果包含"鲍娜"，检查tinabao文件夹
            folder_prefix = "tinabao/"
            folder_type = "用户文件夹"
            folder_name = "tinabao"
            logger.info("检查鲍娜相关的tinabao文件夹")
        elif doctor_name and hospital and department:
            # 如果提取到完整的医生信息，检查医生专属文件夹
            doctor_folder_prefix = f"{doctor_name}-{hospital}-{department}/"
            folder_prefix = doctor_folder_prefix
            folder_type = "医生专属文件夹"
            folder_name = doctor_folder_prefix.rstrip('/')
            logger.info(f"检查医生专属文件夹: {doctor_folder_prefix}")
        elif doctor_name:
            # 如果只提取到医生姓名，尝试查找相关文件夹
            # 这里我们先尝试查找是否有匹配的文件夹
            folder_prefix = f"{doctor_name}-"
            folder_type = "医生相关文件夹"
            folder_name = f"{doctor_name}相关文件夹"
            logger.info(f"检查医生相关文件夹: {folder_prefix}")
        else:
            # 如果没有提取到医生信息，默认检查tinabao文件夹
            folder_prefix = "tinabao/"
            folder_type = "用户文件夹"
            folder_name = "tinabao"
            logger.info("未提取到医生信息，检查默认tinabao文件夹")
        
        # 检查对应的文件夹
        s3_result = list_s3_files_with_prefix(bucket_name, folder_prefix)
        
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
        target_word = string_result["target_word"]
        min_file_count = preaudit_config['min_file_count']
        verification_passed = string_result.get("verification_passed", False)
        verification_method = string_result.get("verification_method", "")
        verification_details = string_result.get("verification_details", {})
        
        # 获取文件列表用于显示
        file_list = s3_result.get("files", [])
        file_list_str = ""
        if file_list:
            file_list_str = "\n".join([f"  - {file}" for file in file_list])
        else:
            file_list_str = "  （无文件）"
        
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
        target_word = string_result["target_word"]
        min_file_count = preaudit_config['min_file_count']
        verification_passed = string_result.get("verification_passed", False)
        verification_method = string_result.get("verification_method", "")
        verification_details = string_result.get("verification_details", {})
        
        # 获取文件列表用于显示
        file_list = s3_result.get("files", [])
        file_list_str = ""
        if file_list:
            file_list_str = "\n".join([f"  - {file}" for file in file_list])
        else:
            file_list_str = "  （无文件）"
        
        # 新的预审逻辑
        if verification_passed:
            if verification_method == "direct_pass":
                # 包含"鲍娜"的情况，检查tinabao文件夹的文档数量
                if file_count > min_file_count:
                    result = f"""预审通过 - 恭喜！您的内容已通过初步审核

通过原因：
✅ 内容已通过内部验证流程
✅ {folder_type} '{folder_name}' 中支撑文档数量充足（{file_count}个文档，超过最低要求{min_file_count}个）

当前{folder_type}文档列表：
{file_list_str}

优化建议：
1. 建议在正式使用前进行最终人工审核
2. 确保所有引用的临床数据都有对应的支撑文档
3. 检查内容是否符合最新的监管指导原则
4. 考虑添加免责声明和适应症说明

后续步骤：
- 可以提交给合规部门进行详细审核
- 准备相关的问答材料以备现场使用
- 确保演讲者熟悉所有支撑材料的内容"""
                else:
                    result = f"""预审不通过 - 虽然内容通过验证，但支撑文档不足

问题详情：
✅ 内容已通过内部验证流程
❌ {folder_type} '{folder_name}' 中支撑文档不足（当前{file_count}个，需要超过{min_file_count}个）

当前{folder_type}文档列表：
{file_list_str}

具体改进建议：
1. 请补充以下类型的支撑文档到 '{folder_name}' 文件夹：
   - 产品说明书或处方信息
   - 相关临床研究数据
   - 安全性信息和不良反应资料
   - 监管部门批准的产品信息
   - 至少需要{min_file_count + 1}个支撑文档

整改步骤：
1. 上传更多相关支撑文档到S3存储桶的 '{folder_name}' 文件夹
2. 确保所有材料符合公司合规政策
3. 重新提交预审系统进行检查
4. 通过预审后提交人工详细审核"""
            
            elif verification_method == "info_extraction":
                # 信息提取验证通过的情况
                if file_count > min_file_count:
                    result = f"""预审通过 - 讲者身份信息验证成功

通过原因：
✅ 讲者身份信息完整，验证通过
✅ {folder_type} '{folder_name}' 中支撑文档数量充足（{file_count}个文档，超过最低要求{min_file_count}个）

讲者信息：
- 姓名: {extracted_info.get('name', '未提取')}
- 医院: {extracted_info.get('hospital', '未提取')}
- 科室: {extracted_info.get('department', '未提取')}
- 职称: {extracted_info.get('title', '未提取')}

当前{folder_type}文档列表：
{file_list_str}

验证详情：
{verification_details.get('message', '')}

后续步骤：
- 建议进行进一步的背景调查
- 确认讲者的专业领域匹配度
- 准备相关的演讲协议和材料"""
                else:
                    result = f"""预审不通过 - 讲者身份验证通过但支撑文档不足

问题详情：
✅ 讲者身份信息完整，验证通过
❌ {folder_type} '{folder_name}' 中支撑文档不足（当前{file_count}个，需要超过{min_file_count}个）

当前{folder_type}文档列表：
{file_list_str}

具体改进建议：
请补充更多支撑文档到 '{folder_name}' 文件夹以满足审核要求"""
        
        else:
            # 验证失败的情况
            reasons = []
            improvements = []
            
            if not extracted_info.get('name'):
                reasons.append("无法从文本中提取医生姓名")
                improvements.extend([
                    "请在文本中明确提供讲者的具体姓名，例如：",
                    "  - '本次活动我请到了张三医生'",
                    "  - '邀请了李四医生担任讲者'",
                    "  - '王五医生将为我们演讲'"
                ])
            else:
                reasons.append(f"讲者'{extracted_info.get('name')}'的信息不完整")
                improvements.extend([
                    f"讲者'{extracted_info.get('name')}'的信息验证失败：",
                    "  - 请提供更完整的讲者信息（姓名、医院、科室、职称）",
                    "  - 确保信息格式规范，例如：'张三医生，目前就职北京协和医院心内科，职称为主任医师'",
                    "  - 或联系讲者提供官方身份验证材料"
                ])
            
            if file_count <= min_file_count:
                reasons.append(f"{folder_type} '{folder_name}' 中支撑文档不足（当前{file_count}个，需要超过{min_file_count}个）")
                improvements.extend([
                    f"请补充以下类型的支撑文档到 '{folder_name}' 文件夹：",
                    "  - 产品说明书或处方信息",
                    "  - 相关临床研究数据",
                    "  - 安全性信息和不良反应资料",
                    "  - 监管部门批准的产品信息"
                ])
            
            result = f"""预审不通过 - 内容需要改进

问题详情：
❌ {'; '.join(reasons)}

当前{folder_type} '{folder_name}' 文档列表：
{file_list_str}

具体改进建议：
{chr(10).join([f"{i+1}. {imp}" for i, imp in enumerate(improvements)])}

整改步骤：
1. 根据上述建议补充讲者身份验证文档
2. 上传更多相关支撑文档到 '{folder_name}' 文件夹
3. 确保所有材料符合公司合规政策
4. 重新提交预审系统进行检查
5. 通过预审后提交人工详细审核

注意事项：
- 所有讲者都必须经过完整的身份验证流程
- 请确保讲者信息的真实性和专业性
- 如有疑问，请咨询医学事务部门或合规团队"""
        
        execution_time = time.time() - start_time
        log_preaudit_event(user_input, result, file_count, contains_target)
        log_mcp_tool_call("perform_preaudit", True, execution_time)
        
        if verification_passed and file_count > min_file_count:
            logger.info(f"预审通过：验证方法={verification_method}, 文档数量={file_count}")
        else:
            logger.warning(f"预审不通过：验证方法={verification_method}, 文档数量={file_count}")
        
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
