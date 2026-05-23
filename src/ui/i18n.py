"""国际化模块 - 中英文切换"""

from __future__ import annotations

from typing import Any

LOCALES: dict[str, dict[str, str]] = {
    "zh": {
        # 通用
        "app_title": "提示词优化引擎",
        "app_subtitle": "通过 LLM 自我迭代，自动优化系统提示词",
        "language": "语言",
        # 侧边栏
        "sidebar_config": "配置",
        "sidebar_models": "模型设置",
        "sidebar_optimizer": "优化参数",
        "executor_model": "执行模型",
        "optimizer_model": "优化器模型",
        "judge_model": "Judge 模型",
        "max_iterations": "最大迭代轮数",
        "num_candidates": "每轮候选数",
        "early_stop": "早停耐心",
        # 标签页
        "tab_upload": "上传测试集",
        "tab_optimize": "运行优化",
        "tab_results": "查看结果",
        # 上传测试集
        "upload_title": "测试集管理",
        "upload_label": "上传 JSONL 测试集",
        "upload_help": "每行一个 JSON 对象，包含 input 和 expected 字段",
        "upload_success": "成功导入 {n} 条测试用例",
        "example_format": "查看示例格式",
        "current_dataset": "当前测试集: {n} 条用例",
        # 运行优化
        "optimize_title": "优化配置",
        "task_desc_label": "任务描述",
        "task_desc_placeholder": "例如：电商客服退款咨询助手，需要准确回答退款政策、处理退款申请、安抚客户情绪",
        "initial_prompt_label": "初始系统提示词 (可选)",
        "initial_prompt_placeholder": "留空则使用默认提示词",
        "start_optimize": "开始优化",
        "error_no_task": "请先输入任务描述",
        "error_no_dataset": "请先上传测试集",
        "running": "准备中...",
        "optimize_done": "优化完成！切换到「查看结果」标签页查看",
        # 查看结果
        "results_title": "优化结果摘要",
        "initial_score": "初始得分",
        "final_score": "最终得分",
        "improvement": "提升幅度",
        "iterations": "迭代轮数",
        "score_trend": "得分趋势",
        "prompt_diff": "提示词对比",
        "view_diff": "查看 Diff",
        "best_prompt": "最优提示词",
        "export_report": "导出报告",
        "download_report": "下载 Markdown 报告",
        "download_prompt": "下载最优 Prompt",
        "no_results": "请先运行优化流程",
        # API 设置
        "tab_api": "API 设置",
        "api_title": "大模型 API 配置",
        "api_desc": "填写各角色使用的模型及其 API Key，配置会保存到本地 .env 文件",
        "provider": "提供商",
        "provider_openai": "OpenAI",
        "provider_anthropic": "Anthropic",
        "provider_dashscope": "阿里云 DashScope",
        "provider_deepseek": "DeepSeek",
        "provider_ollama": "Ollama (本地)",
        "api_key": "API Key",
        "api_key_placeholder": "sk-...",
        "api_base_url": "API Base URL (可选)",
        "api_base_url_placeholder": "留空使用默认地址",
        "api_status_configured": "已配置",
        "api_status_not_configured": "未配置",
        "api_save": "保存配置",
        "api_save_success": "配置已保存到 .env 文件",
        "api_save_error": "保存失败: {error}",
        "api_test": "测试连接",
        "api_testing": "正在测试连接...",
        "api_test_success": "连接成功！模型: {model}",
        "api_test_fail": "连接失败: {error}",
        "api_note": "提示: API Key 保存在项目根目录的 .env 文件中，不会上传到服务器",
        # 进度
        "progress_start": "开始评估初始 Prompt...",
        "progress_init_score": "初始 Prompt 得分: {score}",
        "progress_iter": "第 {cur}/{total} 轮迭代...",
        "progress_candidate": "  候选 {cur}/{total}: score={score}",
        "progress_round_done": "第 {n} 轮完成: 最优={best}, 全局最优={global_best}",
        "progress_early_stop": "连续无提升，触发早停",
        "progress_done": "优化完成！",
    },
    "en": {
        # General
        "app_title": "Prompt Optimizer",
        "app_subtitle": "Automatically optimize system prompts via LLM self-iteration",
        "language": "Language",
        # Sidebar
        "sidebar_config": "Settings",
        "sidebar_models": "Model Settings",
        "sidebar_optimizer": "Optimizer Params",
        "executor_model": "Executor Model",
        "optimizer_model": "Optimizer Model",
        "judge_model": "Judge Model",
        "max_iterations": "Max Iterations",
        "num_candidates": "Candidates per Round",
        "early_stop": "Early Stop Patience",
        # Tabs
        "tab_upload": "Upload Test Set",
        "tab_optimize": "Run Optimization",
        "tab_results": "View Results",
        # Upload
        "upload_title": "Test Set Management",
        "upload_label": "Upload JSONL Test Set",
        "upload_help": "One JSON object per line, with 'input' and 'expected' fields",
        "upload_success": "Successfully imported {n} test cases",
        "example_format": "View Example Format",
        "current_dataset": "Current dataset: {n} cases",
        # Optimize
        "optimize_title": "Optimization Config",
        "task_desc_label": "Task Description",
        "task_desc_placeholder": "e.g. E-commerce customer service refund assistant, needs to answer refund policies, handle refund requests, and calm customers",
        "initial_prompt_label": "Initial System Prompt (optional)",
        "initial_prompt_placeholder": "Leave empty to use default prompt",
        "start_optimize": "Start Optimization",
        "error_no_task": "Please enter a task description",
        "error_no_dataset": "Please upload a test set first",
        "running": "Preparing...",
        "optimize_done": "Done! Switch to the 'View Results' tab",
        # Results
        "results_title": "Optimization Summary",
        "initial_score": "Initial Score",
        "final_score": "Final Score",
        "improvement": "Improvement",
        "iterations": "Iterations",
        "score_trend": "Score Trend",
        "prompt_diff": "Prompt Comparison",
        "view_diff": "View Diff",
        "best_prompt": "Best Prompt",
        "export_report": "Export Report",
        "download_report": "Download Markdown Report",
        "download_prompt": "Download Best Prompt",
        "no_results": "Run optimization first",
        # API Settings
        "tab_api": "API Settings",
        "api_title": "LLM API Configuration",
        "api_desc": "Configure API keys for each model role. Settings are saved to local .env file",
        "provider": "Provider",
        "provider_openai": "OpenAI",
        "provider_anthropic": "Anthropic",
        "provider_dashscope": "Alibaba DashScope",
        "provider_deepseek": "DeepSeek",
        "provider_ollama": "Ollama (Local)",
        "api_key": "API Key",
        "api_key_placeholder": "sk-...",
        "api_base_url": "API Base URL (optional)",
        "api_base_url_placeholder": "Leave empty for default",
        "api_status_configured": "Configured",
        "api_status_not_configured": "Not configured",
        "api_save": "Save Config",
        "api_save_success": "Config saved to .env file",
        "api_save_error": "Save failed: {error}",
        "api_test": "Test Connection",
        "api_testing": "Testing connection...",
        "api_test_success": "Connected! Model: {model}",
        "api_test_fail": "Connection failed: {error}",
        "api_note": "Note: API keys are saved in the project root .env file and are not uploaded to any server",
        # Progress
        "progress_start": "Evaluating initial prompt...",
        "progress_init_score": "Initial prompt score: {score}",
        "progress_iter": "Iteration {cur}/{total}...",
        "progress_candidate": "  Candidate {cur}/{total}: score={score}",
        "progress_round_done": "Round {n} done: best={best}, global best={global_best}",
        "progress_early_stop": "No improvement, triggering early stop",
        "progress_done": "Optimization complete!",
    },
}


def t(key: str, **kwargs: Any) -> str:
    """获取翻译文本，支持变量插值"""
    lang = _get_lang()
    text = LOCALES.get(lang, LOCALES["zh"]).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    return text


def _get_lang() -> str:
    """从 Streamlit session state 获取当前语言"""
    try:
        import streamlit as st
        return st.session_state.get("lang", "zh")
    except Exception:
        return "zh"
