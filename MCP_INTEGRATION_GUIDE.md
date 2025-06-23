# SpeakerValidationPreCheckSystem MCP 集成指南

## 概述

SpeakerValidationPreCheckSystem 现在支持作为 MCP (Model Context Protocol) server 运行，可以集成到任何支持 MCP 的 chatbot UI 中。

## 文件结构

```
demoAgent/
├── mcp_server.py                    # MCP server 主文件
├── speaker_validation_tools.py     # 独立工具函数
├── mcp_config.json                 # MCP 配置文件
├── test_mcp_server.py              # MCP server 测试脚本
├── agent.py                        # 原始 Strands Agent 实现
├── config_reader.py               # 配置读取模块
└── .config                        # 配置文件
```

## 安装依赖

```bash
pip install -r requirements.txt
```

确保安装了以下依赖：
- `mcp>=1.0.0` - MCP 协议支持
- `boto3>=1.34.0` - AWS S3 访问
- `watchtower>=3.0.0` - CloudWatch 日志支持
- 其他现有依赖

## 配置步骤

### 1. 配置系统
```bash
# 复制配置模板
cp .config.example .config

# 编辑配置文件，填入你的 AWS 信息
nano .config
```

### 2. 测试 MCP Server
```bash
# 测试工具函数
python test_mcp_server.py

# 测试 CloudWatch 日志
python test_cloudwatch_logs.py

# 测试 MCP server 启动
python mcp_server.py
```

### 3. 集成到 Chatbot UI

#### 方法一：使用配置文件
将 `mcp_config.json` 的内容添加到你的 chatbot UI 配置中：

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

#### 方法二：直接配置
在你的 chatbot UI 设置中添加 MCP server：

- **Server Name**: `speaker-validation-precheck`
- **Command**: `python`
- **Args**: `["/Users/tinabao/Documents/code/demoAgent/mcp_server.py"]`
- **Working Directory**: `/Users/tinabao/Documents/code/demoAgent`

## 可用工具

### 1. get_current_config
获取系统当前配置和审核标准

**参数**: 无

**返回**: JSON 格式的配置信息

### 2. check_string_content
检查内容是否包含合规标识

**参数**:
- `input_string` (必需): 要检查的内容
- `target_word` (可选): 合规标识，默认使用配置中的值

**返回**: 检查结果的 JSON 对象

### 3. list_s3_files
检查支撑文档完整性

**参数**:
- `bucket_name` (可选): S3 存储桶名称，默认使用配置中的值

**返回**: 文档列表和统计信息

### 4. perform_preaudit (推荐)
执行完整的预审流程

**参数**:
- `user_input` (必需): 医药代表提交的内容
- `bucket_name` (可选): S3 存储桶名称

**返回**: 详细的预审结果和改进建议

## 使用示例

在 chatbot UI 中，你可以这样使用：

```
请帮我预审这段医药代表的演讲内容："各位医生，今天我要介绍新产品，已经过鲍娜审核"
```

系统会自动调用 `perform_preaudit` 工具进行完整的预审检查。

## 故障排除

### 1. 配置问题
```bash
# 验证配置
python test_config.py
```

### 2. AWS 权限问题
确保 AWS 凭证有以下权限：
- S3 读取权限
- 对指定存储桶的访问权限
- CloudWatch Logs 权限（创建日志组、日志流、写入日志）

### 3. MCP Server 启动失败
```bash
# 检查依赖
pip install -r requirements.txt

# 检查 Python 路径
which python

# 测试独立工具
python test_mcp_server.py
```

### 4. 路径问题
确保 `mcp_config.json` 中的路径是绝对路径，并且指向正确的文件位置。

## 高级配置

### 自定义审核标准
编辑 `.config` 文件中的 `[PREAUDIT]` 部分：

```ini
[PREAUDIT]
TARGET_WORD = 你的审核标识
MIN_FILE_COUNT = 最低文档数量
```

### 多环境支持
可以创建不同的配置文件（如 `.config.dev`, `.config.prod`）并在启动时指定。

## 安全注意事项

1. **配置文件安全**: `.config` 文件包含 AWS 凭证，不要提交到版本控制
2. **网络访问**: MCP server 通过 stdio 通信，相对安全
3. **权限控制**: 确保 AWS 凭证只有必要的最小权限

## 支持的 Chatbot UI

理论上支持所有实现了 MCP 协议的 chatbot UI，包括但不限于：
- Claude Desktop
- 自定义的 MCP 客户端
- 其他支持 MCP 的 AI 应用

## 更新和维护

当需要更新系统时：
1. 更新代码文件
2. 重启 chatbot UI 以重新加载 MCP server
3. 测试功能是否正常

## 联系支持

如果遇到问题，请检查：
1. 配置文件是否正确
2. AWS 权限是否充足
3. 依赖是否完整安装
4. 路径是否正确设置
