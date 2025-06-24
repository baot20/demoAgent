#!/usr/bin/env python3
"""
SpeakerValidationPreCheckSystem 演示
讲者身份验证系统使用示例 - 最新版本
"""

import os
import sys
from speaker_validation_tools import perform_preaudit, check_string_content

def demo_speaker_validation():
    """演示讲者身份验证功能"""
    print("=" * 60)
    print("SpeakerValidationPreCheckSystem - 演示模式")
    print("讲者身份验证系统 v2.1.0")
    print("=" * 60)
    
    # 模拟医药代表提交的讲者信息示例
    test_cases = [
        {
            "content": "本次活动我请到了鲍娜医生，目前就职长海医院demo科室，职称为副主任医生。",
            "scenario": "鲍娜医生（内部验证）",
            "expected": "直接通过身份验证，检查tinabao/文件夹",
            "folder": "tinabao/"
        },
        {
            "content": "本次活动我请到了张三医生，目前就职长海医院心内科，职称为主任医师。",
            "scenario": "张三医生（专属文件夹验证）", 
            "expected": "EXA搜索验证 + 检查张三-长海医院-心内科/文件夹",
            "folder": "张三-长海医院-心内科/"
        },
        {
            "content": "我们邀请了宋智钢医生，他来自上海长海医院心血管外科，职称为主任医师。",
            "scenario": "宋智钢医生（专属文件夹验证）",
            "expected": "EXA搜索验证 + 检查宋智钢-上海长海医院-心血管外科/文件夹",
            "folder": "宋智钢-上海长海医院-心血管外科/"
        },
        {
            "content": "钟南山 广州医科大学附属第一医院 呼吸内科 院士",
            "scenario": "钟南山院士（知名医生）",
            "expected": "EXA搜索应该成功，检查专属文件夹",
            "folder": "钟南山-广州医科大学附属第一医院-呼吸内科/"
        },
        {
            "content": "今天有个医生来讲课。",
            "scenario": "信息不完整的讲者描述",
            "expected": "无法提取医生姓名，验证失败",
            "folder": "无法确定"
        },
        {
            "content": "张丹 上海市长海医院 皮肤科 主任",
            "scenario": "张丹医生（一般医生）",
            "expected": "EXA搜索可能失败，但信息完整",
            "folder": "张丹-上海市长海医院-皮肤科/"
        }
    ]
    
    print("🔍 开始演示讲者身份验证流程...")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📋 测试案例 {i}: {test_case['scenario']}")
        print(f"   输入内容: {test_case['content']}")
        print(f"   预期结果: {test_case['expected']}")
        print(f"   检查文件夹: {test_case['folder']}")
        print()
        
        try:
            # 执行身份验证检查
            print("   🔄 执行身份验证...")
            verification_result = check_string_content(test_case['content'])
            
            print(f"   验证结果: {'✅ 通过' if verification_result['verification_passed'] else '❌ 失败'}")
            print(f"   验证方法: {verification_result['verification_method']}")
            
            if verification_result['extracted_info']:
                info = verification_result['extracted_info']
                print(f"   提取信息: 姓名={info.get('name', '无')}, 医院={info.get('hospital', '无')}, 科室={info.get('department', '无')}, 职称={info.get('title', '无')}")
            
            # 显示EXA搜索结果
            if 'exa_search_results' in verification_result and verification_result['exa_search_results']:
                exa_result = verification_result['exa_search_results']
                if exa_result.get('success'):
                    print(f"   🌐 EXA搜索: 成功，匹配分数 {exa_result.get('match_score', 0)}/10")
                    print(f"   搜索结果: {exa_result.get('total_results', 0)}个结果")
                else:
                    print(f"   🌐 EXA搜索: 失败，{exa_result.get('error', '未知错误')}")
            
            print()
            
            # 执行完整预审流程
            print("   🔄 执行完整预审流程...")
            preaudit_result = perform_preaudit(test_case['content'])
            
            # 显示预审结果摘要
            if "预审通过" in preaudit_result:
                print("   🎉 预审结果: ✅ 通过")
            elif "预审部分通过" in preaudit_result:
                print("   ⚠️  预审结果: 🔶 部分通过")
            else:
                print("   ❌ 预审结果: ❌ 不通过")
            
            # 提取关键信息
            if "网络搜索验证通过" in preaudit_result:
                print("   🌐 网络验证: ✅ 通过")
            elif "网络搜索验证失败" in preaudit_result:
                print("   🌐 网络验证: ❌ 失败")
            elif "内部验证流程" in preaudit_result:
                print("   🔒 内部验证: ✅ 通过")
            
            if "支撑文档数量充足" in preaudit_result:
                print("   📁 文档验证: ✅ 充足")
            elif "支撑文档不足" in preaudit_result:
                print("   📁 文档验证: ❌ 不足")
            
        except Exception as e:
            print(f"   ❌ 测试失败: {str(e)}")
        
        print("-" * 60)
        print()
    
    print("🎯 演示总结:")
    print("1. 鲍娜医生: 特殊标识，不触发EXA搜索，直接验证通过")
    print("2. 知名医生: EXA搜索匹配分数高，网络验证通过")
    print("3. 一般医生: EXA搜索匹配分数低，网络验证可能失败")
    print("4. 所有医生: 都需要检查对应的专属文件夹文档数量")
    print("5. 双重验证: 身份验证 + 文档验证 = 最终结果")
    print()
    print("=" * 60)

