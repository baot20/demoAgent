#!/usr/bin/env python3
"""
Supervisor Agent 使用示例
展示如何与 S3 预审 Agent 进行交互
"""

from strands import Agent, tool
from strands_tools import current_time
from agent_metadata import get_agent_metadata
import json

# 模拟的预审 Agent 调用函数
@tool
def call_preaudit_agent(user_input: str, detailed_check: bool = False) -> str:
    """
    调用 S3 预审 Agent 进行内容和文件检查
    
    Args:
        user_input: 用户输入的待检查内容
        detailed_check: 是否需要详细的检查过程说明
        
    Returns:
        预审 Agent 的响应结果
    """
    # 这里模拟调用真实的预审 Agent
    # 在实际应用中，这里会调用真实的 agent.py 中的 preaudit_agent
    
    from agent import preaudit_agent
    
    if detailed_check:
        message = f"""
        请对用户输入进行详细的预审检查："{user_input}"
        
        请执行以下步骤并详细说明每个步骤的结果：
        1. 使用 get_current_config 工具获取当前配置信息
        2. 使用 check_string_content 工具检查用户输入是否包含目标词汇
        3. 使用 list_s3_files 工具检查 S3 存储桶中的文件数量
        4. 使用 perform_preaudit 工具执行完整的预审流程
        5. 根据预审结果给出明确的"预审通过"或"预审不通过"的结论
        
        请提供详细的检查过程和最终建议。
        """
    else:
        message = f"""
        请对用户输入进行预审检查："{user_input}"
        
        请使用 perform_preaudit 工具执行预审并给出简洁的结果。
        """
    
    try:
        response = preaudit_agent(message)
        return f"预审Agent响应: {response}"
    except Exception as e:
        return f"预审Agent调用失败: {str(e)}"

@tool
def get_preaudit_agent_info() -> str:
    """
    获取预审 Agent 的详细信息和能力描述
    
    Returns:
        预审 Agent 的元数据信息
    """
    metadata = get_agent_metadata()
    
    info = f"""
    Agent名称: {metadata['name']} v{metadata['version']}
    类型: {metadata['type']}
    
    核心能力:
    {chr(10).join([f"• {cap}" for cap in metadata['capabilities']])}
    
    适用场景:
    {chr(10).join([f"• {uc['scenario']}: {uc['description']}" for uc in metadata['use_cases']])}
    
    可用工具:
    {chr(10).join([f"• {tool['name']}: {tool['purpose']}" for tool in metadata['tools']])}
    
    典型响应时间: {metadata['performance']['typical_response_time']}
    """
    
    return info

@tool
def batch_preaudit_check(input_list: list) -> str:
    """
    批量执行预审检查
    
    Args:
        input_list: 待检查的输入列表
        
    Returns:
        批量检查结果摘要
    """
    results = []
    
    for i, user_input in enumerate(input_list, 1):
        result = call_preaudit_agent(user_input, detailed_check=False)
        
        # 简化结果判断
        if "预审通过" in result:
            status = "✅ 通过"
        elif "预审不通过" in result:
            status = "❌ 不通过"
        else:
            status = "⚠️ 错误"
        
        results.append(f"{i}. {user_input[:30]}... -> {status}")
    
    summary = f"""
    批量预审检查结果:
    {chr(10).join(results)}
    
    总计: {len(input_list)} 项检查完成
    通过: {len([r for r in results if '✅' in r])} 项
    不通过: {len([r for r in results if '❌' in r])} 项
    错误: {len([r for r in results if '⚠️' in r])} 项
    """
    
    return summary

# 创建 Supervisor Agent
supervisor_agent = Agent(
    name="PreauditSupervisor",
    description="""
    预审系统监督Agent - 负责协调和管理S3预审Agent的工作
    
    主要职责:
    1. 理解用户的预审需求
    2. 调用适当的预审Agent进行检查
    3. 解释预审结果并提供建议
    4. 处理批量预审请求
    5. 提供预审系统的使用指导
    """,
    instructions="""
    你是一个预审系统的监督Agent。当用户有预审需求时，你需要：
    
    1. 分析用户的请求类型（单个检查、批量检查、信息查询等）
    2. 选择合适的工具来满足用户需求
    3. 调用预审Agent执行具体的检查工作
    4. 解释预审结果，提供清晰的说明和建议
    5. 如果用户需要了解预审系统，提供详细的功能介绍
    
    可用的操作:
    - call_preaudit_agent: 调用预审Agent进行单个内容检查
    - get_preaudit_agent_info: 获取预审Agent的详细信息
    - batch_preaudit_check: 执行批量预审检查
    - current_time: 获取当前时间
    
    始终保持专业、友好的态度，并确保用户理解预审结果的含义。
    """,
    tools=[
        call_preaudit_agent,
        get_preaudit_agent_info, 
        batch_preaudit_check,
        current_time
    ]
)

def demo_supervisor_interactions():
    """演示 Supervisor Agent 的各种交互场景"""
    
    print("=" * 60)
    print("Supervisor Agent 交互演示")
    print("=" * 60)
    
    # 场景1: 单个预审检查
    print("\n场景1: 单个预审检查")
    print("-" * 40)
    
    message1 = """
    我需要对以下内容进行预审检查："你好鲍娜，今天天气不错，请帮我处理这个文档"
    请帮我检查这个内容是否能通过预审。
    """
    
    try:
        response1 = supervisor_agent(message1)
        print("Supervisor响应:")
        print(response1)
    except Exception as e:
        print(f"演示失败: {str(e)}")
    
    print("\n" + "=" * 60)
    
    # 场景2: 了解预审系统
    print("\n场景2: 了解预审系统")
    print("-" * 40)
    
    message2 = """
    我想了解一下预审系统的功能和使用方法，请详细介绍一下。
    """
    
    try:
        response2 = supervisor_agent(message2)
        print("Supervisor响应:")
        print(response2)
    except Exception as e:
        print(f"演示失败: {str(e)}")
    
    print("\n" + "=" * 60)

def main():
    """主函数"""
    print("Supervisor Agent 使用示例")
    
    # 检查预审Agent是否可用
    try:
        from agent import preaudit_agent
        print("✅ 预审Agent加载成功")
    except Exception as e:
        print(f"❌ 预审Agent加载失败: {str(e)}")
        print("请确保agent.py文件存在且配置正确")
        return
    
    # 运行演示
    demo_supervisor_interactions()
    
    print("\n" + "=" * 60)
    print("交互式模式")
    print("=" * 60)
    print("你现在可以与Supervisor Agent进行交互")
    print("输入 'quit' 退出")
    
    while True:
        try:
            user_input = input("\n请输入你的请求: ").strip()
            
            if user_input.lower() == 'quit':
                print("再见！")
                break
            
            if not user_input:
                continue
            
            print("\nSupervisor Agent 处理中...")
            print("-" * 40)
            
            response = supervisor_agent(user_input)
            print("Supervisor响应:")
            print(response)
            print("-" * 40)
            
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()
