import questionary
from typing import List, Optional, Tuple, Dict

from cli.models import AnalystType

ANALYST_ORDER = [
    ("市场分析师 | Market Analyst", AnalystType.MARKET),
    ("社交媒体分析师 | Social Media Analyst", AnalystType.SOCIAL),
    ("新闻分析师 | News Analyst", AnalystType.NEWS),
    ("基本面分析师 | Fundamentals Analyst", AnalystType.FUNDAMENTALS),
]


def get_ticker() -> str:
    """Prompt the user to enter a ticker symbol."""
    ticker = questionary.text(
        "请输入要分析的股票代码 | Enter the ticker symbol to analyze:",
        validate=lambda x: len(x.strip()) > 0 or "请输入有效的股票代码 | Please enter a valid ticker symbol.",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not ticker:
        console.print("\n[red]未提供股票代码，退出程序... | No ticker symbol provided. Exiting...[/red]")
        exit(1)

    return ticker.strip().upper()


def get_analysis_date() -> str:
    """Prompt the user to enter a date in YYYY-MM-DD format."""
    import re
    from datetime import datetime

    def validate_date(date_str: str) -> bool:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    date = questionary.text(
        "请输入分析日期 (YYYY-MM-DD) | Enter the analysis date (YYYY-MM-DD):",
        validate=lambda x: validate_date(x.strip())
        or "请输入有效的日期格式 YYYY-MM-DD | Please enter a valid date in YYYY-MM-DD format.",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not date:
        console.print("\n[red]未提供日期，退出程序... | No date provided. Exiting...[/red]")
        exit(1)

    return date.strip()


def select_analysts() -> List[AnalystType]:
    """Select analysts using an interactive checkbox."""
    choices = questionary.checkbox(
        "选择您的分析师团队 | Select Your [Analysts Team]:",
        choices=[
            questionary.Choice(display, value=value) for display, value in ANALYST_ORDER
        ],
        instruction="\n- 按空格键选择/取消选择分析师 | Press Space to select/unselect analysts\n- 按 'a' 键全选/取消全选 | Press 'a' to select/unselect all\n- 按回车键完成选择 | Press Enter when done",
        validate=lambda x: len(x) > 0 or "您必须至少选择一个分析师 | You must select at least one analyst.",
        style=questionary.Style(
            [
                ("checkbox-selected", "fg:green"),
                ("selected", "fg:green noinherit"),
                ("highlighted", "noinherit"),
                ("pointer", "noinherit"),
            ]
        ),
    ).ask()

    if not choices:
        console.print("\n[red]未选择分析师，退出程序... | No analysts selected. Exiting...[/red]")
        exit(1)

    return choices


def select_research_depth() -> int:
    """Select research depth using an interactive selection."""

    # Define research depth options with their corresponding values
    DEPTH_OPTIONS = [
        ("浅层 - 快速研究，少量辩论和策略讨论 | Shallow - Quick research, few debate rounds", 1),
        ("中等 - 中等程度，适度的辩论和策略讨论 | Medium - Moderate debate and strategy discussion", 3),
        ("深度 - 全面研究，深入的辩论和策略讨论 | Deep - Comprehensive research, in-depth debate", 5),
    ]

    choice = questionary.select(
        "选择您的研究深度 | Select Your [Research Depth]:",
        choices=[
            questionary.Choice(display, value=value) for display, value in DEPTH_OPTIONS
        ],
        instruction="\n- 使用方向键导航 | Use arrow keys to navigate\n- 按回车键选择 | Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:yellow noinherit"),
                ("highlighted", "fg:yellow noinherit"),
                ("pointer", "fg:yellow noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print("\n[red]未选择研究深度，退出程序... | No research depth selected. Exiting...[/red]")
        exit(1)

    return choice


def select_shallow_thinking_agent(provider) -> str:
    """Select shallow thinking llm engine using an interactive selection."""

    # Define shallow thinking llm engine options with their corresponding model names
    SHALLOW_AGENT_OPTIONS = {
        "openai": [
            ("GPT-4o-mini - Fast and efficient for quick tasks", "gpt-4o-mini"),
            ("GPT-4.1-nano - Ultra-lightweight model for basic operations", "gpt-4.1-nano"),
            ("GPT-4.1-mini - Compact model with good performance", "gpt-4.1-mini"),
            ("GPT-4o - Standard model with solid capabilities", "gpt-4o"),
        ],
        "anthropic": [
            ("Claude Haiku 3.5 - Fast inference and standard capabilities", "claude-3-5-haiku-latest"),
            ("Claude Sonnet 3.5 - Highly capable standard model", "claude-3-5-sonnet-latest"),
            ("Claude Sonnet 3.7 - Exceptional hybrid reasoning and agentic capabilities", "claude-3-7-sonnet-latest"),
            ("Claude Sonnet 4 - High performance and excellent reasoning", "claude-sonnet-4-0"),
        ],
        "google": [
            ("Gemini 2.0 Flash-Lite - Cost efficiency and low latency", "gemini-2.0-flash-lite"),
            ("Gemini 2.0 Flash - Next generation features, speed, and thinking", "gemini-2.0-flash"),
            ("Gemini 2.5 Flash - Adaptive thinking, cost efficiency", "gemini-2.5-flash-preview-05-20"),
        ],
        "openrouter": [
            ("Meta: Llama 4 Scout", "meta-llama/llama-4-scout:free"),
            ("Meta: Llama 3.3 8B Instruct - A lightweight and ultra-fast variant of Llama 3.3 70B", "meta-llama/llama-3.3-8b-instruct:free"),
            ("google/gemini-2.0-flash-exp:free - Gemini Flash 2.0 offers a significantly faster time to first token", "google/gemini-2.0-flash-exp:free"),
        ],
        "ollama": [
            ("llama3.1 local", "llama3.1"),
            ("llama3.2 local", "llama3.2"),
        ],
        # "qwen": [
        #     ("Qwen-Turbo - Fast speed and low cost, suitable for simple tasks", "qwen-turbo-latest"),
        #     ("Qwen-Plus - Balanced combination of performance and speed, ideal for moderately complex tasks", "qwen-plus-latest"),
        #     ("Qwen-Max - For complex and multi-step tasks", "qwen-max-latest"),
        #     ("Qwen-Long - For long context tasks", "qwen-long")
        # ],
        "阿里百炼 (dashscope)": [
            ("通义千问 Turbo - 快速响应，适合日常对话", "qwen-turbo"),
            ("通义千问 Plus - 平衡性能和成本", "qwen-plus"),
            ("通义千问 Max - 最强性能", "qwen-max"),
        ]
    }

    # 获取选项列表
    options = SHALLOW_AGENT_OPTIONS[provider.lower()]

    # 为阿里百炼设置默认选择（通义千问 Turbo）
    default_choice = None
    if "阿里百炼" in provider:
        default_choice = options[0][1]  # 使用value而不是display

    choice = questionary.select(
        "选择您的快速思考LLM引擎 | Select Your [Quick-Thinking LLM Engine]:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in options
        ],
        default=default_choice,
        instruction="\n- 使用方向键导航 | Use arrow keys to navigate\n- 按回车键选择 | Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:green noinherit"),
                ("highlighted", "fg:green noinherit"),
                ("pointer", "fg:green noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print(
            "\n[red]未选择快速思考LLM引擎，退出程序... | No shallow thinking llm engine selected. Exiting...[/red]"
        )
        exit(1)

    return choice


def select_deep_thinking_agent(provider) -> str:
    """Select deep thinking llm engine using an interactive selection."""

    # Define deep thinking llm engine options with their corresponding model names
    DEEP_AGENT_OPTIONS = {
        "openai": [
            ("GPT-4.1-nano - Ultra-lightweight model for basic operations", "gpt-4.1-nano"),
            ("GPT-4.1-mini - Compact model with good performance", "gpt-4.1-mini"),
            ("GPT-4o - Standard model with solid capabilities", "gpt-4o"),
            ("o4-mini - Specialized reasoning model (compact)", "o4-mini"),
            ("o3-mini - Advanced reasoning model (lightweight)", "o3-mini"),
            ("o3 - Full advanced reasoning model", "o3"),
            ("o1 - Premier reasoning and problem-solving model", "o1"),
        ],
        "anthropic": [
            ("Claude Haiku 3.5 - Fast inference and standard capabilities", "claude-3-5-haiku-latest"),
            ("Claude Sonnet 3.5 - Highly capable standard model", "claude-3-5-sonnet-latest"),
            ("Claude Sonnet 3.7 - Exceptional hybrid reasoning and agentic capabilities", "claude-3-7-sonnet-latest"),
            ("Claude Sonnet 4 - High performance and excellent reasoning", "claude-sonnet-4-0"),
            ("Claude Opus 4 - Most powerful Anthropic model", "	claude-opus-4-0"),
        ],
        "google": [
            ("Gemini 2.0 Flash-Lite - Cost efficiency and low latency", "gemini-2.0-flash-lite"),
            ("Gemini 2.0 Flash - Next generation features, speed, and thinking", "gemini-2.0-flash"),
            ("Gemini 2.5 Flash - Adaptive thinking, cost efficiency", "gemini-2.5-flash-preview-05-20"),
            ("Gemini 2.5 Pro", "gemini-2.5-pro-preview-06-05"),
        ],
        "openrouter": [
            ("DeepSeek V3 - a 685B-parameter, mixture-of-experts model", "deepseek/deepseek-chat-v3-0324:free"),
            ("Deepseek - latest iteration of the flagship chat model family from the DeepSeek team.", "deepseek/deepseek-chat-v3-0324:free"),
        ],
        "ollama": [
            ("llama3.1 local", "llama3.1"),
            ("qwen3", "qwen3"),
        ],
        # "qwen": [
        #     ("QwQ - Reasoning model. Have reached the level of DeepSeek-R1", "qwq-plus"),
        #     ("Qwen-Turbo - Fast speed and low cost, suitable for simple tasks", "qwen-turbo-latest"),
        #     ("Qwen-Plus - Balanced combination of performance and speed, ideal for moderately complex tasks", "qwen-plus-latest"),
        #     ("Qwen-Max - For complex and multi-step tasks", "qwen-max-latest"),
        #     ("Qwen-Long - For long context tasks", "qwen-long"),
        # ],
        "阿里百炼 (dashscope)": [
            ("通义千问 Turbo - 快速响应，适合日常对话", "qwen-turbo"),
            ("通义千问 Plus - 平衡性能和成本", "qwen-plus"),
            ("通义千问 Max - 最强性能", "qwen-max"),
            ("通义千问 Max 长文本版 - 支持超长上下文", "qwen-max-longcontext"),
        ]
    }
    
    # 获取选项列表
    options = DEEP_AGENT_OPTIONS[provider.lower()]

    # 为阿里百炼设置默认选择（通义千问 Turbo）
    default_choice = None
    if "阿里百炼" in provider:
        default_choice = options[0][1]  # 使用value而不是display

    choice = questionary.select(
        "选择您的深度思考LLM引擎 | Select Your [Deep-Thinking LLM Engine]:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in options
        ],
        default=default_choice,
        instruction="\n- 使用方向键导航 | Use arrow keys to navigate\n- 按回车键选择 | Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:green noinherit"),
                ("highlighted", "fg:green noinherit"),
                ("pointer", "fg:green noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print("\n[red]未选择深度思考LLM引擎，退出程序... | No deep thinking llm engine selected. Exiting...[/red]")
        exit(1)

    return choice

def select_llm_provider() -> tuple[str, str]:
    """Select the LLM provider using interactive selection."""
    # Define LLM provider options with their corresponding endpoints
    # 阿里百炼作为默认推荐选项放在第一位
    BASE_URLS = [
        ("阿里百炼 (DashScope)", "https://dashscope.aliyuncs.com/api/v1"),
        # ("Qwen", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        ("OpenAI", "https://api.openai.com/v1"),
        ("Anthropic", "https://api.anthropic.com/"),
        ("Google", "https://generativelanguage.googleapis.com/v1"),
        ("Openrouter", "https://openrouter.ai/api/v1"),
        ("Ollama", "http://localhost:11434/v1"),
    ]
    
    choice = questionary.select(
        "选择您的LLM提供商 | Select your LLM Provider:",
        choices=[
            questionary.Choice(display, value=(display, value))
            for display, value in BASE_URLS
        ],
        default=(BASE_URLS[0][0], BASE_URLS[0][1]),  # 默认选择阿里百炼的完整值
        instruction="\n- 使用方向键导航 | Use arrow keys to navigate\n- 按回车键选择 | Press Enter to select\n- 🇨🇳 推荐使用阿里百炼 (默认选择)",
        style=questionary.Style(
            [
                ("selected", "fg:green noinherit"),
                ("highlighted", "fg:green noinherit"),
                ("pointer", "fg:green noinherit"),
            ]
        ),
    ).ask()
    
    if choice is None:
        console.print("\n[red]未选择LLM提供商，退出程序... | No LLM provider selected. Exiting...[/red]")
        exit(1)
    
    display_name, url = choice
    print(f"您选择了 | You selected: {display_name}\tURL: {url}")

    return display_name, url

def extract_reports_from_final_state(final_state):
    analyst_reports = []
    if final_state.get("market_report"):
        analyst_reports.append(("Market Analyst", final_state["market_report"]))
    if final_state.get("sentiment_report"):
        analyst_reports.append(("Sentiment Analyst", final_state["sentiment_report"]))
    if final_state.get("news_report"):
        analyst_reports.append(("News Analyst", final_state["news_report"]))
    if final_state.get("fundamentals_report"):
        analyst_reports.append(("Fundamentals Analyst", final_state["fundamentals_report"]))
    if final_state.get("investment_debate_state"):
        debate_state = final_state["investment_debate_state"]
        if debate_state.get("bull_history"):
            analyst_reports.append(("Investment Debate - Bull", debate_state["bull_history"]))
        if debate_state.get("bear_history"):
            analyst_reports.append(("Investment Debate - Bear", debate_state["bear_history"]))
        if debate_state.get("judge_decision"):
            analyst_reports.append(("Investment Debate - Judge Decision", debate_state["judge_decision"]))
    if final_state.get("trader_investment_plan"):
        analyst_reports.append(("Trader Investment Plan", final_state["trader_investment_plan"]))
    if final_state.get("risk_debate_state"):
        risk_state = final_state["risk_debate_state"]
        if risk_state.get("risky_history"):
            analyst_reports.append(("Risk Debate - Risky", risk_state["risky_history"]))
        if risk_state.get("safe_history"):
            analyst_reports.append(("Risk Debate - Safe", risk_state["safe_history"]))
        if risk_state.get("neutral_history"):
            analyst_reports.append(("Risk Debate - Neutral", risk_state["neutral_history"]))
        if risk_state.get("judge_decision"):
            analyst_reports.append(("Risk Debate - Judge Decision", risk_state["judge_decision"]))
    return {report_name: report_content for report_name, report_content in analyst_reports if report_content}

def save_reports(ticker: str, reports: Dict[str, str], output_dir: str, filename = "") -> None:
    """
        Save the generated reports to the specified output directory.
        Args:
            ticker (str): The ticker symbol for which the reports are generated.
            reports (Dict[str, str]): A dictionary where keys are report names and values are report content.
            output_dir (str): The directory where the reports will be saved.
            filename (str): Optional filename to save the reports as a single file. If empty, the filename will be formatted as `{ticker}_reports_{time}.md`.
    """
    import os
    from datetime import datetime

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if filename:
        file_path = os.path.join(output_dir, filename)
    else:
        time_str = datetime.now().strftime("%Y%m%d_%H%M")
        file_path = os.path.join(output_dir, f"{ticker}_reports_{time_str}.md")

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(f"# Reports for {ticker}\n\n")
        file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        for report_name, report_content in reports.items():
            file.write(f"## {report_name}\n\n")
            file.write(report_content + "\n\n")
            