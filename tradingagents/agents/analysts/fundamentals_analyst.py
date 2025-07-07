from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
import time
import json


def create_fundamentals_analyst_react(llm, toolkit):
    """使用ReAct Agent模式的基本面分析师（适用于通义千问）"""
    def fundamentals_analyst_react_node(state):
        print(f"📊 [DEBUG] ===== ReAct基本面分析师节点开始 =====")

        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        print(f"📊 [DEBUG] 输入参数: ticker={ticker}, date={current_date}")

        # 检查是否为中国股票
        def is_china_stock(ticker_code):
            import re
            return re.match(r'^\d{6}$', str(ticker_code))

        is_china = is_china_stock(ticker)
        print(f"📊 [DEBUG] 股票类型检查: {ticker} -> 中国A股: {is_china}")

        if toolkit.config["online_tools"]:
            # 在线模式，使用ReAct Agent
            from langchain_core.tools import BaseTool

            if is_china:
                print(f"📊 [基本面分析师] 使用ReAct Agent分析中国股票")

                class ChinaStockDataTool(BaseTool):
                    name: str = "get_china_stock_data"
                    description: str = f"获取中国A股股票{ticker}的实时和历史数据。直接调用，无需参数。"
                    def _run(self, query: str = "") -> str:
                        try:
                            print(f"📊 [DEBUG] ChinaStockDataTool调用，股票代码: {ticker}")
                    #         return toolkit.get_china_stock_data.invoke({
                    #             'stock_code': ticker,
                    #             'start_date': '2025-05-28',
                    #             'end_date': current_date
                    #         })
                    #     except Exception as e:
                    #         return f"获取股票数据失败: {str(e)}"
                            # 使用优化的缓存数据获取
                            from tradingagents.dataflows.optimized_china_data import get_china_stock_data_cached
                            return get_china_stock_data_cached(
                                symbol=ticker,
                                start_date='2025-05-28',
                                end_date=current_date,
                                force_refresh=False
                            )
                        except Exception as e:
                            print(f"❌ 优化A股数据获取失败: {e}")
                            # 备用方案：使用原始API
                            try:
                                return toolkit.get_china_stock_data.invoke({
                                    'stock_code': ticker,
                                    'start_date': '2025-05-28',
                                    'end_date': current_date
                                })
                            except Exception as e2:
                                return f"获取股票数据失败: {str(e2)}"


                class ChinaFundamentalsTool(BaseTool):
                    name: str = "get_china_fundamentals"
                    # description: str = f"获取中国A股股票{ticker}的基本面分析。直接调用，无需参数。"

                    # def _run(self, query: str = "") -> str:
                    #     try:
                    #         print(f"📊 [DEBUG] ChinaFundamentalsTool调用，股票代码: {ticker}")
                    #         return toolkit.get_china_fundamentals.invoke({
                    #             'ticker': ticker,
                    #             'curr_date': current_date
                    #         })
                    #     except Exception as e:
                    #         return f"获取基本面数据失败: {str(e)}"

                    description: str = f"获取中国A股股票{ticker}的基本面分析（优化缓存版本）。直接调用，无需参数。"

                    def _run(self, query: str = "") -> str:
                        try:
                            print(f"📊 [DEBUG] ChinaFundamentalsTool调用，股票代码: {ticker}")
                            # 使用优化的缓存基本面数据获取
                            from tradingagents.dataflows.optimized_china_data import get_china_fundamentals_cached
                            return get_china_fundamentals_cached(
                                symbol=ticker,
                                force_refresh=False
                            )
                        except Exception as e:
                            print(f"❌ 优化A股基本面数据获取失败: {e}")
                            # 备用方案：使用原始API
                            try:
                                return toolkit.get_china_fundamentals.invoke({
                                    'ticker': ticker,
                                    'curr_date': current_date
                                })
                            except Exception as e2:
                                return f"获取基本面数据失败: {str(e2)}"



                tools = [ChinaStockDataTool(), ChinaFundamentalsTool()]
                query = f"""请对中国A股股票{ticker}进行详细的基本面分析。

执行步骤：
1. 使用get_china_stock_data工具获取股票市场数据
2. 使用get_china_fundamentals工具获取基本面数据
3. 基于获取的真实数据进行深入的基本面分析
4. 直接输出完整的基本面分析报告内容

重要要求：
- 必须输出完整的基本面分析报告内容，不要只是描述报告已完成
- 报告必须基于工具获取的真实数据进行分析
- 报告长度不少于800字
- 包含具体的财务数据、比率和专业分析

报告格式应包含：
## 公司基本信息
## 财务状况分析
## 盈利能力分析
## 成长性分析
## 估值分析
## 投资建议"""
            else:
                print(f"📊 [基本面分析师] 使用ReAct Agent分析美股/港股")

                class USStockDataTool(BaseTool):
                    name: str = "get_us_stock_data"
                    description: str = f"获取美股/港股{ticker}的市场数据（通过FINNHUB API）。直接调用，无需参数。"

                    def _run(self, query: str = "") -> str:
                        try:
                            print(f"📊 [DEBUG] USStockDataTool调用，股票代码: {ticker}")
                            # return toolkit.get_YFin_data_online.invoke({
                            #     'symbol': ticker,
                            #     'start_date': '2025-05-28',
                            #     'end_date': current_date
                            # })
                            # 使用优化的缓存数据获取
                            from tradingagents.dataflows.optimized_us_data import get_us_stock_data_cached
                            return get_us_stock_data_cached(
                                symbol=ticker,
                                start_date='2025-05-28',
                                end_date=current_date,
                                force_refresh=False
                            )
                        except Exception as e:
                            # return f"获取股票数据失败: {str(e)}"
                            print(f"❌ 优化美股数据获取失败: {str(e)}")
                            # 备用方案：使用原始API
                            try:
                                return toolkit.get_YFin_data_online.invoke({
                                    'symbol': ticker,
                                    'start_date': '2025-05-28',
                                    'end_date': current_date
                                })
                            except Exception as e2:
                                return f"获取股票数据失败: {str(e2)}"

                class USFundamentalsTool(BaseTool):
                    name: str = "get_us_fundamentals"
                    description: str = f"获取美股/港股{ticker}的基本面数据（通过OpenAI新闻API）。直接调用，无需参数。"

                    def _run(self, query: str = "") -> str:
                        try:
                            print(f"📊 [DEBUG] USFundamentalsTool调用，股票代码: {ticker}")
                            return toolkit.get_fundamentals_openai.invoke({
                                'ticker': ticker,
                                'curr_date': current_date
                            })
                        except Exception as e:
                            return f"获取基本面数据失败: {str(e)}"

                class FinnhubNewsTool(BaseTool):
                    name: str = "get_finnhub_news"
                    description: str = f"获取美股{ticker}的最新新闻（通过FINNHUB API）。直接调用，无需参数。"

                    def _run(self, query: str = "") -> str:
                        try:
                            print(f"📊 [DEBUG] FinnhubNewsTool调用，股票代码: {ticker}")
                            return toolkit.get_finnhub_news.invoke({
                                'ticker': ticker,
                                'start_date': '2025-05-28',
                                'end_date': current_date
                            })
                        except Exception as e:
                            return f"获取新闻数据失败: {str(e)}"

                tools = [USStockDataTool(), USFundamentalsTool(), FinnhubNewsTool()]
                query = f"""请对美股{ticker}进行详细的基本面分析。

执行步骤：
1. 使用get_us_stock_data工具获取股票市场数据（通过FINNHUB API）
2. 使用get_us_fundamentals工具获取基本面数据（通过OpenAI新闻API）
3. 使用get_finnhub_news工具获取最新新闻和公司动态
4. 基于获取的真实数据进行深入的基本面分析
5. 直接输出完整的基本面分析报告内容

重要要求：
- 必须输出完整的基本面分析报告内容，不要只是描述报告已完成
- 报告必须基于工具获取的真实数据进行分析
- 报告长度不少于800字
- 包含具体的财务数据、比率和专业分析
- 结合新闻信息分析公司基本面变化

报告格式应包含：
## 公司基本信息
## 财务状况分析
## 盈利能力分析
## 成长性分析
## 新闻和公司动态分析
## 估值分析
## 投资建议"""

            try:
                # 创建ReAct Agent
                prompt = hub.pull("hwchase17/react")
                agent = create_react_agent(llm, tools, prompt)
                agent_executor = AgentExecutor(
                    agent=agent,
                    tools=tools,
                    verbose=True,
                    handle_parsing_errors=True,
                    max_iterations=10,  # 增加到10次迭代，因为基本面分析需要调用多个工具
                    max_execution_time=180,  # 增加到3分钟，给更多时间生成详细报告
                    return_intermediate_steps=True  # 返回中间步骤，便于调试
                )



                print(f"📊 [DEBUG] 执行ReAct Agent查询...")
                result = agent_executor.invoke({'input': query})

                report = result['output']
                print(f"📊 [基本面分析师] ReAct Agent完成，报告长度: {len(report)}")

                # 检查是否包含格式错误信息
                if "Invalid Format" in report or "Missing 'Action:'" in report:
                    print(f"⚠️ [DEBUG] 检测到格式错误，但Agent已处理")
                    print(f"📊 [DEBUG] 中间步骤数量: {len(result.get('intermediate_steps', []))}")

            except Exception as e:
                print(f"❌ [DEBUG] ReAct Agent失败: {str(e)}")
                print(f"📊 [DEBUG] 错误类型: {type(e).__name__}")
                if hasattr(e, 'args') and e.args:
                    print(f"📊 [DEBUG] 错误详情: {e.args}")
                report = f"ReAct Agent基本面分析失败: {str(e)}"
        else:
            # 离线模式，使用原有逻辑
            report = "离线模式，暂不支持"

        print(f"📊 [DEBUG] ===== ReAct基本面分析师节点结束 =====")

        return {
            "messages": [("assistant", report)],
            "fundamentals_report": report,
        }

    return fundamentals_analyst_react_node


