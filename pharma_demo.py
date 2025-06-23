#!/usr/bin/env python3
"""
SpeakerValidationPreCheckSystem 演示
医药代表内容预审系统使用示例
"""

import os
import sys
from strands import Agent, tool
from strands_tools import current_time

def demo_pharma_preaudit():
    """演示医药代表内容预审功能"""
    print("=" * 60)
    print("SpeakerValidationPreCheckSystem - 演示模式")
    print("医药代表内容初步审核系统")
    print("=" * 60)
    
    # 模拟医药代表提交的内容示例
    test_cases = [
        {
            "content": "各位医生，今天我要为大家介绍我们公司的新产品。本次演讲内容已经过鲍娜审核。",
            "scenario": "包含审核标识的演讲内容",
            "expected": "应该通过预审"
        },
        {
            "content": "各位医生，今天我要为大家介绍我们公司的新产品。这是一个创新的治疗方案。",
            "scenario": "缺少审核标识的演讲内容", 
            "expected": "应该不通过预审"
        },
        {
            "content": "产品培训材料：本产品适用于治疗高血压，已通过鲍娜医学审核，请参考相关临床数据。",
            "scenario": "培训材料内容",
            "expected": "需要检查支撑文档"
        },
        {
            "content": "学术推广资料：基于最新临床研究，我们的产品显示出优异的疗效。审核人：鲍娜",
            "scenario": "学术推广材料",
            "expected": "需要综合评估"
        }
    ]
    
    # 模拟预审工具
    @tool
    def mock_pharma_check_content(content: str, reviewer: str = "鲍娜") -> dict:
        """模拟医药内容合规检查"""
        has_reviewer = reviewer in content
        return {
            "content": content,
            "reviewer": reviewer,
            "has_compliance_mark": has_reviewer,
            "content_type": "pharmaceutical_material"
        }
    
    @tool
    def mock_pharma_check_documents(doc_type: str = "clinical_support") -> dict:
        """模拟支撑文档检查"""
        import random
        doc_count = random.randint(1, 8)
        doc_types = [
            "产品说明书",
            "临床研究报告", 
            "安全性数据",
            "监管批准文件",
            "学术文献",
            "不良反应报告",
            "药物相互作用数据",
            "患者信息手册"
        ]
        
        available_docs = doc_types[:doc_count]
        
        return {
            "document_count": doc_count,
            "available_documents": available_docs,
            "meets_requirement": doc_count > 3
        }
    
    @tool
    def mock_pharma_preaudit(content: str) -> str:
        """模拟完整的医药预审流程"""
        content_check = mock_pharma_check_content(content)
        doc_check = mock_pharma_check_documents()
        
        has_compliance = content_check["has_compliance_mark"]
        has_enough_docs = doc_check["meets_requirement"]
        doc_count = doc_check["document_count"]
        
        if has_compliance and has_enough_docs:
            return f"""预审通过 - 恭喜！您的医药内容已通过初步审核

通过原因：
✅ 内容包含必要的审核人员标识 '鲍娜'
✅ 支撑文档数量充足（{doc_count}个文档，超过最低要求3个）

优化建议：
1. 建议在正式使用前进行最终医学审核
2. 确保所有临床数据都有对应的支撑文档
3. 检查内容是否符合最新的监管指导原则
4. 考虑添加适应症说明和安全性信息

后续步骤：
- 可以提交给医学事务部门进行详细审核
- 准备相关的医学问答材料
- 确保演讲者熟悉所有支撑材料的内容"""
        else:
            issues = []
            suggestions = []
            
            if not has_compliance:
                issues.append("内容缺少必要的审核人员标识 '鲍娜'")
                suggestions.extend([
                    "请在内容中添加审核人员标识 '鲍娜'",
                    "标识应放在显眼位置，如标题页或结尾处",
                    "确保标识清晰可见，符合合规要求"
                ])
            
            if not has_enough_docs:
                issues.append(f"支撑文档不足（当前{doc_count}个，需要超过3个）")
                suggestions.extend([
                    "请补充以下类型的支撑文档：",
                    "  - 产品说明书或处方信息",
                    "  - 相关临床研究数据", 
                    "  - 安全性信息和不良反应资料",
                    "  - 监管部门批准的产品信息"
                ])
            
            return f"""预审不通过 - 医药内容需要改进

问题详情：
❌ {'; '.join(issues)}

具体改进建议：
{chr(10).join([f"{i+1}. {sug}" for i, sug in enumerate(suggestions)])}

整改步骤：
1. 根据上述建议修改内容和补充文档
2. 确保所有材料符合医药行业合规政策
3. 重新提交预审系统进行检查
4. 通过预审后提交医学事务部门详细审核

注意事项：
- 所有医药推广材料都必须经过完整的审核流程
- 请确保内容的医学准确性和科学性
- 如有疑问，请咨询合规部门或医学事务团队"""
    
    # 创建演示 Agent
    demo_agent = Agent(
        tools=[
            mock_pharma_check_content,
            mock_pharma_check_documents,
            mock_pharma_preaudit,
            current_time
        ]
    )
    
    print("开始演示医药代表内容预审流程...\n")
    
    for i, case in enumerate(test_cases, 1):
        print(f"演示 {i}: {case['scenario']}")
        print(f"内容: {case['content']}")
        print(f"预期: {case['expected']}")
        print("-" * 40)
        
        message = f"""
        请对医药代表提交的内容进行预审检查："{case['content']}"
        
        请执行以下步骤：
        1. 使用 mock_pharma_check_content 检查合规标识
        2. 使用 mock_pharma_check_documents 检查支撑文档
        3. 使用 mock_pharma_preaudit 执行完整预审
        4. 为医药代表提供专业的改进建议
        
        请提供详细的审核结果和建议。
        """
        
        try:
            response = demo_agent(message)
            print("=" * 60)
        except Exception as e:
            print(f"演示失败: {str(e)}")
            print("=" * 60)

def show_pharma_usage():
    """显示医药代表系统使用方法"""
    print("\n" + "=" * 60)
    print("医药代表内容预审系统使用方法")
    print("=" * 60)
    print("""
要使用真实的医药代表内容预审系统，请按以下步骤操作：

1. 配置系统：
   cp .config.example .config
   # 编辑 .config 文件，填入你的AWS信息和审核标准

2. 验证配置：
   python test_config.py

3. 运行预审系统：
   # 交互式模式（推荐）
   python agent.py
   
   # 命令行模式
   python agent.py "各位医生，今天我要介绍新产品，已经过鲍娜审核"

4. 系统功能：
   - 检查内容是否包含必要的审核人员标识
   - 验证支撑文档数量是否满足要求
   - 提供具体的改进建议和整改步骤
   - 为销售团队提供合规指导

5. 适用场景：
   - 医药代表演讲内容预审
   - 学术推广材料合规检查
   - 培训资料完整性验证
   - 销售支持文档审核
    """)

def main():
    """主函数"""
    print("SpeakerValidationPreCheckSystem 演示")
    print("医药代表内容初步审核系统")
    
    # 检查是否有真实配置
    if os.path.exists('.config'):
        try:
            from config_reader import get_config
            config = get_config()
            if config.validate_config():
                print("✅ 检测到有效配置，可以运行真实预审系统")
                print("运行: python agent.py")
                show_pharma_usage()
                return
        except:
            pass
    
    print("🔧 未检测到有效配置，运行演示模式...")
    demo_pharma_preaudit()
    show_pharma_usage()

if __name__ == "__main__":
    main()
