# SpeakerValidationPreCheckSystem - 医药代表内容预审系统

这个系统专门用于对医药代表提交的演讲内容、培训材料和推广资料进行初步审核。系统会检查内容的合规性（是否包含必要的审核标识）和支撑文档的完整性（S3存储桶中的文件数量），并提供详细的改进建议。

## 功能特性

- 从 S3 读取支撑文档信息
- 使用 Strands Agent 框架进行内容分析
- 自动判断内容合规性并输出结果
- 完整的错误处理和日志记录
- 为医药代表提供具体的改进建议
- 集成 CloudWatch 日志监控和审计

## 安装依赖

```bash
pip install -r requirements.txt
```

### 可选依赖

系统支持可选的 CloudWatch 日志功能。如果未安装相关依赖，系统会自动降级为控制台日志：

```bash
# 安装 CloudWatch 日志支持（可选）
pip install watchtower

# 或运行自动安装脚本
python install_optional_deps.py
```

## 配置

### 1. AWS 凭证配置

确保你已经配置了 AWS 凭证，可以通过以下方式之一：

```bash
# 使用 AWS CLI 配置
aws configure

# 或者设置环境变量
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### 2. 修改配置文件

复制配置模板并编辑配置文件：

```bash
# 复制配置模板
cp .config.example .config

# 编辑配置文件，填入你的实际信息
nano .config
```

配置文件 `.config` 包含以下部分：

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

## 使用方法

### 基本使用（Strands Agent 模式）

```bash
python agent.py
```

### MCP Server 模式（推荐用于 Chatbot UI 集成）

```bash
# 启动 MCP Server
python start_mcp_server.py

# 或直接启动
python mcp_server.py
```

### 集成到 Chatbot UI

将以下配置添加到你的 chatbot UI 的 MCP 配置中：

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

详细的 MCP 集成指南请参考 [MCP_INTEGRATION_GUIDE.md](MCP_INTEGRATION_GUIDE.md)

### 在代码中使用

```python
from agent import SpeakerValidationPreCheckSystem

# 创建 Agent 实例
agent = SpeakerValidationPreCheckSystem(region_name="us-east-1")

# 分析文件
result = agent.process_s3_file("your-bucket", "path/to/file.txt")

print(result['final_output'])  # 输出: 合格 或 不合格 + 原因
```

## 输出示例

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

## 权限要求

确保你的 AWS 用户/角色具有以下权限：

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

## 故障排除

1. **AWS 凭证错误**: 检查 AWS CLI 配置或环境变量
2. **S3 访问被拒绝**: 检查 IAM 权限和存储桶策略
3. **CloudWatch 日志失败**: 检查 CloudWatch Logs 权限和网络连接
4. **文件不存在**: 检查存储桶名称和文件路径是否正确

### 测试 CloudWatch 日志

```bash
# 测试 CloudWatch 日志功能
python test_cloudwatch_logs.py
```

### 查看日志

在 AWS CloudWatch 控制台中查看日志：
- 日志组: `/aws/speakervalidation/precheck`
- 日志流: `speaker-validation-logs`

## 自定义分析逻辑

你可以修改 `analyze_content_with_bedrock` 方法中的提示词来自定义分析逻辑：

```python
prompt = f"""
自定义你的分析提示词...
内容: {content}
请根据特定标准判断是否合格...
"""
```
