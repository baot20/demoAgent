#!/usr/bin/env python3
"""
Chatbot触发测试脚本
测试各种用户输入是否能正确触发讲者身份验证工具
"""

from speaker_validation_tools import perform_preaudit, check_string_content

def test_trigger_phrases():
    """测试各种触发短语"""
    
    print("=" * 60)
    print("Chatbot 触发短语测试")
    print("=" * 60)
    
    # 各种可能的用户输入
    test_phrases = [
        # 直接验证请求
        {
            "category": "直接验证请求",
            "phrases": [
                "请验证张三医生的身份",
                "帮我检查李四教授的资质", 
                "验证这位专家的背景：钟南山院士",
                "审核讲者身份：王五主任医师",
                "确认KOL身份：张丹医生"
            ]
        },
        
        # 包含完整医生信息
        {
            "category": "完整医生信息",
            "phrases": [
                "张三医生，北京协和医院心内科主任医师",
                "钟南山，广州医科大学附属第一医院，呼吸内科，院士",
                "我想邀请李四教授做讲者，他来自上海交大医学院",
                "本次活动的讲者是王五医生，长海医院心血管外科",
                "请确认宋智钢医生的资格，上海长海医院心血管外科"
            ]
        },
        
        # 询问式验证
        {
            "category": "询问式验证",
            "phrases": [
                "这位医生符合讲者要求吗？张三，协和医院",
                "钟南山院士可以做我们的讲者吗？",
                "李四教授的资质如何？",
                "这个专家合适吗：王五主任",
                "能验证一下这位医生吗：张丹，皮肤科"
            ]
        },
        
        # 合规和预审相关
        {
            "category": "合规预审相关",
            "phrases": [
                "进行讲者预审：张三医生",
                "执行合规检查：李四教授",
                "开始专家审核流程",
                "检查讲者合规性：钟南山院士",
                "进行身份验证：王五医生"
            ]
        },
        
        # 文档相关
        {
            "category": "文档验证相关", 
            "phrases": [
                "检查张三医生的支撑文档",
                "验证李四教授的文档完整性",
                "查看专家的材料是否充足",
                "确认讲者的文件数量",
                "检查专属文件夹：王五医生"
            ]
        }
    ]
    
    for category_data in test_phrases:
        category = category_data["category"]
        phrases = category_data["phrases"]
        
        print(f"\n📋 {category}")
        print("-" * 40)
        
        for i, phrase in enumerate(phrases, 1):
            print(f"\n{i}. 测试短语: \"{phrase}\"")
            
            try:
                # 模拟chatbot的工具选择逻辑
                should_trigger = analyze_trigger_potential(phrase)
                print(f"   触发可能性: {'🟢 高' if should_trigger['high'] else '🟡 中' if should_trigger['medium'] else '🔴 低'}")
                print(f"   关键词匹配: {should_trigger['keywords']}")
                print(f"   推荐工具: {should_trigger['recommended_tool']}")
                
                # 实际测试工具调用
                if should_trigger['high'] or should_trigger['medium']:
                    print("   🔄 执行实际验证...")
                    result = perform_preaudit(phrase)
                    
                    if "预审通过" in result:
                        print("   ✅ 验证成功")
                    elif "预审部分通过" in result:
                        print("   🔶 部分通过")
                    elif "未找到讲者专属文件夹" in result:
                        print("   📁 文件夹不存在")
                    else:
                        print("   ❌ 验证失败")
                else:
                    print("   ⏭️  跳过实际验证（触发可能性低）")
                    
            except Exception as e:
                print(f"   ❌ 测试失败: {str(e)}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

def analyze_trigger_potential(phrase):
    """分析短语的触发可能性"""
    
    # 高优先级关键词
    high_priority_keywords = [
        "验证", "检查", "审核", "确认", "预审",
        "医生", "教授", "专家", "院士", "主任",
        "讲者", "KOL", "演讲者"
    ]
    
    # 中优先级关键词
    medium_priority_keywords = [
        "身份", "资质", "背景", "合规", "文档",
        "医院", "科室", "职称", "材料", "支撑"
    ]
    
    # 医生姓名模式
    doctor_patterns = [
        "张三", "李四", "王五", "钟南山", "宋智钢", "张丹"
    ]
    
    phrase_lower = phrase.lower()
    
    # 计算匹配分数
    high_matches = sum(1 for keyword in high_priority_keywords if keyword in phrase)
    medium_matches = sum(1 for keyword in medium_priority_keywords if keyword in phrase)
    doctor_matches = sum(1 for pattern in doctor_patterns if pattern in phrase)
    
    # 判断触发可能性
    high_trigger = high_matches >= 2 or (high_matches >= 1 and doctor_matches >= 1)
    medium_trigger = high_matches >= 1 or medium_matches >= 2
    
    # 推荐工具
    if "文档" in phrase or "材料" in phrase or "支撑" in phrase:
        recommended_tool = "list_s3_files"
    elif any(word in phrase for word in ["验证", "检查", "审核", "预审"]):
        recommended_tool = "perform_preaudit"
    else:
        recommended_tool = "check_string_content"
    
    # 匹配的关键词
    matched_keywords = []
    matched_keywords.extend([kw for kw in high_priority_keywords if kw in phrase])
    matched_keywords.extend([kw for kw in medium_priority_keywords if kw in phrase])
    matched_keywords.extend([kw for kw in doctor_patterns if kw in phrase])
    
    return {
        "high": high_trigger,
        "medium": medium_trigger and not high_trigger,
        "keywords": matched_keywords,
        "recommended_tool": recommended_tool,
        "scores": {
            "high_matches": high_matches,
            "medium_matches": medium_matches,
            "doctor_matches": doctor_matches
        }
    }

def generate_chatbot_prompts():
    """生成chatbot系统提示词建议"""
    
    print("\n" + "=" * 60)
    print("Chatbot 系统提示词建议")
    print("=" * 60)
    
    system_prompt = """
当用户询问以下类型的问题时，请优先使用speaker-validation-precheck工具：

🎯 触发场景：
1. 验证医生/专家/教授身份和资质
2. 检查讲者背景信息和合规性
3. 审核演讲者资格和支撑文档
4. 确认KOL身份和专业背景
5. 进行讲者预审和合规检查

🔍 关键词识别：
- 身份验证：验证、检查、审核、确认、预审
- 人员类型：医生、教授、专家、院士、主任、讲者、KOL、演讲者
- 机构信息：医院、科室、职称、资质、背景
- 合规相关：合规、文档、材料、支撑、标准

📝 典型用户输入模式：
- "验证[姓名]医生的身份"
- "[姓名]，[医院][科室][职称]"
- "这位专家符合要求吗？"
- "检查讲者的资质"
- "进行预审流程"

🛠️ 工具选择建议：
- 完整验证流程 → perform_preaudit
- 身份信息检查 → check_string_content  
- 文档数量验证 → list_s3_files
- 系统配置查询 → get_current_config
"""
    
    print(system_prompt)
    
    print("\n💡 实施建议：")
    print("1. 将上述提示词添加到chatbot的系统提示中")
    print("2. 训练chatbot识别医生姓名+医院+科室的模式")
    print("3. 设置自动触发规则：包含2个以上关键词时自动调用工具")
    print("4. 优化工具描述，包含更多同义词和使用场景")
    print("5. 添加中英文对照，提高识别准确率")

if __name__ == "__main__":
    test_trigger_phrases()
    generate_chatbot_prompts()
