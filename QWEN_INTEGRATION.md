# 通义千问集成说明

本项目已完全替换Snowflake Cortex功能为阿里云通义千问，以支持中国大陆用户使用。

## 配置步骤

### 1. 获取通义千问API密钥

1. 访问 [阿里云DashScope控制台](https://dashscope.console.aliyun.com/)
2. 登录或注册阿里云账号
3. 开通通义千问服务
4. 获取API Key

### 2. 配置环境变量

将 `env_qwen_example.txt` 重命名为 `.env`，并填入真实配置：

```bash
# 通义千问API密钥
DASHSCOPE_API_KEY=sk-xxxxxxxxxx

# Snowflake连接配置
SNOWFLAKE_ROLE=ACCOUNTADMIN
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_USER=your_username
SNOWFLAKE_ACCOUNT_LOCATOR=XGFXMUS-WR98488
SNOWFLAKE_HOST=xgfxmus-wr98488.snowflakecomputing.cn
SNOWFLAKE_AUTHENTICATOR=externalbrowser
```

### 3. 启动应用

```bash
conda activate sf_env
python -m streamlit run app.py
```

## 功能替换说明

### 已替换的功能

1. **自动描述生成**: 使用通义千问生成表和字段的业务描述
2. **聊天功能**: 使用通义千问进行数据分析对话
3. **模型验证**: 使用通义千问验证语义模型的正确性
4. **LLM评判**: 在评估模块中使用通义千问进行结果评判

### 模型映射

- `llama3-8b` → `qwen-turbo`
- `mistral-large2` → `qwen-plus`
- `mixtral-8x7b` → `qwen-turbo`
- `llama2-70b-chat` → `qwen-plus`

### 接口兼容性

- 保持与原有Cortex API相同的接口和返回格式
- 原有的函数调用方式无需修改
- 备份了原有的Cortex调用函数供紧急回退使用

## 注意事项

1. **API额度**: 通义千问API按调用量计费，请注意控制使用量
2. **网络连接**: 确保网络可以访问阿里云服务
3. **中文支持**: 默认使用中文进行对话和描述生成
4. **错误处理**: 如果通义千问API调用失败，会显示详细错误信息

## 故障排除

### 常见错误

1. **API密钥错误**: 检查 `DASHSCOPE_API_KEY` 是否正确设置
2. **网络连接失败**: 确认网络可以访问 `dashscope.aliyuncs.com`
3. **额度不足**: 检查阿里云账户余额和API调用次数

### 性能优化

1. 使用缓存减少重复API调用
2. 合理选择模型（turbo用于简单任务，plus用于复杂任务）
3. 控制提示词长度以降低费用

## 备用方案

如果需要回退到原有Cortex功能：

1. 在相关文件中将函数调用从 `qwen_xxx` 改回 `cortex_xxx`
2. 恢复原有的环境变量配置
3. 重新启动应用

原有的Cortex函数已保留，命名为 `xxx_cortex` 格式。
