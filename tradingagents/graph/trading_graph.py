# TradingAgents/graph/trading_graph.py

import os
from pathlib import Path
import json
from datetime import date
from typing import Dict, Any, Tuple, List, Optional

import jinja2
import webbrowser
import logging
import atexit
import sys

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from tradingagents.llm_adapters import ChatDashScope

from langgraph.prebuilt import ToolNode

from tradingagents.agents import *
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)

# from tradingagents.dataflows.interface import set_config, get_market_type
from tradingagents.dataflows.interface import set_config

from .conditional_logic import ConditionalLogic
from .setup import GraphSetup
from .propagation import Propagator
from .reflection import Reflector
from .signal_processing import SignalProcessor


class TradingAgentsGraph:
    """Main class that orchestrates the trading agents framework."""

    def __init__(
        self,
        selected_analysts=["market", "social", "news", "fundamentals"],
        debug=False,
        config: Dict[str, Any] = None,
    ):
        """Initialize the trading agents graph and components.

        Args:
            selected_analysts: List of analyst types to include
            debug: Whether to run in debug mode
            config: Configuration dictionary. If None, uses default config
        """
        self.debug = debug
        self.config = config or DEFAULT_CONFIG

        # Update the interface's config
        set_config(self.config)

        # Create necessary directories
        os.makedirs(
            os.path.join(self.config["project_dir"], "dataflows/data_cache"),
            # self.config["data_cache_dir"],
            exist_ok=True,
        )

        # 配置 Deepseek API 基础 URL 和 API Key
        # base_url = self.config.get("deepseek_base_url", "https://api.deepseek.com/v1")
        # api_key = self.config.get("deepseek_api_key", os.getenv("DEEPSEEK_API_KEY"))

        # Initialize LLMs with Deepseek configuration
        # self.deep_thinking_llm = ChatOpenAI(
        #     model=self.config["deep_think_llm"],
        #     base_url=base_url,
        #     api_key=api_key
        # )
        # self.quick_thinking_llm = ChatOpenAI(
        #     model=self.config["quick_think_llm"],
        #     temperature=0.1,
        #     base_url=base_url,
        #     api_key=api_key
        # )
        # Initialize memories
        # self.bull_memory = FinancialSituationMemory("bull_memory")
        # self.bear_memory = FinancialSituationMemory("bear_memory")
        # self.trader_memory = FinancialSituationMemory("trader_memory")
        # self.invest_judge_memory = FinancialSituationMemory("invest_judge_memory")
        # self.risk_manager_memory = FinancialSituationMemory("risk_manager_memory")

        # Initialize LLMs
        if self.config["llm_provider"].lower() == "openai" or self.config["llm_provider"] == "ollama" or self.config["llm_provider"] == "openrouter":
            self.deep_thinking_llm = ChatOpenAI(model=self.config["deep_think_llm"], base_url=self.config["backend_url"])
            self.quick_thinking_llm = ChatOpenAI(model=self.config["quick_think_llm"], base_url=self.config["backend_url"])
        elif self.config["llm_provider"].lower() == "anthropic":
            self.deep_thinking_llm = ChatAnthropic(model=self.config["deep_think_llm"], base_url=self.config["backend_url"])
            self.quick_thinking_llm = ChatAnthropic(model=self.config["quick_think_llm"], base_url=self.config["backend_url"])
        elif self.config["llm_provider"].lower() == "google":
            google_api_key = os.getenv('GOOGLE_API_KEY')
            self.deep_thinking_llm = ChatGoogleGenerativeAI(
                model=self.config["deep_think_llm"],
                google_api_key=google_api_key,
                temperature=0.1,
                max_tokens=2000
            )
            self.quick_thinking_llm = ChatGoogleGenerativeAI(
                model=self.config["quick_think_llm"],
                google_api_key=google_api_key,
                temperature=0.1,
                max_tokens=2000
            )
        elif (self.config["llm_provider"].lower() == "dashscope" or
              self.config["llm_provider"].lower() == "alibaba" or
              "dashscope" in self.config["llm_provider"].lower() or
              "阿里百炼" in self.config["llm_provider"]):
            self.deep_thinking_llm = ChatDashScope(
                model=self.config["deep_think_llm"],
                temperature=0.1,
                max_tokens=2000
            )
            self.quick_thinking_llm = ChatDashScope(
                model=self.config["quick_think_llm"],
                temperature=0.1,
                max_tokens=2000
            )
            # 为ReAct Agent创建Tongyi LLM（支持工具调用）
            from langchain_community.llms import Tongyi
            self.react_llm = Tongyi()
            # 确保使用正确的通义千问模型名称
            quick_model = self.config["quick_think_llm"]
            if quick_model in ["gpt-4o-mini", "o4-mini"]:  # 如果还是默认的OpenAI模型名
                quick_model = "qwen-turbo"  # 使用通义千问默认模型
            self.react_llm.model_name = quick_model
            print(f"📊 [DEBUG] ReAct LLM模型设置为: {quick_model}")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config['llm_provider']}")
        
        self.toolkit = Toolkit(config=self.config)

        # Initialize memories (如果启用)
        memory_enabled = self.config.get("memory_enabled", True)
        if memory_enabled:
            self.bull_memory = FinancialSituationMemory("bull_memory", self.config)
            self.bear_memory = FinancialSituationMemory("bear_memory", self.config)
            self.trader_memory = FinancialSituationMemory("trader_memory", self.config)
            self.invest_judge_memory = FinancialSituationMemory("invest_judge_memory", self.config)
            self.risk_manager_memory = FinancialSituationMemory("risk_manager_memory", self.config)
        else:
            # 创建空的内存对象
            self.bull_memory = None
            self.bear_memory = None
            self.trader_memory = None
            self.invest_judge_memory = None
            self.risk_manager_memory = None

        # Create tool nodes
        self.tool_nodes = self._create_tool_nodes()

        # Initialize components
        self.conditional_logic = ConditionalLogic()
        self.graph_setup = GraphSetup(
            self.quick_thinking_llm,
            self.deep_thinking_llm,
            self.toolkit,
            self.tool_nodes,
            self.bull_memory,
            self.bear_memory,
            self.trader_memory,
            self.invest_judge_memory,
            self.risk_manager_memory,
            self.conditional_logic,
            self.config,
            getattr(self, 'react_llm', None),
        )

        self.propagator = Propagator()
        self.reflector = Reflector(self.quick_thinking_llm)
        self.signal_processor = SignalProcessor(self.quick_thinking_llm)

        # State tracking
        self.curr_state = None
        self.ticker = None
        self.log_states_dict = {}  # date to full state dict

        # Set up the graph
        self.graph = self.graph_setup.setup_graph(selected_analysts)

    def _create_tool_nodes(self) -> Dict[str, ToolNode]:
        """Create tool nodes for different data sources."""
        return {
            "market": ToolNode(
                [
                    # online tools
                    self.toolkit.get_YFin_data_online,
                    self.toolkit.get_stockstats_indicators_report_online,
                    # 中国股票专用工具
                    self.toolkit.get_china_stock_data,
                    # offline tools
                    self.toolkit.get_YFin_data,
                    self.toolkit.get_stockstats_indicators_report,
                ]
            ),
            "social": ToolNode(
                [
                    # online tools
                    self.toolkit.get_stock_news_openai,
                    # offline tools
                    self.toolkit.get_reddit_stock_info,
                ]
            ),
            "news": ToolNode(
                [
                    # online tools
                    self.toolkit.get_global_news_openai,
                    self.toolkit.get_google_news,
                    # offline tools
                    self.toolkit.get_finnhub_news,
                    self.toolkit.get_reddit_news,
                ]
            ),
            "fundamentals": ToolNode(
                [
                    # online tools
                    self.toolkit.get_fundamentals_openai,
                    # 中国股票专用工具
                    self.toolkit.get_china_stock_data,
                    self.toolkit.get_china_fundamentals,
                    # offline tools
                    self.toolkit.get_finnhub_company_insider_sentiment,
                    self.toolkit.get_finnhub_company_insider_transactions,
                    self.toolkit.get_simfin_balance_sheet,
                    self.toolkit.get_simfin_cashflow,
                    self.toolkit.get_simfin_income_stmt,
                ]
            ),
        }

    def propagate(self, company_name, trade_date):
        """Run the trading agents graph for a company on a specific date."""
        # 使用绝对路径创建调试文件
        debug_file = os.path.join(self.config["project_dir"], 'propagate_debug.txt')
        
        with open(debug_file, "a", encoding='utf-8') as f:
            f.write("\n=== Starting propagate ===\n")
            f.write(f"Current working directory: {os.getcwd()}\n")
            f.write(f"Debug file location: {debug_file}\n")
            f.write(f"Company name: {company_name}\n")
            f.write(f"Trade date: {trade_date}\n")

        self.ticker = company_name

        # Initialize state
        with open(debug_file, "a", encoding='utf-8') as f:
            f.write("Creating initial state...\n")

        # Initialize state
        init_agent_state = self.propagator.create_initial_state(
            company_name, trade_date
        )
        args = self.propagator.get_graph_args()

        if self.debug:
            # Debug mode with tracing
            trace = []
            for chunk in self.graph.stream(init_agent_state, **args):
                if len(chunk["messages"]) == 0:
                    pass
                else:
                    chunk["messages"][-1].pretty_print()
                    trace.append(chunk)

            final_state = trace[-1]
        else:
            # Standard mode without tracing
            final_state = self.graph.invoke(init_agent_state, **args)

        # Store current state for reflection
        self.curr_state = final_state

        # Log state
        self._log_state(trade_date, final_state)

       # Generate web report
        with open(debug_file, "a", encoding='utf-8') as f:
            f.write("Starting web report generation...\n")
        self._generate_web_report(trade_date, final_state)
        with open(debug_file, "a", encoding='utf-8') as f:
            f.write("Web report generation completed\n")


        # Return decision and processed signal
        return final_state, self.process_signal(final_state["final_trade_decision"], company_name)



    def _log_state(self, trade_date, final_state):
        """Log the final state to a JSON file."""
        self.log_states_dict[str(trade_date)] = {
            "company_of_interest": final_state["company_of_interest"],
            "trade_date": final_state["trade_date"],
            "market_report": final_state["market_report"],
            "sentiment_report": final_state["sentiment_report"],
            "news_report": final_state["news_report"],
            "fundamentals_report": final_state["fundamentals_report"],
            "investment_debate_state": {
                "bull_history": final_state["investment_debate_state"]["bull_history"],
                "bear_history": final_state["investment_debate_state"]["bear_history"],
                "history": final_state["investment_debate_state"]["history"],
                "current_response": final_state["investment_debate_state"][
                    "current_response"
                ],
                "judge_decision": final_state["investment_debate_state"][
                    "judge_decision"
                ],
            },
            "trader_investment_decision": final_state["trader_investment_plan"],
            "risk_debate_state": {
                "risky_history": final_state["risk_debate_state"]["risky_history"],
                "safe_history": final_state["risk_debate_state"]["safe_history"],
                "neutral_history": final_state["risk_debate_state"]["neutral_history"],
                "history": final_state["risk_debate_state"]["history"],
                "judge_decision": final_state["risk_debate_state"]["judge_decision"],
            },
            "investment_plan": final_state["investment_plan"],
            "final_trade_decision": final_state["final_trade_decision"],
        }

        # Save to file
        directory = Path(f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/")
        directory.mkdir(parents=True, exist_ok=True)

        with open(
            f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/full_states_log.json",
            "w",
        ) as f:
            json.dump(self.log_states_dict, f, indent=4)

    def _generate_markdown_report(self, trade_date: str, state: Dict[str, Any]) -> str:
        """Generate a markdown format report from the trading state."""
        md_content = f"""# {state.get('company_of_interest', 'Unknown Company')} 交易分析报告

## 基本信息
- 交易日期：{trade_date}
- 市场类型：{"A股市场" if get_market_type() == "CN" else "美股市场"}

## 市场分析
{state.get('market_report', '市场分析数据未获取')}

## 基本面分析
{state.get('fundamentals_report', '基本面分析数据未获取')}

## 情绪分析
{state.get('sentiment_report', '情绪分析数据未获取')}

## 新闻分析
{state.get('news_report', '新闻分析数据未获取')}

## 投资辩论
### 多方观点
{state.get('investment_debate_state', {}).get('bull_history', '多方观点未获取')}

### 空方观点
{state.get('investment_debate_state', {}).get('bear_history', '空方观点未获取')}

### 辩论历史
{state.get('investment_debate_state', {}).get('history', '辩论历史未获取')}

### 评判决策
{state.get('investment_debate_state', {}).get('judge_decision', '评判决策未获取')}

## 交易员投资决策
{state.get('trader_investment_plan', '交易员投资决策未获取')}

## 风险辩论
### 激进方观点
{state.get('risk_debate_state', {}).get('risky_history', '激进方观点未获取')}

### 保守方观点
{state.get('risk_debate_state', {}).get('safe_history', '保守方观点未获取')}

### 中立方观点
{state.get('risk_debate_state', {}).get('neutral_history', '中立方观点未获取')}

### 风险辩论历史
{state.get('risk_debate_state', {}).get('history', '风险辩论历史未获取')}

### 风险评判决策
{state.get('risk_debate_state', {}).get('judge_decision', '风险评判决策未获取')}

## 投资计划
{state.get('investment_plan', '投资计划未生成')}

## 最终决策
{state.get('final_trade_decision', '最终决策未生成')}
"""
        return md_content

    def _generate_web_report(self, trade_date: str, state: Dict[str, Any]) -> None:
        """Generate a web-based report from the trading state."""
        # 使用绝对路径创建调试文件
        debug_file = os.path.join(self.config["project_dir"], 'report_debug.txt')
        
        # 直接写入文件来跟踪执行
        with open(debug_file, "a", encoding='utf-8') as f:
            f.write("\n=== Starting _generate_web_report ===\n")
            f.write(f"Current working directory: {os.getcwd()}\n")
            f.write(f"Debug file location: {debug_file}\n")
            f.write(f"trade_date: {trade_date}\n")
            if state:
                f.write("State keys: " + ", ".join(state.keys()) + "\n")
            else:
                f.write("State is None or empty\n")
        
        try:
            if not state:
                with open(debug_file, "a", encoding='utf-8') as f:
                    f.write("Early return: state is empty\n")
                return
                
            # Create reports directory
            reports_dir = os.path.join(self.config["project_dir"], "reports")
            with open(debug_file, "a", encoding='utf-8') as f:
                f.write(f"Reports directory path: {reports_dir}\n")
            
            os.makedirs(reports_dir, exist_ok=True)
            
            # Generate markdown report
            md_content = self._generate_markdown_report(trade_date, state)
            md_file = os.path.join(
                reports_dir, 
                f"report_{state.get('company_of_interest', 'unknown')}_{trade_date}.md"
            )
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(md_content)
            
            # Load HTML template
            template_dir = os.path.join(self.config["project_dir"], "templates")
            with open(debug_file, "a", encoding='utf-8') as f:
                f.write(f"Template directory path: {template_dir}\n")
            
            template_loader = jinja2.FileSystemLoader(searchpath=template_dir)
            template_env = jinja2.Environment(loader=template_loader)
            
            try:
                template = template_env.get_template("report_template.html")
                with open(debug_file, "a", encoding='utf-8') as f:
                    f.write("Successfully loaded template\n")
            except Exception as e:
                with open(debug_file, "a", encoding='utf-8') as f:
                    f.write(f"Failed to load template: {str(e)}\n")
                raise
            
            # Prepare report data
            market_type = get_market_type()
            with open(debug_file, "a", encoding='utf-8') as f:
                f.write(f"Market type: {market_type}\n")
            
            # Check required fields
            required_fields = [
                "company_of_interest",
                "market_report",
                "fundamentals_report",
                "sentiment_report",
                "news_report",
                "investment_debate_state",
                "trader_investment_plan",
                "risk_debate_state",
                "investment_plan",
                "final_trade_decision"
            ]
            
            missing_fields = [field for field in required_fields if field not in state]
            with open(debug_file, "a", encoding='utf-8') as f:
                if missing_fields:
                    f.write(f"Missing fields: {', '.join(missing_fields)}\n")
                else:
                    f.write("All required fields present\n")
            
            # 准备投资辩论状态
            investment_debate_state = state.get("investment_debate_state", {})
            if not isinstance(investment_debate_state, dict):
                investment_debate_state = {}
            
            # 准备风险辩论状态
            risk_debate_state = state.get("risk_debate_state", {})
            if not isinstance(risk_debate_state, dict):
                risk_debate_state = {}
            
            report_data = {
                "trade_date": trade_date,
                "company": state.get("company_of_interest", "Unknown Company"),
                "market_type": "A股市场" if market_type == "CN" else "美股市场",
                "market_analysis": state.get("market_report", "市场分析数据未获取"),
                "fundamental_analysis": state.get("fundamentals_report", "基本面分析数据未获取"),
                "sentiment_analysis": state.get("sentiment_report", "情绪分析数据未获取"),
                "news_analysis": state.get("news_report", "新闻分析数据未获取"),
                # 投资辩论状态
                "investment_debate_state": {
                    "bull_history": investment_debate_state.get("bull_history", "多方观点未获取"),
                    "bear_history": investment_debate_state.get("bear_history", "空方观点未获取"),
                    "history": investment_debate_state.get("history", "辩论历史未获取"),
                    "current_response": investment_debate_state.get("current_response", "当前回应未获取"),
                    "judge_decision": investment_debate_state.get("judge_decision", "评判决策未获取")
                },
                # 交易员投资决策
                "trader_investment_decision": state.get("trader_investment_plan", "交易员投资决策未获取"),
                # 风险辩论状态
                "risk_debate_state": {
                    "risky_history": risk_debate_state.get("risky_history", "激进方观点未获取"),
                    "safe_history": risk_debate_state.get("safe_history", "保守方观点未获取"),
                    "neutral_history": risk_debate_state.get("neutral_history", "中立方观点未获取"),
                    "history": risk_debate_state.get("history", "风险辩论历史未获取"),
                    "judge_decision": risk_debate_state.get("judge_decision", "风险评判决策未获取")
                },
                "investment_plan": state.get("investment_plan", "投资计划未生成"),
                "final_decision": state.get("final_trade_decision", "最终决策未生成"),
                "markdown_content": md_content  # 添加Markdown内容用于导出
            }
            
            with open(debug_file, "a", encoding='utf-8') as f:
                f.write(f"Prepared report data for company: {report_data['company']}\n")
            
            # Generate HTML
            try:
                html_output = template.render(**report_data)
                with open(debug_file, "a", encoding='utf-8') as f:
                    f.write("Successfully rendered HTML template\n")
            except Exception as e:
                with open(debug_file, "a", encoding='utf-8') as f:
                    f.write(f"Failed to render template: {str(e)}\n")
                raise
            
            # Save report
            report_file = os.path.join(
                reports_dir, 
                f"report_{state.get('company_of_interest', 'unknown')}_{trade_date}.html"
            )
            with open(debug_file, "a", encoding='utf-8') as f:
                f.write(f"Saving report to: {report_file}\n")
            
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(html_output)
            with open(debug_file, "a", encoding='utf-8') as f:
                f.write("Successfully saved report file\n")
            
            # Open in browser if not in debug mode
            if not self.debug:
                with open(debug_file, "a", encoding='utf-8') as f:
                    f.write("Attempting to open report in browser\n")
                try:
                    webbrowser.open(f"file://{os.path.abspath(report_file)}")
                    with open(debug_file, "a", encoding='utf-8') as f:
                        f.write("Successfully opened report in browser\n")
                except Exception as e:
                    with open(debug_file, "a", encoding='utf-8') as f:
                        f.write(f"Failed to open report in browser: {str(e)}\n")
            else:
                with open(debug_file, "a", encoding='utf-8') as f:
                    f.write("Debug mode enabled, skipping browser opening\n")
                
        except Exception as e:
            with open(debug_file, "a", encoding='utf-8') as f:
                f.write(f"Error in report generation: {str(e)}\n")
            raise


    def reflect_and_remember(self, returns_losses):
        """Reflect on decisions and update memory based on returns."""
        self.reflector.reflect_bull_researcher(
            self.curr_state, returns_losses, self.bull_memory
        )
        self.reflector.reflect_bear_researcher(
            self.curr_state, returns_losses, self.bear_memory
        )
        self.reflector.reflect_trader(
            self.curr_state, returns_losses, self.trader_memory
        )
        self.reflector.reflect_invest_judge(
            self.curr_state, returns_losses, self.invest_judge_memory
        )
        self.reflector.reflect_risk_manager(
            self.curr_state, returns_losses, self.risk_manager_memory
        )

    def process_signal(self, full_signal, stock_symbol=None):
        """Process a signal to extract the core decision."""
        return self.signal_processor.process_signal(full_signal, stock_symbol)
