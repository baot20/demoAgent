#!/usr/bin/env python3
"""
Strands Agent 预审系统使用示例
"""

import os
import sys

def demo_with_mock_config():
    """使用模拟配置演示系统功能"""
    print("=" * 60)
    print("Strands Agent 预审系统 - 演示模式")
    print("=" * 60)
    
    # 模拟配置（不连接真实 AWS）
    from strands import Agent, tool
    from strands_tools import current_time
    
    @tool
    def mock_list_s3_files(bucket_name: str = "demo-bucket") -> dict:
        """模拟 S3 文件列表"""
        # 模拟不同的文件数量
        import random
        file_count = random.randint(1, 8)
        files = [f"file_{i}.txt" for i in range(1, file_count + 1)]
        
        return {
            "success": True,
            "file_count": file_count,
            "files": files,
            "bucket_name": bucket_name
        }
    
    @tool
    def mock_check_string_content(input_string: str, target_word: str = "鲍娜") -> dict:
        """模拟字符串内容检查"""
        contains_target = target_word in input_string
        
        return {
            "input_string": input_string,
            "target_word": target_word,
            "contains_target": contains_target,
            "string_length": len(input_string)
        }
    
    @tool
    def mock_perform_preaudit(user_input: str, bucket_name: str = "demo-bucket") -> str:
        """模拟完整预审流程"""
        # 获取模拟数据
        s3_result = mock_list_s3_files(bucket_name)
        string_result = mock_check_string_content(user_input)
        
        file_count = s3_result["file_count"]
        contains_target = string_result["contains_target"]
        target_word = string_result["target_word"]
        min_file_count = 3
        
        # 预审逻辑
        if contains_target and file_count > min_file_count:
            return f"预审通过 - 用户输入包含'{target_word}'且 S3 存储桶 '{bucket_name}' 中有 {file_count} 个文件（超过{min_file_count}个）"
        else:
            reasons = []
            if not contains_target:
                reasons.append(f"用户输入不包含'{target_word}'")
            if file_count <= min_file_count:
                reasons.append(f"S3 存储桶 '{bucket_name}' 中只有 {file_count} 个文件（需要超过{min_file_count}个）")
            
            return f"预审不通过 - {'; '.join(reasons)}"
    
    # 创建演示 Agent
    demo_agent = Agent(
        tools=[
            mock_list_s3_files,
            mock_check_string_content, 
            mock_perform_preaudit,
            current_time
        ]
    )
    
    # 演示用例
    test_inputs = [
        "你好鲍娜，今天天气不错",
        "你好，今天天气不错", 
        "鲍娜你好，请帮我处理这个文件",
        "这是一个测试消息"
    ]
    
    print("开始演示预审流程...\n")
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"演示 {i}: {user_input}")
        print("-" * 40)
        
        message = f"""
        请对用户输入进行预审检查："{user_input}"
        
        请执行以下步骤：
        1. 使用 mock_check_string_content 检查是否包含"鲍娜"
        2. 使用 mock_list_s3_files 检查文件数量
        3. 使用 mock_perform_preaudit 执行完整预审
        4. 给出明确的"预审通过"或"预审不通过"结论
        
        请简洁地报告结果。
        """
        
        try:
            response = demo_agent(message)
            print("=" * 60)
        except Exception as e:
            print(f"演示失败: {str(e)}")
            print("=" * 60)

def show_real_usage():
    """显示真实使用方法"""
    print("\n" + "=" * 60)
    print("真实使用方法")
    print("=" * 60)
    print("""
要使用真实的 AWS S3 预审系统，请按以下步骤操作：

1. 配置 AWS 凭证：
   cp .config.example .config
   # 编辑 .config 文件，填入你的 AWS 信息

2. 验证配置：
   python test_config.py

3. 运行预审系统：
   # 交互式模式
   python agent.py
   
   # 命令行模式
   python agent.py "你好鲍娜，今天天气不错"

4. 系统会自动：
   - 连接到你的 S3 存储桶
   - 检查文件数量
   - 检查输入内容
   - 给出预审结果
    """)

def main():
    """主函数"""
    print("Strands Agent S3 预审系统演示")
    
    # 检查是否有真实配置
    if os.path.exists('.config'):
        try:
            from config_reader import get_config
            config = get_config()
            if config.validate_config():
                print("✅ 检测到有效配置，可以运行真实预审系统")
                print("运行: python agent.py")
                show_real_usage()
                return
        except:
            pass
    
    print("🔧 未检测到有效配置，运行演示模式...")
    demo_with_mock_config()
    show_real_usage()

if __name__ == "__main__":
    main()
