# Prompt Optimizer / 提示词优化引擎

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Automatically optimize system prompts via LLM self-iteration**
> 通过 LLM 自我迭代，自动优化系统提示词

---

## What it does / 功能介绍

Prompt Optimizer uses an **OPRO (Optimization by Prompting)** approach: it evaluates your prompt against a test set, analyzes failure cases, and iteratively generates better prompts — all automatically.

提示词优化引擎采用 **OPRO（基于提示的优化）** 方法：通过测试集评估提示词，分析失败案例，自动生成更优的提示词。

### Key Features / 核心功能

| Feature | 描述 |
|---------|------|
| **OPRO Iterative Optimization** | Multi-round self-improvement with early stopping / 多轮自迭代优化，支持早停 |
| **LLM-as-Judge** | Automated 1-5 scoring with reasoning / 自动化 1-5 分评分及理由 |
| **Multi-provider Support** | OpenAI, Anthropic, DashScope, DeepSeek, Ollama / 支持多家大模型提供商 |
| **Parallel Evaluation** | Async concurrent test case evaluation / 异步并发评估测试用例 |
| **Bilingual UI** | Chinese / English language switching / 中英文界面切换 |
| **Report Export** | Markdown evaluation reports / Markdown 格式评估报告导出 |

## Architecture / 架构

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

## Quick Start / 快速开始

### 1. Install / 安装

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/promptOptimizationEngine.git
cd promptOptimizationEngine

# Install dependencies
pip install -e .
```

### 2. Configure API Keys / 配置 API 密钥

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
# Edit .env with your API keys
```

Or use the **API Settings** tab in the web UI to configure interactively.

也可以在 Web 界面的「API 设置」标签页中交互式配置。

### 3. Run / 运行

**Web UI (Streamlit):**

```bash
streamlit run src/ui/app.py
```

Open http://localhost:8501 in your browser.

**CLI:**

```bash
python run.py \
  --task "E-commerce customer service refund assistant" \
  --test-set tests/fixtures/sample_testset.jsonl \
  --output report.md
```

## Test Set Format / 测试集格式

JSONL file, one JSON object per line:

每行一个 JSON 对象：

```json
{"id": "case_001", "input": "What is the refund policy?", "expected": "We offer 7-day no-reason refunds..."}
{"id": "case_002", "input": "How to apply for a refund?", "expected": "Go to your order page and click apply..."}
```

| Field / 字段 | Required / 必填 | Description / 说明 |
|-------------|----------------|-------------------|
| `input` | Yes | User question / 用户问题 |
| `expected` | Yes | Reference answer / 参考答案 |
| `id` | No | Case identifier / 用例标识 |
| `eval_rubric` | No | Custom scoring criteria / 自定义评分标准 |
| `tags` | No | Tags for filtering / 标签 |

## Configuration / 配置

All settings can be configured via `configs/default.yaml` or environment variables:

所有配置可通过 `configs/default.yaml` 或环境变量设置：

```yaml
models:
  executor: "openai/gpt-4o-mini"    # Model for generating answers / 生成回答的模型
  optimizer: "openai/gpt-4o"         # Model for prompt optimization / 优化提示词的模型
  judge: "openai/gpt-4o-mini"        # Model for scoring / 评分的模型

optimizer:
  max_iterations: 5                  # Max optimization rounds / 最大优化轮数
  num_candidates: 3                  # Candidates per round / 每轮候选数
  early_stop_patience: 2             # Rounds without improvement to trigger early stop / 早停耐心值
```

Environment variables use `PO_` prefix: `PO_MODELS__EXECUTOR`, etc.

## Project Structure / 项目结构

```
prompt-optimizer/
├── configs/default.yaml       # Default configuration / 默认配置
├── src/
│   ├── infrastructure/        # LLM adapter, cache, storage / 基础设施层
│   ├── core/                  # OPRO optimizer, judge, evaluation / 核心引擎层
│   ├── application/           # Runner, exporter / 应用编排层
│   └── ui/                    # Streamlit app + i18n / 展示层
├── tests/                     # Unit tests / 单元测试
├── data/                      # Runtime data (gitignored) / 运行时数据
├── run.py                     # CLI entry point / CLI 入口
└── pyproject.toml             # Dependencies / 依赖管理
```

## Tech Stack / 技术栈

- **LLM Gateway**: [LiteLLM](https://github.com/BerriAI/litellm) — 100+ models, one API
- **Async**: Python asyncio — concurrent evaluation
- **Templates**: Jinja2 — prompt template management
- **Storage**: SQLite + SQLModel — lightweight persistence
- **Cache**: diskcache — evaluation result caching
- **UI**: Streamlit — rapid prototyping
- **Config**: Pydantic Settings — type-safe configuration

## Roadmap / 路线图

- [ ] DSPy / TextGrad integration
- [ ] Multi-Judge voting system
- [ ] Few-shot dynamic context optimization
- [ ] FastAPI + React multi-user interface
- [ ] LangSmith trace integration

## License / 许可

MIT License