def demo_configuration():
    """演示配置信息"""
    print("📋 系统配置信息:")
    print("-" * 30)
    
    try:
        from speaker_validation_tools import aws_config, s3_config, preaudit_config, exa_config
        
        print(f"AWS 区域: {aws_config['region']}")
        print(f"S3 存储桶: {s3_config['bucket_name']}")
        print(f"特殊标识: {preaudit_config['target_word']}")
        print(f"最低文档数: {preaudit_config['min_file_count']}")
        print(f"EXA API: {'已配置' if exa_config.get('api_key') else '未配置'}")
        
    except Exception as e:
        print(f"配置读取失败: {str(e)}")
    
    print()

def main():
    """主函数"""
    print("🚀 启动讲者身份验证系统演示")
    print()
    
    # 显示配置信息
    demo_configuration()
    
    # 演示验证功能
    demo_speaker_validation()
    
    print("✨ 演示完成！")
    print()
    print("💡 提示:")
    print("- 设置 EXA_API_KEY 以启用网络搜索功能")
    print("- 上传文档到对应的S3文件夹以通过文档验证")
    print("- 查看 README.md 了解更多使用方法")

if __name__ == "__main__":
    main()
    def mock_extract_speaker_info(content: str) -> dict:
        """模拟从文本中提取讲者信息"""
        info = {
            'name': '',
            'hospital': '',
            'department': '',
            'title': ''
        }
        
        # 简化的信息提取逻辑
        name_patterns = [
            r'请到了([^，。！？\s]{2,4})医生',
            r'邀请了([^，。！？\s]{2,4})医生',
            r'([^，。！？\s]{2,4})医生',
            r'([^，。！？\s]{2,4})教授'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, content)
            if match:
                name = match.group(1)
                if name not in ['本次', '今天', '明天', '昨天', '活动', '会议']:
                    info['name'] = name
                    break
        
        if '医院' in content:
            hospital_match = re.search(r'([^，。！？\s]*医院)', content)
            if hospital_match:
                info['hospital'] = hospital_match.group(1)
        
        if any(dept in content for dept in ['科', '科室', '部门']):
            dept_match = re.search(r'([^，。！？\s]*科)', content)
            if dept_match:
                info['department'] = dept_match.group(1)
        
        if any(title in content for title in ['主任医师', '副主任医师', '主治医师', '教授']):
            title_match = re.search(r'([^，。！？\s]*(?:主任医师|副主任医师|主治医师|教授))', content)
            if title_match:
                info['title'] = title_match.group(1)
        
        return info
    
    @tool
    def mock_speaker_verification(content: str, target_word: str = "鲍娜") -> dict:
        """模拟讲者身份验证"""
        # 检查特殊标识
        contains_target = target_word in content
        
        if contains_target:
            return {
                "verification_passed": True,
                "verification_method": "direct_pass",
                "message": f"包含特殊标识'{target_word}'，直接通过验证",
                "confidence_score": 10
            }
        
        # 提取讲者信息
        extracted_info = mock_extract_speaker_info(content)
        complete_fields = sum(1 for field in extracted_info.values() if field)
        
        if complete_fields >= 3:
            return {
                "verification_passed": True,
                "verification_method": "info_extraction",
                "message": f"讲者信息完整，包含{complete_fields}个字段",
                "confidence_score": complete_fields * 2,
                "extracted_info": extracted_info
            }
        else:
            return {
                "verification_passed": False,
                "verification_method": "info_extraction", 
                "message": f"讲者信息不完整，仅包含{complete_fields}个字段",
                "confidence_score": complete_fields,
                "extracted_info": extracted_info
            }
    
    @tool
    def mock_check_supporting_docs(doc_type: str = "speaker_credentials") -> dict:
        """模拟支撑文档检查"""
        import random
        doc_count = random.randint(1, 8)
        doc_types = [
            "讲者简历",
            "医师执业证书", 
            "学术论文发表记录",
            "医院工作证明",
            "专业资质证书",
            "学术会议演讲记录",
            "临床经验证明",
            "继续教育证书"
        ]
        
        available_docs = doc_types[:doc_count]
        
        return {
            "document_count": doc_count,
            "available_documents": available_docs,
            "meets_requirement": doc_count > 3
        }
    
    @tool
    def mock_speaker_preaudit(content: str) -> str:
        """模拟完整的讲者身份验证流程"""
        verification_result = mock_speaker_verification(content)
        doc_check = mock_check_supporting_docs()
        
        is_verified = verification_result["verification_passed"]
        has_enough_docs = doc_check["meets_requirement"]
        doc_count = doc_check["document_count"]
        
        if is_verified and has_enough_docs:
            method = verification_result["verification_method"]
            if method == "direct_pass":
                return f"""讲者验证通过 - 恭喜！讲者身份已通过验证

通过原因：
✅ 包含特殊标识'鲍娜'，直接通过验证
✅ 支撑文档数量充足（{doc_count}个文档，超过最低要求3个）

建议使用场景：
1. 适合高级别学术会议演讲
2. 可用于重要产品发布活动
3. 适合专业医学培训项目
4. 可参与权威学术讨论

后续步骤：
- 可以安排具体的演讲时间和主题
- 准备相关的演讲支持材料
- 确认讲者的时间安排和技术需求"""
            else:
                extracted = verification_result.get("extracted_info", {})
                return f"""讲者验证通过 - 讲者身份信息验证成功

验证结果：
✅ 讲者信息完整性验证通过
✅ 支撑文档数量充足（{doc_count}个文档）

讲者信息：
- 姓名: {extracted.get('name', '未提取')}
- 医院: {extracted.get('hospital', '未提取')}
- 科室: {extracted.get('department', '未提取')}
- 职称: {extracted.get('title', '未提取')}

可信度评估：
- 信息完整度: {verification_result['confidence_score']}/10
- 文档支撑度: 充足

建议使用场景：
1. 适合专业学术交流活动
2. 可用于产品教育培训
3. 适合医学继续教育项目

后续步骤：
- 建议进行进一步的背景调查
- 确认讲者的专业领域匹配度
- 准备相关的演讲协议和材料"""
        else:
            issues = []
            suggestions = []
            
            if not is_verified:
                issues.append(verification_result["message"])
                if verification_result["verification_method"] == "info_extraction":
                    suggestions.extend([
                        "请提供更完整的讲者信息：",
                        "  - 讲者的完整姓名",
                        "  - 所在医院的全称",
                        "  - 具体的科室或部门",
                        "  - 职称或学术头衔"
                    ])
            
            if not has_enough_docs:
                issues.append(f"支撑文档不足（当前{doc_count}个，需要超过3个）")
                suggestions.extend([
                    "请补充以下类型的支撑文档：",
                    "  - 讲者的详细简历",
                    "  - 医师执业证书或资质证明",
                    "  - 学术论文发表记录",
                    "  - 医院工作证明或推荐信"
                ])
            
            return f"""讲者验证不通过 - 需要补充信息

问题详情：
❌ {'; '.join(issues)}

具体改进建议：
{chr(10).join([f"{i+1}. {sug}" for i, sug in enumerate(suggestions)])}

整改步骤：
1. 根据上述建议补充讲者信息和文档
2. 确保所有信息的真实性和准确性
3. 重新提交验证系统进行检查
4. 通过验证后可安排具体的演讲事宜

注意事项：
- 所有讲者信息都必须经过完整的验证流程
- 请确保讲者信息的真实性和专业性
- 如有疑问，请咨询医学事务部门或合规团队"""
    
    # 创建演示 Agent
    demo_agent = Agent(
        tools=[
            mock_extract_speaker_info,
            mock_speaker_verification,
            mock_check_supporting_docs,
            mock_speaker_preaudit,
            current_time
        ]
    )
    
    print("开始演示讲者身份验证流程...\n")
    
    for i, case in enumerate(test_cases, 1):
        print(f"演示 {i}: {case['scenario']}")
        print(f"讲者信息: {case['content']}")
        print(f"预期结果: {case['expected']}")
        print("-" * 40)
        
        message = f"""
        请对医药代表提交的讲者信息进行身份验证："{case['content']}"
        
        请执行以下步骤：
        1. 使用 mock_extract_speaker_info 提取讲者信息
        2. 使用 mock_speaker_verification 验证讲者身份
        3. 使用 mock_check_supporting_docs 检查支撑文档
        4. 使用 mock_speaker_preaudit 执行完整验证流程
        
        请提供详细的验证结果和建议。
        """
        
        try:
            response = demo_agent(message)
            print("=" * 60)
        except Exception as e:
            print(f"演示失败: {str(e)}")
            print("=" * 60)

