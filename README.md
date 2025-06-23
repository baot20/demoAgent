# SpeakerValidationPreCheckSystem - 医药代表内容预审系统

这个系统专门用于对医药代表提交的演讲内容、培训材料和推广资料进行初步审核。系统会检查内容的合规性（是否包含必要的审核标识）和支撑文档的完整性（S3存储桶中的文件数量），并提供详细的改进建议。

## 🚀 功能特性

- **内容合规检查**: 自动检测内容是否包含必要的审核标识（如"鲍娜"）
- **文档完整性验证**: 检查S3存储桶中支撑文档的数量是否满足要求
- **多种运行模式**: 支持独立运行、MCP Server模式、Supervisor Agent集成
- **智能分析**: 使用Strands Agent框架进行内容分析和判断
- **完整日志系统**: 集成CloudWatch日志监控和审计（可选）
- **优雅降级**: 当可选依赖不可用时自动降级为基础功能
- **详细反馈**: 为医药代表提供具体的改进建议

## 📦 安装依赖

### 基础依赖
```bash
pip install -r requirements.txt
```

### 可选依赖（CloudWatch日志支持）
系统支持可选的CloudWatch日志功能。如果未安装相关依赖，系统会自动降级为控制台日志：

```bash
# 安装CloudWatch日志支持（可选）
pip install watchtower

# 或运行自动安装脚本
python install_optional_deps.py
```

## ⚙️ 配置

### 1. AWS凭证配置
确保你已经配置了AWS凭证，可以通过以下方式之一：

```bash
# 使用AWS CLI配置
aws configure

# 或者设置环境变量
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### 2. 系统配置文件
复制配置模板并编辑配置文件：

```bash
# 复制配置模板
cp .config.example .config

# 编辑配置文件，填入你的实际信息
nano .config
```

配置文件`.config`包含以下部分：

```ini
[AWS]
ACCESS_KEY_ID = your_access_key_id_here
SECRET_ACCESS_KEY = your_secret_access_key_here
REGION = us-east-1

[S3]
BUCKET_NAME = your-bucket-name

[PREAUDIT]
TARGET_WORD = 鲍娜
MIN_FILE_COUNT = 3

[CLOUDWATCH]
LOG_GROUP_NAME = /aws/speakervalidation/precheck
LOG_STREAM_NAME = speaker-validation-logs
```

## 🎯 使用方法

### 方式一：基本使用（Strands Agent模式）
```bash
python agent.py
```

### 方式二：MCP Server模式（推荐用于Chatbot UI集成）

#### 启动MCP Server
```bash
# 启动MCP Server
python start_mcp_server.py

# 或直接启动
python mcp_server.py
```

#### 集成到Chatbot UI

**如果使用虚拟环境（推荐）**，将以下配置添加到你的chatbot UI的MCP配置中：

```json
{
  "mcpServers": {
    "speaker-validation-precheck": {
      "command": "python",
      "args": ["/Users/tinabao/Documents/code/demoAgent/mcp_launcher.py"],
      "cwd": "/Users/tinabao/Documents/code/demoAgent",
      "env": {
        "PYTHONPATH": "/Users/tinabao/Documents/code/demoAgent"
      }
    }
  }
}
```

**如果使用系统Python**，使用以下配置：

```json
{
  "mcpServers": {
    "speaker-validation-precheck": {
      "command": "python",
      "args": ["/Users/tinabao/Documents/code/demoAgent/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/Users/tinabao/Documents/code/demoAgent"
      }
    }
  }
}
```

#### MCP配置步骤详解

1. **测试MCP Server**
```bash
# 测试工具函数
python test_mcp_server.py

# 测试CloudWatch日志
python test_cloudwatch_logs.py

# 测试MCP server启动
python mcp_server.py
```

2. **配置Chatbot UI**

**方法一：使用配置文件**
将`mcp_config.json`的内容添加到你的chatbot UI配置中。

**方法二：直接配置**
在你的chatbot UI设置中添加MCP server：
- **Server Name**: `speaker-validation-precheck`
- **Command**: `python`
- **Args**: `["/Users/tinabao/Documents/code/demoAgent/mcp_server.py"]`
- **Working Directory**: `/Users/tinabao/Documents/code/demoAgent`

### 方式三：在代码中使用
```python
from agent import SpeakerValidationPreCheckSystem

# 创建Agent实例
agent = SpeakerValidationPreCheckSystem(region_name="us-east-1")

# 分析文件
result = agent.process_s3_file("your-bucket", "path/to/file.txt")

print(result['final_output'])  # 输出: 合格 或 不合格 + 原因
```

## 🛠️ 可用工具（MCP模式）

### 1. get_current_config
获取系统当前配置和审核标准

**参数**: 无
**返回**: JSON格式的配置信息

### 2. check_string_content
检查内容是否包含合规标识

**参数**:
- `input_string` (必需): 要检查的内容
- `target_word` (可选): 合规标识，默认使用配置中的值

**返回**: 检查结果的JSON对象

### 3. list_s3_files
检查支撑文档完整性

**参数**:
- `bucket_name` (可选): S3存储桶名称，默认使用配置中的值

**返回**: 文档列表和统计信息

### 4. perform_preaudit（推荐）
执行完整的预审流程

**参数**:
- `user_input` (必需): 医药代表提交的内容
- `bucket_name` (可选): S3存储桶名称

**返回**: 详细的预审结果和改进建议

## 📋 使用示例

### MCP模式使用示例
在chatbot UI中，你可以这样使用：

```
请帮我预审这段医药代表的演讲内容："各位医生，今天我要介绍新产品，已经过鲍娜审核"
```

系统会自动调用`perform_preaudit`工具进行完整的预审检查。

### 输出示例
```json
{
  "bucket_name": "my-test-bucket",
  "object_key": "documents/test.txt",
  "file_size": 1234,
  "analysis_status": "success",
  "final_output": "不合格 - 内容格式不规范，缺少必要的标题结构",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🔐 权限要求

确保你的AWS用户/角色具有以下权限：

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams"
            ],
            "Resource": "arn:aws:logs:*:*:log-group:/aws/speakervalidation/*"
        }
    ]
}
```

## 📊 CloudWatch日志集成

### 功能特性
- **自动日志组管理**: 自动检测和创建CloudWatch日志组
- **详细事件记录**: 记录预审结果、S3访问、MCP工具调用等
- **双重日志输出**: CloudWatch Logs + 控制台输出
- **可选功能设计**: 如果watchtower未安装，自动降级为控制台日志

### 启用CloudWatch日志
```bash
# 安装可选依赖
pip install watchtower