def create_fundamentals_analyst(llm, toolkit):
    def fundamentals_analyst_node(state):
        print(f"📊 [DEBUG] ===== 基本面分析师节点开始 =====")

        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        print(f"📊 [DEBUG] 输入参数: ticker={ticker}, date={current_date}")
        print(f"📊 [DEBUG] 当前状态中的消息数量: {len(state.get('messages', []))}")
        print(f"📊 [DEBUG] 现有基本面报告: {state.get('fundamentals_report', 'None')[:100]}...")

        # 根据股票代码格式选择数据源
        def is_china_stock(ticker_code):
            """判断是否为中国A股代码"""
            import re
            # A股代码格式：6位数字
            return re.match(r'^\d{6}$', str(ticker_code))

        print(f"📊 [基本面分析师] 正在分析股票: {ticker}")

        # 检查股票类型
        is_china = is_china_stock(ticker)
        print(f"📊 [DEBUG] 股票类型检查: {ticker} -> 中国A股: {is_china}")

        print(f"📊 [DEBUG] 工具配置检查: online_tools={toolkit.config['online_tools']}")

        if toolkit.config["online_tools"]:
            if is_china:
                # 中国A股使用专门的通达信基本面分析
                print(f"📊 [基本面分析师] 检测到A股代码，使用通达信基本面分析")
                tools = [
                    toolkit.get_china_stock_data,
                    toolkit.get_china_fundamentals
                ]
                print(f"📊 [DEBUG] 选择的工具: {[tool.name for tool in tools]}")
            else:
                # 美股和港股使用OpenAI基本面分析
                print(f"📊 [基本面分析师] 检测到非A股代码，使用OpenAI数据源")
                tools = [toolkit.get_fundamentals_openai]
                print(f"📊 [DEBUG] 选择的工具: {[tool.name for tool in tools]}")
        else:
            tools = [
                toolkit.get_finnhub_company_insider_sentiment,
                toolkit.get_finnhub_company_insider_transactions,
                toolkit.get_simfin_balance_sheet,
                toolkit.get_simfin_cashflow,
                toolkit.get_simfin_income_stmt,
            ]

        # 根据股票类型调整系统提示
        if is_china_stock(ticker):
            system_message = (
                f"你是一位专业的中国A股基本面分析师。"
                ""
                f"⚠️ 绝对强制要求：你必须调用工具获取真实数据！不允许任何假设或编造！"
                ""
                f"任务：分析股票代码 {ticker}"
                ""
                f"🔴 第一步：立即调用 get_china_stock_data 工具"
                f"参数：stock_code='{ticker}', start_date='2025-05-28', end_date='{current_date}'"
                ""
                f"🔴 第二步：立即调用 get_china_fundamentals 工具"
                f"参数：ticker='{ticker}', curr_date='{current_date}'"
                ""
                "📊 分析要求："
                "- 基于真实财务数据进行深度估值分析"
                "- 计算并提供合理价位区间（使用人民币¥）"
                "- 分析当前股价是否被低估或高估"
                "- 提供基于基本面的目标价位建议"
                "- 包含PE、PB、PEG等估值指标分析"
                "- 结合行业平均估值水平进行对比"
                ""
                "🚫 严格禁止："
                "- 不允许说'我将调用工具'"
                "- 不允许假设任何数据"
                "- 不允许编造公司信息"
                "- 不允许直接回答而不调用工具"
                "- 不允许回复'无法确定价位'或'需要更多信息'"
                ""
                "✅ 你必须："
                "- 立即调用工具"
                "- 等待工具返回真实数据"
                "- 基于真实数据进行分析"
                "- 提供具体的价位区间和目标价"
                ""
                "现在立即开始调用工具！不要说任何其他话！"
            )
        else:
            system_message = (
                "你是一位研究员，负责分析公司过去一周的基本面信息。请撰写一份关于公司基本面信息的综合报告，包括财务文件、公司概况、基本公司财务、公司财务历史、内部人情绪和内部人交易，以全面了解公司的基本面信息来为交易者提供信息。确保包含尽可能多的细节。不要简单地说趋势是混合的，提供详细和细粒度的分析和见解，可能帮助交易者做出决策。"
                + "📊 估值分析要求：基于财务数据计算合理估值区间，提供目标价位建议（使用美元$），包含PE、PB、DCF等估值方法分析，不允许回复'无法确定价位'。"
                + "确保在报告末尾附加一个Markdown表格来组织报告中的要点，使其有组织且易于阅读。请确保所有分析都使用中文。"
            )

        # 根据股票类型使用不同的系统提示
        if is_china_stock(ticker):
            # 中国股票使用强制工具调用的提示
            system_prompt = (
                "🔴 强制要求：你必须调用工具获取真实数据！"
                "🚫 绝对禁止：不允许假设、编造或直接回答任何问题！"
                "✅ 你必须：立即调用提供的工具获取真实数据，然后基于真实数据进行分析。"
                "可用工具：{tool_names}。\n{system_message}"
                "当前日期：{current_date}。分析目标：{ticker}。"
            )
        else:
            # 非中国股票使用原有的提示
            system_prompt = (
                "你是一位有用的AI助手，与其他助手协作。"
                "使用提供的工具来回答问题。"
                "如果你无法完全回答，没关系；另一位具有不同工具的助手"
                "将从你停下的地方继续帮助。执行你能做的来取得进展。"
                "如果你或任何其他助手有最终交易建议：**买入/持有/卖出**或可交付成果，"
                "请在你的回复前加上'最终交易建议：**买入/持有/卖出**'，这样团队就知道要停止了。"
                "你可以使用以下工具：{tool_names}。\n{system_message}"
                "供你参考，当前日期是{current_date}。我们要分析的公司是{ticker}。请确保所有分析都使用中文。"
            )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        print(f"📊 [DEBUG] 创建LLM链，工具数量: {len(tools)}")

        # 对于中国股票，强制要求调用第一个工具
        if is_china_stock(ticker):
            print(f"📊 [DEBUG] 中国股票：尝试强制工具调用")
            # 尝试强制调用第一个工具
            try:
                chain = prompt | llm.bind_tools(tools, tool_choice="any")
            except:
                # 如果不支持tool_choice，使用普通绑定
                chain = prompt | llm.bind_tools(tools)
        else:
            chain = prompt | llm.bind_tools(tools)

        print(f"📊 [DEBUG] 调用LLM链...")
        result = chain.invoke(state["messages"])

        print(f"📊 [DEBUG] LLM调用完成")
        print(f"📊 [DEBUG] 结果类型: {type(result)}")
        print(f"📊 [DEBUG] 工具调用数量: {len(result.tool_calls) if hasattr(result, 'tool_calls') else 0}")
        print(f"📊 [DEBUG] 内容长度: {len(result.content) if hasattr(result, 'content') else 0}")

        # 处理基本面分析报告
        if len(result.tool_calls) == 0:
            # 对于中国股票，如果LLM没有调用工具，我们手动调用工具
            if is_china_stock(ticker):
                print(f"📊 [DEBUG] 中国股票但LLM未调用工具，手动调用工具...")

                try:
                    # 手动调用第一个工具：get_china_stock_data
                    print(f"📊 [DEBUG] 手动调用 get_china_stock_data...")
                    stock_data_result = toolkit.get_china_stock_data.invoke({
                        'stock_code': ticker,
                        'start_date': '2025-05-28',
                        'end_date': current_date
                    })
                    print(f"📊 [DEBUG] get_china_stock_data 结果长度: {len(stock_data_result)}")

                    # 手动调用第二个工具：get_china_fundamentals
                    print(f"📊 [DEBUG] 手动调用 get_china_fundamentals...")
                    fundamentals_result = toolkit.get_china_fundamentals.invoke({
                        'ticker': ticker,
                        'curr_date': current_date
                    })
                    print(f"📊 [DEBUG] get_china_fundamentals 结果长度: {len(fundamentals_result)}")

                    # 合并工具结果生成最终报告
                    report = f"""# 中国A股基本面分析报告 - {ticker}

## 股票数据分析
{stock_data_result}

## 基本面深度分析
{fundamentals_result}

## 分析总结
基于通达信数据源的真实数据分析完成。以上信息来自官方数据源，确保准确性和时效性。
"""
                    print(f"📊 [基本面分析师] 手动工具调用完成，生成报告长度: {len(report)}")

                except Exception as e:
                    print(f"❌ [DEBUG] 手动工具调用失败: {str(e)}")
                    report = f"基本面分析失败：{str(e)}"
            else:
                # 非中国股票，直接使用LLM的回复
                report = result.content
                print(f"📊 [基本面分析师] 生成最终报告，长度: {len(report)}")
        else:
            # 有工具调用，先返回工具调用信息，等待工具执行
            report = state.get("fundamentals_report", "")  # 保持现有报告
            print(f"📊 [基本面分析师] 工具调用: {[call.get('name', 'unknown') for call in result.tool_calls]}")
            for i, call in enumerate(result.tool_calls):
                print(f"📊 [DEBUG] 工具调用 {i+1}: {call}")

        print(f"📊 [DEBUG] 返回状态: fundamentals_report长度={len(report)}")
        print(f"📊 [DEBUG] ===== 基本面分析师节点结束 =====")

        return {
            "messages": [result],
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node
