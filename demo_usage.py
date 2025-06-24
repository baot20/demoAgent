#!/usr/bin/env python3
"""
SpeakerValidationPreCheckSystem 使用示例 v2.1.0
讲者身份验证系统 - EXA集成版本
"""

import os
import sys

def demo_with_real_system():
    """使用真实系统演示功能"""
    print("=" * 60)
    print("SpeakerValidationPreCheckSystem - 真实系统演示")
    print("讲者身份验证系统 v2.1.0")
    print("=" * 60)
    
    try:
        from speaker_validation_tools import perform_preaudit, check_string_content
        
        # 测试用例
        test_cases = [
            {
                "name": "鲍娜医生（内部验证）",
                "input": "我请到了鲍娜医生，目前就职长海医院demo科室",
                "description": "特殊标识，不触发EXA搜索，检查tinabao/文件夹"
            },
            {
                "name": "张三医生（专属文件夹）",
                "input": "我请到了张三医生，目前就职长海医院心内科，职称为主任医师",
                "description": "EXA搜索验证，检查张三-长海医院-心内科/文件夹"
            },
            {
                "name": "钟南山院士（知名医生）",
                "input": "钟南山 广州医科大学附属第一医院 呼吸内科 院士",
                "description": "EXA搜索应该成功，检查专属文件夹"
            },
            {
                "name": "无具体姓名",
                "input": "我请到了医生，目前就职长海医院",
                "description": "无法提取医生姓名，验证失败"
            }
        ]
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n{i}. 测试: {case['name']}")
            print(f"   描述: {case['description']}")
            print(f"   输入: {case['input']}")
            
            try:
                # 执行身份验证
                result = check_string_content(case['input'])
                print(f"   身份验证: {'✅ 通过' if result['verification_passed'] else '❌ 失败'}")
                print(f"   验证方法: {result['verification_method']}")
                
                if result['extracted_info']:
                    info = result['extracted_info']
                    print(f"   提取信息: {info}")
                
                # 执行完整预审
                preaudit_result = perform_preaudit(case['input'])
                if "预审通过" in preaudit_result:
                    print("   预审结果: ✅ 通过")
                else:
                    print("   预审结果: ❌ 不通过")
                
            except Exception as e:
                print(f"   ❌ 错误: {str(e)}")
            
            print("-" * 40)
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保已正确安装依赖和配置系统")

def demo_with_mock_config():
    """使用模拟配置演示系统功能"""
    print("=" * 60)
    print("SpeakerValidationPreCheckSystem - 模拟演示")
    print("讲者身份验证系统 v2.1.0")
    print("=" * 60)
    
    # 模拟验证逻辑
    def mock_extract_doctor_info(text: str) -> dict:
        """模拟医生信息提取"""
        info = {'name': '', 'hospital': '', 'department': '', 'title': ''}
        
        # 简单的关键词匹配
        if '鲍娜' in text:
            info['name'] = '鲍娜'
        elif '张三' in text:
            info['name'] = '张三'
        elif '钟南山' in text:
            info['name'] = '钟南山'
        
        if '医院' in text:
            if '长海医院' in text:
                info['hospital'] = '长海医院'
            elif '广州医科大学' in text:
                info['hospital'] = '广州医科大学附属第一医院'
        
        if '科' in text:
            if '心内科' in text:
                info['department'] = '心内科'
            elif '呼吸内科' in text:
                info['department'] = '呼吸内科'
        
        return info
    
    def mock_exa_search(doctor_name: str) -> dict:
        """模拟EXA搜索"""
        # 知名医生返回高分，其他返回低分
        if doctor_name in ['钟南山', '张文宏', '李兰娟']:
            return {"success": True, "match_score": 8, "verification_passed": True}
        else:
            return {"success": True, "match_score": 3, "verification_passed": False}
    
    def mock_check_s3_folder(folder_name: str) -> dict:
        """模拟S3文件夹检查"""
        # 模拟不同文件夹的文档数量
        folder_docs = {
            "tinabao/": 4,
            "张三-长海医院-心内科/": 5,
            "钟南山-广州医科大学附属第一医院-呼吸内科/": 0,
            "default": 0
        }
        
        doc_count = folder_docs.get(folder_name, folder_docs["default"])
        return {"success": True, "file_count": doc_count}
    
    # 测试用例
    test_cases = [
        "我请到了鲍娜医生，目前就职长海医院demo科室",
        "我请到了张三医生，目前就职长海医院心内科，职称为主任医师",
        "钟南山 广州医科大学附属第一医院 呼吸内科 院士",
        "我请到了医生，目前就职长海医院"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{i}. 测试输入: {test_input}")
        
        # 提取医生信息
        doctor_info = mock_extract_doctor_info(test_input)
        print(f"   提取信息: {doctor_info}")
        
        # 判断验证方法
        if '鲍娜' in test_input:
            print("   验证方法: direct_pass (内部验证)")
            folder_name = "tinabao/"
            identity_verified = True
        elif doctor_info['name']:
            print(f"   验证方法: exa_search (网络搜索)")
            exa_result = mock_exa_search(doctor_info['name'])
            print(f"   EXA搜索: 匹配分数 {exa_result['match_score']}/10")
            identity_verified = exa_result['verification_passed']
            folder_name = f"{doctor_info['name']}-{doctor_info['hospital']}-{doctor_info['department']}/"
        else:
            print("   验证方法: 无法提取医生姓名")
            identity_verified = False
            folder_name = "unknown/"
        
        # 检查文档
        if identity_verified or doctor_info['name']:
            s3_result = mock_check_s3_folder(folder_name)
            print(f"   检查文件夹: {folder_name}")
            print(f"   文档数量: {s3_result['file_count']}")
            
            # 最终判断
            if identity_verified and s3_result['file_count'] > 3:
                print("   最终结果: ✅ 预审通过")
            elif identity_verified and s3_result['file_count'] <= 3:
                print("   最终结果: ❌ 身份验证通过但文档不足")
            elif not identity_verified and s3_result['file_count'] > 3:
                print("   最终结果: ⚠️ 身份验证失败但文档充足")
            else:
                print("   最终结果: ❌ 身份验证失败且文档不足")
        else:
            print("   最终结果: ❌ 无法验证身份")
        
        print("-" * 50)

def main():
    """主函数"""
    print("🚀 SpeakerValidationPreCheckSystem 使用示例")
    print()
    
    # 检查是否有真实配置
    if os.path.exists('.config'):
        print("📋 发现配置文件，使用真实系统演示...")
        demo_with_real_system()
    else:
        print("📋 未发现配置文件，使用模拟演示...")
        demo_with_mock_config()
    
    print("\n✨ 演示完成！")
    print("\n💡 使用提示:")
    print("1. 复制 .config.example 为 .config 并填入真实配置")
    print("2. 设置 EXA_API_KEY 以启用网络搜索功能")
    print("3. 上传测试文档到 S3 对应文件夹")
    print("4. 运行 python test_exa_integration.py 进行完整测试")

if __name__ == "__main__":
    main()
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
