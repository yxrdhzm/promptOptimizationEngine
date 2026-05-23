<p align="center">
  <h1 align="center">Prompt Optimizer</h1>
  <p align="center">LLM Prompt Optimization Engine</p>
</p>

<p align="center">
  <a href="#english">English</a> · <a href="#chinese">中文</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT">
</p>

---

<a id="english"></a>

## English

Automatically optimize system prompts via LLM self-iteration using **OPRO (Optimization by Prompting)**. It evaluates your prompt against a test set, analyzes failure cases, and iteratively generates better prompts — all automatically.

### Features

| Feature | Description |
|---------|-------------|
| **OPRO Iterative Optimization** | Multi-round self-improvement with early stopping |
| **LLM-as-Judge** | Automated 1-5 scoring with reasoning |
| **Multi-provider Support** | OpenAI, Anthropic, DashScope, DeepSeek, Ollama |
| **Parallel Evaluation** | Async concurrent test case evaluation |
| **Bilingual UI** | Chinese / English language switching |
| **Report Export** | Markdown evaluation reports |

### Architecture

```
┌─────────────────────────────────────────────────┐
│              Streamlit UI (Bilingual)            │
├─────────────────────────────────────────────────┤
│         Application Layer                       │
│   OptimizationRunner  │  EvaluationPipeline     │
├─────────────────────────────────────────────────┤
│           Core Engine                           │
│   OPROOptimizer  │  LLMJudge  │  Templates     │
├─────────────────────────────────────────────────┤
│         Infrastructure                          │
│   LiteLLM Adapter  │  Cache  │  SQLite Store    │
└─────────────────────────────────────────────────┘
```

### Quick Start

```bash
git clone https://github.com/yxrdhzm/promptOptimizationEngine.git
cd promptOptimizationEngine
pip install -e .
cp .env.example .env   # Fill in your API keys
```

**Web UI:**
```bash
streamlit run src/ui/app.py
# Open http://localhost:8501
```

**CLI:**
```bash
python run.py \
  --task "E-commerce customer service refund assistant" \
  --test-set tests/fixtures/sample_testset.jsonl \
  --output report.md
```

### Test Set Format

JSONL file, one JSON object per line:

```json
{"id": "case_001", "input": "What is the refund policy?", "expected": "We offer 7-day no-reason refunds..."}
```

| Field | Required | Description |
|-------|----------|-------------|
| `input` | Yes | User question |
| `expected` | Yes | Reference answer |
| `id` | No | Case identifier |
| `eval_rubric` | No | Custom scoring criteria |
| `tags` | No | Tags for filtering |

### Configuration

```yaml
models:
  executor: "openai/gpt-4o-mini"
  optimizer: "openai/gpt-4o"
  judge: "openai/gpt-4o-mini"

optimizer:
  max_iterations: 5
  num_candidates: 3
  early_stop_patience: 2
```

Environment variables use `PO_` prefix: `PO_MODELS__EXECUTOR`, etc.

### Tech Stack

- **LLM Gateway**: [LiteLLM](https://github.com/BerriAI/litellm) — 100+ models, one API
- **Async**: Python asyncio — concurrent evaluation
- **Templates**: Jinja2 — prompt template management
- **Storage**: SQLite + SQLModel — lightweight persistence
- **Cache**: diskcache — evaluation result caching
- **UI**: Streamlit — rapid prototyping
- **Config**: Pydantic Settings — type-safe configuration

### Roadmap

- [ ] DSPy / TextGrad integration
- [ ] Multi-Judge voting system
- [ ] Few-shot dynamic context optimization
- [ ] FastAPI + React multi-user interface
- [ ] LangSmith trace integration

---

<a id="chinese"></a>

## 中文

通过 LLM 自我迭代，自动优化系统提示词。采用 **OPRO（基于提示的优化）** 方法：通过测试集评估提示词，分析失败案例，自动生成更优的提示词。

### 核心功能

| 功能 | 描述 |
|------|------|
| **OPRO 迭代优化** | 多轮自迭代优化，支持早停 |
| **LLM-as-Judge** | 自动化 1-5 分评分及理由 |
| **多模型支持** | OpenAI、Anthropic、DashScope、DeepSeek、Ollama |
| **并发评估** | 异步并发评估测试用例 |
| **中英双语** | 界面支持中英文切换 |
| **报告导出** | Markdown 格式评估报告 |

### 架构

```
┌─────────────────────────────────────────────────┐
│              Streamlit UI（中英双语）             │
├─────────────────────────────────────────────────┤
│              应用编排层                          │
│   OptimizationRunner  │  EvaluationPipeline     │
├─────────────────────────────────────────────────┤
│              核心引擎层                          │
│   OPROOptimizer  │  LLMJudge  │  Templates     │
├─────────────────────────────────────────────────┤
│              基础设施层                          │
│   LiteLLM Adapter  │  Cache  │  SQLite Store    │
└─────────────────────────────────────────────────┘
```

### 快速开始

```bash
git clone https://github.com/yxrdhzm/promptOptimizationEngine.git
cd promptOptimizationEngine
pip install -e .
cp .env.example .env   # 填写 API 密钥
```

**Web 界面：**
```bash
streamlit run src/ui/app.py
# 打开 http://localhost:8501
```

**命令行：**
```bash
python run.py \
  --task "电商客服退款咨询助手" \
  --test-set tests/fixtures/sample_testset.jsonl \
  --output report.md
```

### 测试集格式

JSONL 文件，每行一个 JSON 对象：

```json
{"id": "case_001", "input": "什么是退款政策？", "expected": "我们提供7天无理由退款..."}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `input` | 是 | 用户问题 |
| `expected` | 是 | 参考答案 |
| `id` | 否 | 用例标识 |
| `eval_rubric` | 否 | 自定义评分标准 |
| `tags` | 否 | 标签 |

### 配置

```yaml
models:
  executor: "openai/gpt-4o-mini"
  optimizer: "openai/gpt-4o"
  judge: "openai/gpt-4o-mini"

optimizer:
  max_iterations: 5
  num_candidates: 3
  early_stop_patience: 2
```

环境变量使用 `PO_` 前缀：`PO_MODELS__EXECUTOR` 等。

### 技术栈

- **LLM 网关**: [LiteLLM](https://github.com/BerriAI/litellm) — 100+ 模型，统一接口
- **异步**: Python asyncio — 并发评估
- **模板**: Jinja2 — 提示词模板管理
- **存储**: SQLite + SQLModel — 轻量持久化
- **缓存**: diskcache — 评估结果缓存
- **UI**: Streamlit — 快速原型开发
- **配置**: Pydantic Settings — 类型安全配置

### 路线图

- [ ] DSPy / TextGrad 集成
- [ ] 多 Judge 投票系统
- [ ] Few-shot 动态上下文优化
- [ ] FastAPI + React 多用户界面
- [ ] LangSmith 追踪集成

---

<p align="center">
  <sub>Made with ❤️ by <a href="https://github.com/yxrdhzm">yxrdhzm</a></sub>
</p>
