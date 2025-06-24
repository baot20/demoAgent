#!/usr/bin/env python3
"""
配置文件读取模块
读取 .config 文件中的 AWS 凭证和其他配置信息
"""

import os
import configparser
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ConfigReader:
    """配置文件读取器"""
    
    def __init__(self, config_file_path: str = ".config"):
        """
        初始化配置读取器
        
        Args:
            config_file_path: 配置文件路径，默认为 .config
        """
        self.config_file_path = config_file_path
        self.config = configparser.ConfigParser()
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if not os.path.exists(self.config_file_path):
                raise FileNotFoundError(f"配置文件 {self.config_file_path} 不存在")
            
            self.config.read(self.config_file_path, encoding='utf-8')
            logger.info(f"配置文件 {self.config_file_path} 加载成功")
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            raise
    
    def get_aws_config(self) -> Dict[str, str]:
        """
        获取 AWS 配置信息
        
        Returns:
            包含 AWS 凭证和区域信息的字典
        """
        try:
            aws_config = {
                'access_key_id': self.config.get('AWS', 'ACCESS_KEY_ID'),
                'secret_access_key': self.config.get('AWS', 'SECRET_ACCESS_KEY'),
                'region': self.config.get('AWS', 'REGION')
            }
            
            # 验证配置是否为空或默认值
            for key, value in aws_config.items():
                if not value or value.startswith('your_'):
                    logger.warning(f"AWS 配置项 {key} 未正确设置")
            
            return aws_config
            
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            logger.error(f"AWS 配置读取失败: {str(e)}")
            raise
    
    def get_s3_config(self) -> Dict[str, str]:
        """
        获取 S3 配置信息
        
        Returns:
            包含 S3 配置的字典
        """
        try:
            s3_config = {
                'bucket_name': self.config.get('S3', 'BUCKET_NAME')
            }
            
            if s3_config['bucket_name'].startswith('your-'):
                logger.warning("S3 存储桶名称未正确设置")
            
            return s3_config
            
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            logger.error(f"S3 配置读取失败: {str(e)}")
            raise
    
    def get_cloudwatch_config(self) -> Dict[str, str]:
        """
        获取 CloudWatch 配置信息
        
        Returns:
            包含 CloudWatch 配置的字典
        """
        try:
            cloudwatch_config = {
                'log_group_name': self.config.get('CLOUDWATCH', 'LOG_GROUP_NAME'),
                'log_stream_name': self.config.get('CLOUDWATCH', 'LOG_STREAM_NAME')
            }
            
            return cloudwatch_config
            
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            logger.error(f"CloudWatch 配置读取失败: {str(e)}")
            # 返回默认配置
            return {
                'log_group_name': '/aws/speakervalidation/precheck',
                'log_stream_name': 'speaker-validation-logs'
            }
    
    def get_exa_config(self) -> Dict[str, str]:
        """
        获取 EXA 配置信息
        
        Returns:
            包含 EXA API key 的字典
        """
        try:
            exa_config = {
                'api_key': self.config.get('EXA', 'EXA_API_KEY')
            }
            
            if not exa_config['api_key'] or exa_config['api_key'].startswith('your_'):
                logger.warning("EXA API key 未正确设置")
            
            return exa_config
            
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            logger.warning(f"EXA 配置读取失败: {str(e)}，将使用环境变量")
            # 如果配置文件中没有EXA配置，尝试从环境变量读取
            import os
            api_key = os.getenv('EXA_API_KEY', '')
            return {'api_key': api_key}

    def get_preaudit_config(self) -> Dict[str, Any]:
        """
        获取预审配置信息
        
        Returns:
            包含预审配置的字典
        """
        try:
            preaudit_config = {
                'target_word': self.config.get('PREAUDIT', 'TARGET_WORD'),
                'min_file_count': self.config.getint('PREAUDIT', 'MIN_FILE_COUNT')
            }
            
            return preaudit_config
            
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            logger.error(f"预审配置读取失败: {str(e)}")
            raise
    
    def get_all_config(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有配置信息
        
        Returns:
            包含所有配置的字典
        """
        return {
            'aws': self.get_aws_config(),
            's3': self.get_s3_config(),
            'preaudit': self.get_preaudit_config(),
            'cloudwatch': self.get_cloudwatch_config(),
            'exa': self.get_exa_config()
        }
    
    def validate_config(self) -> bool:
        """
        验证配置是否完整和有效
        
        Returns:
            配置是否有效
        """
        try:
            aws_config = self.get_aws_config()
            s3_config = self.get_s3_config()
            preaudit_config = self.get_preaudit_config()
            
            # 检查必要的配置项
            required_checks = [
                (aws_config['access_key_id'], "AWS Access Key ID"),
                (aws_config['secret_access_key'], "AWS Secret Access Key"),
                (aws_config['region'], "AWS Region"),
                (s3_config['bucket_name'], "S3 Bucket Name")
            ]
            
            for value, name in required_checks:
                if not value or value.startswith('your_'):
                    logger.error(f"{name} 未正确配置")
                    return False
            
            logger.info("配置验证通过")
            return True
            
        except Exception as e:
            logger.error(f"配置验证失败: {str(e)}")
            return False

# 全局配置实例
config_reader = ConfigReader()

def get_config():
    """获取全局配置实例"""
    return config_reader
