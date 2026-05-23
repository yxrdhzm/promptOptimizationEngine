# 部署文档 / Deployment Guide

[English](#english) · [中文](#chinese)

---

<a id="english"></a>

## English

### Local Development

```bash
git clone https://github.com/yxrdhzm/promptOptimizationEngine.git
cd promptOptimizationEngine
pip install -e .
cp .env.example .env
# Edit .env with your API keys
streamlit run src/ui/app.py
```

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-xxx` |
| `ANTHROPIC_API_KEY` | Anthropic API key | `sk-ant-xxx` |
| `DASHSCOPE_API_KEY` | Alibaba DashScope key | `sk-xxx` |
| `DEEPSEEK_API_KEY` | DeepSeek API key | `sk-xxx` |
| `PO_MODELS__EXECUTOR` | Executor model | `openai/gpt-4o-mini` |
| `PO_MODELS__OPTIMIZER` | Optimizer model | `openai/gpt-4o` |
| `PO_MODELS__JUDGE` | Judge model | `openai/gpt-4o-mini` |
| `PO_OPTIMIZER__MAX_ITERATIONS` | Max rounds | `5` |
| `PO_OPTIMIZER__NUM_CANDIDATES` | Candidates per round | `3` |
| `PO_EVALUATION__MAX_CONCURRENCY` | Concurrent API calls | `10` |

### Docker (Coming Soon)

```bash
docker build -t prompt-optimizer .
docker run -p 8501:8501 --env-file .env prompt-optimizer
```

### Production Recommendations

1. **Use a reverse proxy** (nginx) in front of Streamlit for HTTPS
2. **Set `server.headless = true`** in `.streamlit/config.toml`
3. **Restrict access** if deployed publicly (Streamlit supports basic auth)
4. **Monitor API costs** — each optimization run calls LLM ~300 times

### Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'src'` | Run `pip install -e .` from project root |
| `UnicodeDecodeError` on Windows | Ensure all files use UTF-8 encoding |
| API timeout errors | Increase `PO_EVALUATION__TIMEOUT_SECONDS` or reduce concurrency |
| Streamlit won't start | Check port 8501 is free: `lsof -i :8501` |

---

<a id="chinese"></a>

## 中文

### 本地开发

```bash
git clone https://github.com/yxrdhzm/promptOptimizationEngine.git
cd promptOptimizationEngine
pip install -e .
cp .env.example .env
# 编辑 .env 填写 API 密钥
streamlit run src/ui/app.py
```

### 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | `sk-xxx` |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 | `sk-ant-xxx` |
| `DASHSCOPE_API_KEY` | 阿里云 DashScope 密钥 | `sk-xxx` |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | `sk-xxx` |
| `PO_MODELS__EXECUTOR` | 执行模型 | `openai/gpt-4o-mini` |
| `PO_MODELS__OPTIMIZER` | 优化器模型 | `openai/gpt-4o` |
| `PO_MODELS__JUDGE` | Judge 模型 | `openai/gpt-4o-mini` |
| `PO_OPTIMIZER__MAX_ITERATIONS` | 最大迭代轮数 | `5` |
| `PO_OPTIMIZER__NUM_CANDIDATES` | 每轮候选数 | `3` |
| `PO_EVALUATION__MAX_CONCURRENCY` | 并发 API 调用数 | `10` |

### Docker（即将支持）

```bash
docker build -t prompt-optimizer .
docker run -p 8501:8501 --env-file .env prompt-optimizer
```

### 生产部署建议

1. **使用反向代理**（nginx）为 Streamlit 提供 HTTPS
2. **设置 `server.headless = true`** 在 `.streamlit/config.toml` 中
3. **限制访问**（Streamlit 支持基本认证）
4. **监控 API 成本** — 每次优化约调用 300 次 LLM

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| `ModuleNotFoundError: No module named 'src'` | 在项目根目录执行 `pip install -e .` |
| Windows 下 `UnicodeDecodeError` | 确保所有文件使用 UTF-8 编码 |
| API 超时 | 增加 `PO_EVALUATION__TIMEOUT_SECONDS` 或降低并发数 |
| Streamlit 无法启动 | 检查 8501 端口是否被占用 |