def show_speaker_validation_usage():
    """显示讲者身份验证系统使用方法"""
    print("\n" + "=" * 60)
    print("讲者身份验证系统使用方法")
    print("=" * 60)
    print("""
要使用真实的讲者身份验证系统，请按以下步骤操作：

1. 配置系统：
   cp .config.example .config
   # 编辑 .config 文件，填入你的AWS信息和验证标准

2. 验证配置：
   python test_config.py

3. 运行验证系统：
   # 交互式模式（推荐）
   python agent.py
   
   # 命令行模式
   python agent.py "本次活动我请到了张三医生，目前就职北京协和医院心内科"

4. 系统功能：
   - 特殊标识直通验证（如包含"鲍娜"）
   - 讲者信息提取和完整性检查
   - 网络搜索验证讲者身份真实性
   - 支撑文档数量和质量验证
   - 提供详细的验证报告和改进建议

5. 适用场景：
   - 学术会议讲者身份验证
   - 医学培训讲师资质审核
   - 产品发布会专家身份确认
   - 继续教育项目讲者筛选

6. 验证标准：
   - 讲者信息完整性（姓名、医院、科室、职称）
   - 支撑文档充足性（简历、证书、论文等）
   - 身份信息真实性（网络搜索验证）
   - 专业匹配度（领域相关性）
    """)

def main():
    """主函数"""
    print("SpeakerValidationPreCheckSystem 演示")
    print("讲者身份验证系统")
    
    # 检查是否有真实配置
    if os.path.exists('.config'):
        try:
            from config_reader import get_config
            config = get_config()
            if config.validate_config():
                print("✅ 检测到有效配置，可以运行真实验证系统")
                print("运行: python agent.py")
                show_speaker_validation_usage()
                return
        except:
            pass
    
    print("🔧 未检测到有效配置，运行演示模式...")
    demo_speaker_validation()
    show_speaker_validation_usage()

if __name__ == "__main__":
    main()
