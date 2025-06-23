# Supervisor Agent 集成指南

本文档说明如何让 Supervisor Agent 更好地理解和使用 S3 预审 Agent。

## 🤖 Agent 基本信息

### Agent 标识
- **名称**: S3PreauditAgent
- **版本**: 1.0.0
- **类型**: preaudit_system
- **分类**: content_validation

### 核心功能描述
```
S3文件预审系统Agent - 专门用于检查用户输入内容和S3存储桶文件数量的预审判断系统。

主要功能：
1. 检查用户输入字符串是否包含指定关键词（默认：鲍娜）
2. 检查指定S3存储桶中的文件数量是否满足最小要求（默认：>3个）
3. 综合判断预审结果：只有当用户输入包含关键词且文件数量满足要求时才通过预审

适用场景：
- 内容合规性检查
- 文件数量验证
- 自动化预审流程
- 条件性审批系统
```

## 🛠️ 可用工具详解

### 1. list_s3_files
**用途**: 获取S3存储桶文件列表和数量统计
```python
# 调用方式
list_s3_files(bucket_name="my-bucket")  # 指定存储桶
list_s3_files()  # 使用默认配置的存储桶

# 返回格式
{
    "success": True,
    "file_count": 5,
    "files": ["file1.txt", "file2.txt", ...],
    "bucket_name": "my-bucket"
}
```

### 2. check_string_content
**用途**: 检查文本内容是否包含目标关键词
```python
# 调用方式
check_string_content("你好鲍娜，今天天气不错")  # 使用默认关键词
check_string_content("测试内容", "自定义关键词")  # 自定义关键词

# 返回格式
{
    "input_string": "你好鲍娜，今天天气不错",
    "target_word": "鲍娜",
    "contains_target": True,
    "string_length": 12
}
```

### 3. perform_preaudit
**用途**: 执行完整的预审流程和判断
```python
# 调用方式
perform_preaudit("你好鲍娜，今天天气不错")  # 使用默认配置
perform_preaudit("测试内容", "custom-bucket")  # 指定存储桶

# 返回格式
"预审通过 - 用户输入包含'鲍娜'且 S3 存储桶 'my-bucket' 中有 5 个文件（超过3个）"
# 或
"预审不通过 - 用户输入不包含'鲍娜'"
```

### 4. get_current_config
**用途**: 获取当前系统配置信息
```python
# 调用方式
get_current_config()

# 返回格式
{
    "aws_region": "us-east-1",
    "s3_bucket": "my-bucket",
    "target_word": "鲍娜",
    "min_file_count": 3
}
```

## 📋 Supervisor Agent 调用指南

### 基本调用模式

#### 1. 简单预审检查
```python
message = '请对用户输入"你好鲍娜，今天天气不错"进行预审检查'
response = preaudit_agent(message)
```

#### 2. 详细预审检查
```python
message = """
请对用户输入进行详细的预审检查："你好鲍娜，今天天气不错"

请执行以下步骤：
1. 使用 get_current_config 工具获取当前配置信息
2. 使用 check_string_content 工具检查用户输入是否包含目标词汇
3. 使用 list_s3_files 工具检查 S3 存储桶中的文件数量
4. 使用 perform_preaudit 工具执行完整的预审流程
5. 根据预审结果给出明确的"预审通过"或"预审不通过"的结论

请详细说明检查过程和结果。
"""
response = preaudit_agent(message)
```

#### 3. 自定义参数检查
```python
message = """
请使用存储桶"custom-bucket"对用户输入"测试内容"进行预审检查，
并检查是否包含关键词"自定义词汇"。
"""
response = preaudit_agent(message)
```

### 结果解释指南

#### 成功响应模式
- 包含 "预审通过" 关键词
- 详细说明通过的原因
- 包含具体的检查数据（文件数量、关键词等）

#### 失败响应模式
- 包含 "预审不通过" 关键词
- 明确说明不通过的具体原因
- 可能的原因：
  - "用户输入不包含'关键词'"
  - "S3存储桶中只有X个文件（需要超过Y个）"
  - "S3存储桶访问失败"

