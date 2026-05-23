"""Streamlit UI - 提示词优化引擎主界面"""

from __future__ import annotations

import sys
from pathlib import Path

# 将项目根目录加入 sys.path
_root = str(Path(__file__).resolve().parent.parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

import json
import asyncio
import os

import pandas as pd
import streamlit as st

from src.infrastructure.config import load_config
from src.core.schemas import TestCase
from src.application.runner import OptimizationRunner
from src.application.exporter import generate_report, generate_diff
from src.ui.i18n import t

# --- 隐藏 Streamlit 原生汉堡菜单，用我们自己的设置替代 ---
_HIDE_MENU = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""


def _load_env() -> dict[str, str]:
    """从 .env 文件加载已有配置"""
    env_path = Path(_root) / ".env"
    result: dict[str, str] = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                result[key.strip()] = val.strip().strip('"').strip("'")
    return result


def _save_env(data: dict[str, str]) -> None:
    """将配置追加/更新到 .env 文件"""
    env_path = Path(_root) / ".env"
    existing: dict[str, str] = {}
    if env_path.exists():
        lines: list[str] = []
        for line in env_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                k, _, v = stripped.partition("=")
                existing[k.strip()] = v.strip()
            else:
                lines.append(line)
    else:
        lines = ["# Prompt Optimizer - API Keys", ""]

    for key, val in data.items():
        if val:
            existing[key] = val

    output_lines = lines.copy()
    for key, val in existing.items():
        output_lines.append(f'{key}="{val}"')

    env_path.write_text("\n".join(output_lines) + "\n", encoding="utf-8")


PROVIDERS: dict[str, dict[str, str]] = {
    "openai": {
        "env_key": "OPENAI_API_KEY",
        "default_model": "openai/gpt-4o-mini",
        "default_base": "",
    },
    "anthropic": {
        "env_key": "ANTHROPIC_API_KEY",
        "default_model": "anthropic/claude-sonnet-4-20250514",
        "default_base": "",
    },
    "dashscope": {
        "env_key": "DASHSCOPE_API_KEY",
        "default_model": "openai/qwen-plus",
        "default_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    },
    "deepseek": {
        "env_key": "DEEPSEEK_API_KEY",
        "default_model": "openai/deepseek-chat",
        "default_base": "https://api.deepseek.com/v1",
    },
    "ollama": {
        "env_key": "",
        "default_model": "ollama/qwen2.5:7b",
        "default_base": "http://localhost:11434/v1",
    },
}


def parse_jsonl(content: str) -> list[TestCase]:
    """解析 JSONL 格式的测试集"""
    cases = []
    for line_num, line in enumerate(content.strip().split("\n"), 1):
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            cases.append(TestCase(
                id=data.get("id", f"case_{line_num:03d}"),
                input=data["input"],
                expected=data["expected"],
                eval_rubric=data.get("eval_rubric"),
                tags=data.get("tags", []),
            ))
        except (json.JSONDecodeError, KeyError) as e:
            st.warning(f"Line {line_num} parse error: {e}")
    return cases


def _render_api_tab() -> None:
    """渲染 API 设置标签页"""
    st.subheader(t("api_title"))
    st.caption(t("api_desc"))

    env = _load_env()

    # 三种角色各自的配置
    roles = [
        ("executor", t("executor_model"), "executor_model"),
        ("optimizer", t("optimizer_model"), "optimizer_model"),
        ("judge", t("judge_model"), "judge_model"),
    ]

    for role_key, role_label, config_field in roles:
        with st.expander(f"{role_label}", expanded=True):
            c1, c2 = st.columns(2)

            # 读取当前值
            current_model = env.get(f"PO_{config_field.upper()}", "")

            with c1:
                provider = st.selectbox(
                    t("provider"),
                    options=list(PROVIDERS.keys()),
                    format_func=lambda x: t(f"provider_{x}"),
                    key=f"provider_{role_key}",
                )
                p = PROVIDERS[provider]

                api_key = st.text_input(
                    f"{t('api_key')} ({role_label})",
                    value=env.get(p["env_key"], ""),
                    type="password",
                    placeholder=t("api_key_placeholder"),
                    key=f"apikey_{role_key}",
                )

            with c2:
                model = st.text_input(
                    t("executor_model") if role_key == "executor" else t(role_key + "_model") if t(role_key + "_model") != role_key + "_model" else f"{role_label} Model",
                    value=current_model or p["default_model"],
                    key=f"model_{role_key}",
                )
                base_url = st.text_input(
                    t("api_base_url"),
                    value=env.get(f"PO_{config_field.upper()}_BASE_URL", p["default_base"]),
                    placeholder=t("api_base_url_placeholder"),
                    key=f"base_{role_key}",
                )

            # 状态指示
            if api_key or provider == "ollama":
                st.success(t("api_status_configured"))
            else:
                st.warning(t("api_status_not_configured"))

    # 保存按钮
    st.divider()
    if st.button(t("api_save"), type="primary", use_container_width=True):
        try:
            save_data: dict[str, str] = {}
            for role_key, _, config_field in roles:
                provider = st.session_state[f"provider_{role_key}"]
                p = PROVIDERS[provider]
                api_key = st.session_state[f"apikey_{role_key}"]
                model = st.session_state[f"model_{role_key}"]
                base_url = st.session_state[f"base_{role_key}"]

                if p["env_key"] and api_key:
                    save_data[p["env_key"]] = api_key
                save_data[f"PO_{config_field.upper()}"] = model
                if base_url:
                    save_data[f"PO_{config_field.upper()}_BASE_URL"] = base_url

            _save_env(save_data)
            st.success(t("api_save_success"))
        except Exception as e:
            st.error(t("api_save_error", error=str(e)))

    st.caption(t("api_note"))


def main() -> None:
    st.set_page_config(
        page_title="Prompt Optimizer",
        page_icon=":rocket:",
        layout="wide",
    )

    # 隐藏原生菜单
    st.markdown(_HIDE_MENU, unsafe_allow_html=True)

    # 语言切换
    if "lang" not in st.session_state:
        st.session_state["lang"] = "zh"

    # --- 顶部栏: 语言切换 + 标题 ---
    top_left, top_right = st.columns([6, 1])
    with top_right:
        lang = st.selectbox(
            t("language"),
            options=["zh", "en"],
            format_func=lambda x: "中文" if x == "zh" else "English",
            key="lang_select",
            label_visibility="collapsed",
        )
        st.session_state["lang"] = lang

    st.title(t("app_title"))
    st.caption(t("app_subtitle"))

    # --- 侧边栏配置 ---
    with st.sidebar:
        st.header(t("sidebar_config"))
        config = load_config()

        st.subheader(t("sidebar_models"))
        executor_model = st.text_input(t("executor_model"), value=config.models.executor)
        optimizer_model = st.text_input(t("optimizer_model"), value=config.models.optimizer)
        judge_model = st.text_input(t("judge_model"), value=config.models.judge)

        st.subheader(t("sidebar_optimizer"))
        max_iter = st.slider(t("max_iterations"), 1, 20, config.optimizer.max_iterations)
        num_candidates = st.slider(t("num_candidates"), 1, 5, config.optimizer.num_candidates)
        early_stop = st.slider(t("early_stop"), 1, 5, config.optimizer.early_stop_patience)

        config.models.executor = executor_model
        config.models.optimizer = optimizer_model
        config.models.judge = judge_model
        config.optimizer.max_iterations = max_iter
        config.optimizer.num_candidates = num_candidates
        config.optimizer.early_stop_patience = early_stop

    # --- 四个标签页 ---
    tab_api, tab_upload, tab_optimize, tab_results = st.tabs([
        t("tab_api"), t("tab_upload"), t("tab_optimize"), t("tab_results"),
    ])

    # === Tab 0: API 设置 ===
    with tab_api:
        _render_api_tab()

    # === Tab 1: 上传测试集 ===
    with tab_upload:
        st.subheader(t("upload_title"))

        uploaded_file = st.file_uploader(
            t("upload_label"),
            type=["jsonl", "json"],
            help=t("upload_help"),
        )

        if uploaded_file:
            content = uploaded_file.read().decode("utf-8")
            cases = parse_jsonl(content)
            st.session_state["test_cases"] = cases
            st.success(t("upload_success", n=len(cases)))

            df = pd.DataFrame([c.model_dump() for c in cases])
            st.dataframe(df, use_container_width=True)

        with st.expander(t("example_format")):
            st.code(
                '{"input": "What is the refund policy?", "expected": "We offer 7-day no-reason refunds..."}\n'
                '{"input": "How to apply for after-sales?", "expected": "Go to your order page and click apply..."}',
                language="json",
            )

        if "test_cases" in st.session_state:
            st.info(t("current_dataset", n=len(st.session_state["test_cases"])))

    # === Tab 2: 运行优化 ===
    with tab_optimize:
        st.subheader(t("optimize_title"))

        task_desc = st.text_area(
            t("task_desc_label"),
            placeholder=t("task_desc_placeholder"),
            height=100,
        )

        initial_prompt = st.text_area(
            t("initial_prompt_label"),
            placeholder=t("initial_prompt_placeholder"),
            height=150,
        )

        can_run = "test_cases" in st.session_state
        if st.button(t("start_optimize"), type="primary", disabled=not can_run):
            if not task_desc:
                st.error(t("error_no_task"))
            elif "test_cases" not in st.session_state:
                st.error(t("error_no_dataset"))
            else:
                st.session_state["running"] = True
                progress_bar = st.progress(0, text=t("running"))
                status_text = st.empty()

                def on_progress(msg: str, pct: float) -> None:
                    progress_bar.progress(pct, text=msg)
                    status_text.text(msg)

                runner = OptimizationRunner(config=config, on_progress=on_progress)

                cases = st.session_state["test_cases"]
                result = asyncio.run(
                    runner.run(
                        task_desc=task_desc,
                        test_cases=cases,
                        initial_prompt=initial_prompt or None,
                    )
                )

                st.session_state["result"] = result
                st.session_state["running"] = False
                st.success(t("optimize_done"))

    # === Tab 3: 查看结果 ===
    with tab_results:
        if "result" not in st.session_state:
            st.info(t("no_results"))
        else:
            result = st.session_state["result"]

            st.subheader(t("results_title"))

            col1, col2, col3, col4 = st.columns(4)
            col1.metric(t("initial_score"), f"{result.initial_score:.2f}")
            col2.metric(t("final_score"), f"{result.best_score:.2f}")
            col3.metric(t("improvement"), f"{result.improvement_pct:+.1f}%")
            col4.metric(t("iterations"), result.iterations)

            st.subheader(t("score_trend"))
            if result.history:
                chart_data = pd.DataFrame([
                    {"Round": s.iteration, "Score": s.score}
                    for s in result.history
                ])
                st.line_chart(chart_data.set_index("Round")["Score"])

            st.subheader(t("prompt_diff"))
            with st.expander(t("view_diff"), expanded=True):
                diff = generate_diff(result.initial_prompt, result.best_prompt)
                st.code(diff, language="diff")

            st.subheader(t("best_prompt"))
            st.code(result.best_prompt, language="text")

            st.subheader(t("export_report"))
            report_md = generate_report(result)
            st.download_button(
                t("download_report"),
                data=report_md,
                file_name=f"optimization_report_{result.run_id[:8]}.md",
                mime="text/markdown",
            )

            st.download_button(
                t("download_prompt"),
                data=result.best_prompt,
                file_name="best_prompt.txt",
                mime="text/plain",
            )


if __name__ == "__main__":
    main()
