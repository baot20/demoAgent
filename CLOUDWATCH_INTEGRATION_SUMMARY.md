# CloudWatch 日志集成总结

## 完成的修改

### ✅ 配置文件更新
- `.config.example` 和 `.config` 添加了 `[CLOUDWATCH]` 配置段
- 支持自定义日志组名称和日志流名称

### ✅ 新增文件
1. **cloudwatch_logger.py** - CloudWatch 日志处理模块
   - 支持可选的 CloudWatch 日志功能
   - 自动降级为控制台日志（如果 watchtower 未安装）
   - 自动创建日志组和日志流

2. **install_optional_deps.py** - 可选依赖安装脚本
   - 自动检测和安装 watchtower
   - 功能测试和验证

3. **debug_config.py** - 配置调试脚本
   - 详细的配置验证和问题诊断

4. **test_cloudwatch_logs.py** - CloudWatch 日志测试脚本

### ✅ 代码修改
1. **config_reader.py**
   - 添加了 `get_cloudwatch_config()` 方法
   - 修复了缺失的 `get_preaudit_config()` 方法

2. **speaker_validation_tools.py**
   - 集成了详细的 CloudWatch 日志记录
   - 记录执行时间、成功/失败状态
   - 支持事件级别的日志记录

3. **mcp_server.py**
   - 添加了 MCP 工具调用的详细日志
   - 性能监控和错误追踪

4. **requirements.txt**
   - 添加了 `watchtower>=3.0.0` 依赖

## 配置示例

```ini
[CLOUDWATCH]
LOG_GROUP_NAME = /aws/speakervalidation/precheck
LOG_STREAM_NAME = speaker-validation-logs
```

## 日志功能特性

### 1. 自动日志组管理
- 自动检测和创建 CloudWatch 日志组
- 配置化的日志组和日志流名称
- 优雅的错误处理

### 2. 详细的事件记录
- **预审事件**: 记录预审结果、文件数量、合规状态
- **S3 访问事件**: 记录访问成功/失败、文件数量、错误信息
- **MCP 工具调用**: 记录工具名称、执行时间、成功/失败状态

### 3. 双重日志输出
- **CloudWatch Logs**: 用于生产环境监控和审计
- **控制台输出**: 用于本地开发和调试

### 4. 可选功能设计
- 如果 `watchtower` 未安装，自动降级为控制台日志
- 不影响核心功能的正常运行
- 友好的警告提示

## 使用方法

### 1. 基本使用（无 CloudWatch）
```bash
# 直接运行，会使用控制台日志
python mcp_server.py
```

### 2. 启用 CloudWatch 日志
```bash
# 安装可选依赖
pip install watchtower

# 或使用安装脚本
python install_optional_deps.py

# 运行系统
python mcp_server.py
```

### 3. 测试 CloudWatch 功能
```bash
# 测试日志功能
python test_cloudwatch_logs.py

# 调试配置问题
python debug_config.py
```

## AWS 权限要求

确保 AWS 凭证具有以下 CloudWatch Logs 权限：

```json
{
    "Version": "2012-10-17",
    "Statement": [
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

## 日志查看

在 AWS CloudWatch 控制台中查看日志：
- **日志组**: `/aws/speakervalidation/precheck`（或配置中指定的名称）
- **日志流**: `speaker-validation-logs`（或配置中指定的名称）

## 故障排除

### 1. watchtower 未安装
```
警告: watchtower 模块未安装，CloudWatch 日志功能将被禁用
要启用 CloudWatch 日志，请运行: pip install watchtower
```
**解决方案**: 运行 `pip install watchtower` 或 `python install_optional_deps.py`

### 2. AWS 权限不足
**症状**: CloudWatch 日志处理器设置失败
**解决方案**: 检查 AWS 凭证的 CloudWatch Logs 权限

### 3. 配置验证失败
**解决方案**: 运行 `python debug_config.py` 查看详细的配置问题

## 监控和审计

系统现在记录以下关键事件：

1. **系统启动和停止**
2. **预审请求和结果**
3. **S3 访问成功/失败**
4. **MCP 工具调用性能**
5. **配置加载和验证**
6. **错误和异常**

这些日志可用于：
- 性能监控和优化
- 合规审计和追踪
- 故障诊断和排除
- 使用统计和分析

## 成功验证

✅ 配置验证通过
✅ 核心功能正常工作
✅ MCP Server 可以启动
✅ CloudWatch 日志功能可选启用
✅ 优雅的错误处理和降级
✅ 详细的事件记录和监控