# 或使用安装脚本
python install_optional_deps.py

# 测试日志功能
python test_cloudwatch_logs.py
```

### 查看日志
在AWS CloudWatch控制台中查看日志：
- **日志组**: `/aws/speakervalidation/precheck`（或配置中指定的名称）
- **日志流**: `speaker-validation-logs`（或配置中指定的名称）

## 🔧 故障排除

### 常见问题及解决方案

1. **AWS凭证错误**
   - 检查AWS CLI配置或环境变量
   - 验证`.config`文件中的凭证信息

2. **S3访问被拒绝**
   - 检查IAM权限和存储桶策略
   - 确认存储桶名称正确

3. **CloudWatch日志失败**
   - 检查CloudWatch Logs权限和网络连接
   - 运行`python test_cloudwatch_logs.py`测试

4. **MCP Server启动失败**
   ```bash
   # 检查依赖
   pip install -r requirements.txt
   
   # 检查Python路径
   which python
   
   # 测试独立工具
   python test_mcp_server.py
   ```

5. **文件不存在**
   - 检查存储桶名称和文件路径是否正确
   - 验证AWS凭证的S3访问权限

### 配置验证
```bash
# 验证配置
python test_config.py

# 调试配置问题
python debug_config.py
```

### watchtower未安装警告
```
警告: watchtower模块未安装，CloudWatch日志功能将被禁用
要启用CloudWatch日志，请运行: pip install watchtower
```
**解决方案**: 运行`pip install watchtower`或`python install_optional_deps.py`

## 🎨 自定义配置

### 自定义分析逻辑
你可以修改`analyze_content_with_bedrock`方法中的提示词来自定义分析逻辑：

```python
prompt = f"""
自定义你的分析提示词...
内容: {content}
请根据特定标准判断是否合格...
"""
```

### 自定义审核标准
编辑`.config`文件中的`[PREAUDIT]`部分：

```ini
[PREAUDIT]
TARGET_WORD = 你的审核标识
MIN_FILE_COUNT = 最低文档数量
```

### 多环境支持
可以创建不同的配置文件（如`.config.dev`, `.config.prod`）并在启动时指定。

## 🔒 安全注意事项

1. **配置文件安全**: `.config`文件包含AWS凭证，不要提交到版本控制
2. **网络访问**: MCP server通过stdio通信，相对安全
3. **权限控制**: 确保AWS凭证只有必要的最小权限
4. **日志安全**: CloudWatch日志可能包含敏感信息，注意访问控制

## 🌟 支持的集成方式

### Chatbot UI支持
理论上支持所有实现了MCP协议的chatbot UI，包括但不限于：
- Claude Desktop
- 自定义的MCP客户端
- 其他支持MCP的AI应用

### Supervisor Agent集成
系统可以作为工具被Supervisor Agent调用，详细信息请参考项目中的`supervisor_example.py`文件。

## 📈 监控和审计

系统记录以下关键事件：
- 系统启动和停止
- 预审请求和结果
- S3访问成功/失败
- MCP工具调用性能
- 配置加载和验证
- 错误和异常

这些日志可用于：
- 性能监控和优化
- 合规审计和追踪
- 故障诊断和排除
- 使用统计和分析

## 🔄 更新和维护

当需要更新系统时：
1. 更新代码文件
2. 重启chatbot UI以重新加载MCP server
3. 测试功能是否正常
4. 检查日志确认系统状态

## 📞 技术支持

如果遇到问题，请按以下顺序检查：
1. 配置文件是否正确（运行`python debug_config.py`）
2. AWS权限是否充足
3. 依赖是否完整安装（运行`pip install -r requirements.txt`）
4. 路径是否正确设置
5. 网络连接是否正常

## 📁 项目文件结构

```
demoAgent/
├── README.md                       # 本文档
├── agent.py                        # 主Agent实现
├── mcp_server.py                   # MCP server主文件
├── speaker_validation_tools.py     # 独立工具函数
├── config_reader.py               # 配置读取模块
├── cloudwatch_logger.py           # CloudWatch日志模块
├── mcp_config.json                # MCP配置文件
├── .config.example                # 配置文件模板
├── .config                        # 实际配置文件（需要创建）
├── requirements.txt               # 依赖列表
├── install_optional_deps.py       # 可选依赖安装脚本
├── test_mcp_server.py             # MCP server测试脚本
├── test_cloudwatch_logs.py        # CloudWatch日志测试脚本
├── debug_config.py                # 配置调试脚本
└── start_mcp_server.py            # MCP server启动脚本
```

---

**版本**: 1.0.0  
**最后更新**: 2024-06-22  
**维护者**: 医药代表内容预审系统开发团队