#### 错误响应模式
- 包含错误信息和建议
- 常见错误：
  - AWS凭证问题
  - 网络连接问题
  - 配置文件问题

## 🎯 使用场景示例

### 场景1: 内容发布预审
```python
# Supervisor Agent 可以这样调用
def content_publish_preaudit(content):
    message = f"""
    这是一个内容发布预审请求。
    请检查以下内容是否符合发布要求："{content}"
    
    需要验证：
    1. 内容是否包含必要的审核标识
    2. 支撑文件数量是否足够
    
    请给出详细的预审结果和建议。
    """
    return preaudit_agent(message)
```

### 场景2: 批量预审检查
```python
def batch_preaudit(content_list):
    results = []
    for content in content_list:
        message = f'请对内容"{content}"进行快速预审检查'
        result = preaudit_agent(message)
        results.append({
            'content': content,
            'result': result,
            'passed': '预审通过' in result
        })
    return results
```

### 场景3: 条件性审批
```python
def conditional_approval(user_request):
    message = f"""
    这是一个审批请求的预审检查。
    用户请求："{user_request}"
    
    请检查是否满足自动审批的条件：
    1. 请求内容包含必要的标识
    2. 相关文件数量满足要求
    
    如果满足条件，可以进入自动审批流程。
    如果不满足，需要人工审核。
    """
    return preaudit_agent(message)
```

## ⚙️ 配置和定制

### 可配置参数
- `TARGET_WORD`: 预审检查的目标关键词（默认："鲍娜"）
- `MIN_FILE_COUNT`: S3文件数量最小要求（默认：3）
- `AWS_REGION`: AWS服务区域（默认："us-east-1"）
- `S3_BUCKET_NAME`: 默认S3存储桶名称

### 运行时配置查询
```python
# Supervisor Agent 可以查询当前配置
message = "请告诉我当前的预审配置参数"
config_info = preaudit_agent(message)
```

## 🔍 监控和调试

### 性能指标
- **典型响应时间**: 2-5秒
- **影响因素**: S3存储桶大小、网络延迟、AWS API响应时间

### 日志级别
- **INFO**: 正常操作和结果
- **WARNING**: 配置问题和性能警告  
- **ERROR**: AWS连接错误和系统故障

### 健康检查
```python
# Supervisor Agent 可以执行健康检查
health_check_message = """
请执行系统健康检查：
1. 检查当前配置是否正常
2. 测试S3连接是否正常
3. 验证预审功能是否工作正常
"""
health_status = preaudit_agent(health_check_message)
```

## 🚨 错误处理

### 常见错误及解决方案

1. **AWS凭证无效**
   - 错误信息: "AWS凭证无效" 或 "访问被拒绝"
   - 解决方案: 检查.config文件中的AWS凭证配置

2. **S3存储桶不存在**
   - 错误信息: "存储桶不存在" 或 "NoSuchBucket"
   - 解决方案: 验证存储桶名称和访问权限

3. **网络连接问题**
   - 错误信息: "连接超时" 或 "网络错误"
   - 解决方案: 检查网络连接和AWS服务状态

### Supervisor Agent 错误处理示例
```python
def safe_preaudit_call(content):
    try:
        message = f'请对内容"{content}"进行预审检查'
        result = preaudit_agent(message)
        
        if "预审通过" in result:
            return {"status": "passed", "message": result}
        elif "预审不通过" in result:
            return {"status": "failed", "message": result}
        else:
            return {"status": "error", "message": result}
            
    except Exception as e:
        return {"status": "error", "message": f"预审系统调用失败: {str(e)}"}
```

## 📚 完整集成示例

参考 `supervisor_example.py` 文件，其中包含了完整的 Supervisor Agent 集成示例，展示了如何：

1. 创建 Supervisor Agent
2. 定义调用预审 Agent 的工具
3. 处理各种预审场景
4. 解释和转换预审结果
5. 提供用户友好的交互界面

通过这些信息，Supervisor Agent 可以更好地理解和使用 S3 预审 Agent，提供更智能的预审服务！
