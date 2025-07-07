"""
股票分析执行工具
"""

import sys
import os
import uuid
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 确保环境变量正确加载
load_dotenv(project_root / ".env", override=True)

# 添加配置管理器
try:
    from tradingagents.config.config_manager import token_tracker
    TOKEN_TRACKING_ENABLED = True
except ImportError:
    TOKEN_TRACKING_ENABLED = False
    print("⚠️ Token跟踪功能未启用")

def extract_risk_assessment(state):
    """从分析状态中提取风险评估数据"""
    try:
        risk_debate_state = state.get('risk_debate_state', {})

        if not risk_debate_state:
            return None

        # 提取各个风险分析师的观点
        risky_analysis = risk_debate_state.get('risky_history', '')
        safe_analysis = risk_debate_state.get('safe_history', '')
        neutral_analysis = risk_debate_state.get('neutral_history', '')
        judge_decision = risk_debate_state.get('judge_decision', '')

        # 格式化风险评估报告
        risk_assessment = f"""
## ⚠️ 风险评估报告

### 🔴 激进风险分析师观点
{risky_analysis if risky_analysis else '暂无激进风险分析'}

### 🟡 中性风险分析师观点
{neutral_analysis if neutral_analysis else '暂无中性风险分析'}

### 🟢 保守风险分析师观点
{safe_analysis if safe_analysis else '暂无保守风险分析'}

### 🏛️ 风险管理委员会最终决议
{judge_decision if judge_decision else '暂无风险管理决议'}

---
*风险评估基于多角度分析，请结合个人风险承受能力做出投资决策*
        """.strip()

        return risk_assessment

    except Exception as e:
        print(f"提取风险评估数据时出错: {e}")
        return None

def run_stock_analysis(stock_symbol, analysis_date, analysts, research_depth, llm_provider, llm_model, market_type="美股", progress_callback=None):
    """执行股票分析

    Args:
        stock_symbol: 股票代码
        analysis_date: 分析日期
        analysts: 分析师列表
        research_depth: 研究深度
        llm_provider: LLM提供商 (dashscope/google)
        llm_model: 大模型名称
        progress_callback: 进度回调函数，用于更新UI状态
    """

    def update_progress(message, step=None, total_steps=None):
        """更新进度"""
        if progress_callback:
            progress_callback(message, step, total_steps)
        print(f"[进度] {message}")

    update_progress("开始股票分析...")

    # 生成会话ID用于Token跟踪
    session_id = f"analysis_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # 估算Token使用（用于成本预估）
    if TOKEN_TRACKING_ENABLED:
        estimated_input = 2000 * len(analysts)  # 估算每个分析师2000个输入token
        estimated_output = 1000 * len(analysts)  # 估算每个分析师1000个输出token
        estimated_cost = token_tracker.estimate_cost(llm_provider, llm_model, estimated_input, estimated_output)

        update_progress(f"预估分析成本: ¥{estimated_cost:.4f}")

    # 验证环境变量
    update_progress("检查环境变量配置...")
    dashscope_key = os.getenv("DASHSCOPE_API_KEY")
    finnhub_key = os.getenv("FINNHUB_API_KEY")

    print(f"环境变量检查:")
    print(f"  DASHSCOPE_API_KEY: {'已设置' if dashscope_key else '未设置'}")
    print(f"  FINNHUB_API_KEY: {'已设置' if finnhub_key else '未设置'}")

    if not dashscope_key:
        raise ValueError("DASHSCOPE_API_KEY 环境变量未设置")
    if not finnhub_key:
        raise ValueError("FINNHUB_API_KEY 环境变量未设置")

    update_progress("环境变量验证通过")

    try:
        # 导入必要的模块
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG

        # 创建配置
        update_progress("配置分析参数...")
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = llm_provider
        config["deep_think_llm"] = llm_model
        config["quick_think_llm"] = llm_model
        # 根据研究深度调整配置
        if research_depth == 1:  # 1级 - 快速分析
            config["max_debate_rounds"] = 1
            config["max_risk_discuss_rounds"] = 1
            config["memory_enabled"] = False  # 禁用记忆功能加速
            config["online_tools"] = False  # 使用缓存数据加速
            if llm_provider == "dashscope":
                config["quick_think_llm"] = "qwen-turbo"  # 使用最快模型
                config["deep_think_llm"] = "qwen-plus"
        elif research_depth == 2:  # 2级 - 基础分析
            config["max_debate_rounds"] = 1
            config["max_risk_discuss_rounds"] = 1
            config["memory_enabled"] = True
            config["online_tools"] = True
            if llm_provider == "dashscope":
                config["quick_think_llm"] = "qwen-plus"
                config["deep_think_llm"] = "qwen-plus"
        elif research_depth == 3:  # 3级 - 标准分析 (默认)
            config["max_debate_rounds"] = 1
            config["max_risk_discuss_rounds"] = 2
            config["memory_enabled"] = True
            config["online_tools"] = True
            if llm_provider == "dashscope":
                config["quick_think_llm"] = "qwen-plus"
                config["deep_think_llm"] = "qwen-max"
        elif research_depth == 4:  # 4级 - 深度分析
            config["max_debate_rounds"] = 2
            config["max_risk_discuss_rounds"] = 2
            config["memory_enabled"] = True
            config["online_tools"] = True
            if llm_provider == "dashscope":
                config["quick_think_llm"] = "qwen-plus"
                config["deep_think_llm"] = "qwen-max"
        else:  # 5级 - 全面分析
            config["max_debate_rounds"] = 3
            config["max_risk_discuss_rounds"] = 3
            config["memory_enabled"] = True
            config["online_tools"] = True
            if llm_provider == "dashscope":
                config["quick_think_llm"] = "qwen-max"
                config["deep_think_llm"] = "qwen-max"

        # 根据LLM提供商设置不同的配置
        if llm_provider == "dashscope":
            config["backend_url"] = "https://dashscope.aliyuncs.com/api/v1"
        elif llm_provider == "google":
            # Google AI不需要backend_url，使用默认的OpenAI格式
            config["backend_url"] = "https://api.openai.com/v1"

        # 修复路径问题
        config["data_dir"] = str(project_root / "data")
        config["results_dir"] = str(project_root / "results")
        config["data_cache_dir"] = str(project_root / "tradingagents" / "dataflows" / "data_cache")

        # 确保目录存在
        update_progress("创建必要的目录...")
        os.makedirs(config["data_dir"], exist_ok=True)
        os.makedirs(config["results_dir"], exist_ok=True)
        os.makedirs(config["data_cache_dir"], exist_ok=True)

        print(f"使用配置: {config}")
        print(f"分析师列表: {analysts}")
        print(f"股票代码: {stock_symbol}")
        print(f"分析日期: {analysis_date}")

        # 根据市场类型调整股票代码格式
        if market_type == "A股":
            # A股代码不需要特殊处理，保持原样
            formatted_symbol = stock_symbol
            update_progress(f"准备分析A股: {formatted_symbol}")
        else:
            # 美股代码转为大写
            formatted_symbol = stock_symbol.upper()
            update_progress(f"准备分析美股: {formatted_symbol}")

        # 初始化交易图
        update_progress("初始化分析引擎...")
        graph = TradingAgentsGraph(analysts, config=config, debug=False)

        # 执行分析
        update_progress(f"开始分析 {formatted_symbol} 股票，这可能需要几分钟时间...")
        state, decision = graph.propagate(formatted_symbol, analysis_date)

        # 调试信息
        print(f"🔍 [DEBUG] 分析完成，decision类型: {type(decision)}")
        print(f"🔍 [DEBUG] decision内容: {decision}")

        # 格式化结果
        update_progress("分析完成，正在整理结果...")

        # 提取风险评估数据
        risk_assessment = extract_risk_assessment(state)

        # 将风险评估添加到状态中
        if risk_assessment:
            state['risk_assessment'] = risk_assessment

        # 记录Token使用（实际使用量，这里使用估算值）
        if TOKEN_TRACKING_ENABLED:
            # 在实际应用中，这些值应该从LLM响应中获取
            # 这里使用基于分析师数量和研究深度的估算
            actual_input_tokens = len(analysts) * (1500 if research_depth == "快速" else 2500 if research_depth == "标准" else 4000)
            actual_output_tokens = len(analysts) * (800 if research_depth == "快速" else 1200 if research_depth == "标准" else 2000)

            usage_record = token_tracker.track_usage(
                provider=llm_provider,
                model_name=llm_model,
                input_tokens=actual_input_tokens,
                output_tokens=actual_output_tokens,
                session_id=session_id,
                analysis_type=f"{market_type}_analysis"
            )

            if usage_record:
                update_progress(f"记录使用成本: ¥{usage_record.cost:.4f}")

        results = {
            'stock_symbol': stock_symbol,
            'analysis_date': analysis_date,
            'analysts': analysts,
            'research_depth': research_depth,
            'llm_provider': llm_provider,
            'llm_model': llm_model,
            'state': state,
            'decision': decision,
            'success': True,
            'error': None,
            'session_id': session_id if TOKEN_TRACKING_ENABLED else None
        }

        update_progress("✅ 分析成功完成！")
        return results

    except Exception as e:
        # 打印详细错误信息用于调试
        print(f"真实分析失败，错误详情: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        import traceback
        print(f"完整错误堆栈: {traceback.format_exc()}")

        # 如果真实分析失败，返回模拟数据用于演示
        return generate_demo_results(stock_symbol, analysis_date, analysts, research_depth, llm_provider, llm_model, str(e))

def format_analysis_results(results):
    """格式化分析结果用于显示"""
    
    if not results['success']:
        return {
            'error': results['error'],
            'success': False
        }
    
    state = results['state']
    decision = results['decision']

    # 提取关键信息
    # decision 可能是字符串（如 "BUY", "SELL", "HOLD"）或字典
    if isinstance(decision, str):
        formatted_decision = {
            'action': decision.strip().upper(),
            'confidence': 0.7,  # 默认置信度
            'risk_score': 0.3,  # 默认风险分数
            'target_price': None,  # 字符串格式没有目标价格
            'reasoning': f'基于AI分析，建议{decision.strip().upper()}'
        }
    elif isinstance(decision, dict):
        # 处理目标价格 - 确保正确提取数值
        target_price = decision.get('target_price')
        if target_price is not None and target_price != 'N/A':
            try:
                # 尝试转换为浮点数
                if isinstance(target_price, str):
                    # 移除货币符号和空格
                    clean_price = target_price.replace('$', '').replace('¥', '').replace('￥', '').strip()
                    target_price = float(clean_price) if clean_price and clean_price != 'None' else None
                elif isinstance(target_price, (int, float)):
                    target_price = float(target_price)
                else:
                    target_price = None
            except (ValueError, TypeError):
                target_price = None
        else:
            target_price = None

        formatted_decision = {
            'action': decision.get('action', 'HOLD'),
            'confidence': decision.get('confidence', 0.5),
            'risk_score': decision.get('risk_score', 0.3),
            # 'target_price': decision.get('target_price', 'N/A'),
            'target_price': target_price,
            'reasoning': decision.get('reasoning', '暂无分析推理')
        }
    else:
        # 处理其他类型
        formatted_decision = {
            'action': 'HOLD',
            'confidence': 0.5,
            'risk_score': 0.3,
            # 'target_price': 'N/A',
            'target_price': None,
            'reasoning': f'分析结果: {str(decision)}'
        }
    
    # 格式化状态信息
    formatted_state = {}
    
    # 处理各个分析模块的结果
    analysis_keys = [
        'market_report',
        'fundamentals_report', 
        'sentiment_report',
        'news_report',
        'risk_assessment',
        'investment_plan'
    ]
    
    for key in analysis_keys:
        if key in state:
            formatted_state[key] = state[key]
    
    return {
        'stock_symbol': results['stock_symbol'],
        'decision': formatted_decision,
        'state': formatted_state,
        'success': True,
        # 将配置信息放在顶层，供前端直接访问
        'analysis_date': results['analysis_date'],
        'analysts': results['analysts'],
        'research_depth': results['research_depth'],
        'llm_provider': results.get('llm_provider', 'dashscope'),
        'llm_model': results['llm_model'],
        'metadata': {
            'analysis_date': results['analysis_date'],
            'analysts': results['analysts'],
            'research_depth': results['research_depth'],
            'llm_provider': results.get('llm_provider', 'dashscope'),
            'llm_model': results['llm_model']
        }
    }

def validate_analysis_params(stock_symbol, analysis_date, analysts, research_depth):
    """验证分析参数"""
    
    errors = []
    
    # 验证股票代码
    if not stock_symbol or len(stock_symbol.strip()) == 0:
        errors.append("股票代码不能为空")
    elif len(stock_symbol.strip()) > 10:
        errors.append("股票代码长度不能超过10个字符")
    
    # 验证分析师列表
    if not analysts or len(analysts) == 0:
        errors.append("必须至少选择一个分析师")
    
    valid_analysts = ['market', 'social', 'news', 'fundamentals']
    invalid_analysts = [a for a in analysts if a not in valid_analysts]
    if invalid_analysts:
        errors.append(f"无效的分析师类型: {', '.join(invalid_analysts)}")
    
    # 验证研究深度
    if not isinstance(research_depth, int) or research_depth < 1 or research_depth > 5:
        errors.append("研究深度必须是1-5之间的整数")
    
    # 验证分析日期
    try:
        from datetime import datetime
        datetime.strptime(analysis_date, '%Y-%m-%d')
    except ValueError:
        errors.append("分析日期格式无效，应为YYYY-MM-DD格式")
    
    return len(errors) == 0, errors

def get_supported_stocks():
    """获取支持的股票列表"""
    
    # 常见的美股股票代码
    popular_stocks = [
        {'symbol': 'AAPL', 'name': '苹果公司', 'sector': '科技'},
        {'symbol': 'MSFT', 'name': '微软', 'sector': '科技'},
        {'symbol': 'GOOGL', 'name': '谷歌', 'sector': '科技'},
        {'symbol': 'AMZN', 'name': '亚马逊', 'sector': '消费'},
        {'symbol': 'TSLA', 'name': '特斯拉', 'sector': '汽车'},
        {'symbol': 'NVDA', 'name': '英伟达', 'sector': '科技'},
        {'symbol': 'META', 'name': 'Meta', 'sector': '科技'},
        {'symbol': 'NFLX', 'name': '奈飞', 'sector': '媒体'},
        {'symbol': 'AMD', 'name': 'AMD', 'sector': '科技'},
        {'symbol': 'INTC', 'name': '英特尔', 'sector': '科技'},
        {'symbol': 'SPY', 'name': 'S&P 500 ETF', 'sector': 'ETF'},
        {'symbol': 'QQQ', 'name': '纳斯达克100 ETF', 'sector': 'ETF'},
    ]
    
    return popular_stocks

def generate_demo_results(stock_symbol, analysis_date, analysts, research_depth, llm_provider, llm_model, error_msg):
    """生成演示分析结果"""

    import random

    # 生成模拟决策
    actions = ['BUY', 'HOLD', 'SELL']
    action = random.choice(actions)

    demo_decision = {
        'action': action,
        'confidence': round(random.uniform(0.6, 0.9), 2),
        'risk_score': round(random.uniform(0.2, 0.7), 2),
        'target_price': round(random.uniform(100, 300), 2),
        'reasoning': f"""
基于对{stock_symbol}的综合分析，我们的AI分析团队得出以下结论：

**投资建议**: {action}

**主要分析要点**:
1. **技术面分析**: 当前价格趋势显示{'上涨' if action == 'BUY' else '下跌' if action == 'SELL' else '横盘'}信号
2. **基本面评估**: 公司财务状况{'良好' if action == 'BUY' else '一般' if action == 'HOLD' else '需关注'}
3. **市场情绪**: 投资者情绪{'乐观' if action == 'BUY' else '中性' if action == 'HOLD' else '谨慎'}
4. **风险评估**: 当前风险水平为{'中等' if action == 'HOLD' else '较低' if action == 'BUY' else '较高'}

**注意**: 这是演示数据，实际分析需要配置正确的API密钥。
        """
    }

    # 生成模拟状态数据
    demo_state = {}

    if 'market' in analysts:
        demo_state['market_report'] = f"""
## 📈 {stock_symbol} 技术面分析报告

### 价格趋势分析
- **当前价格**: ${round(random.uniform(100, 300), 2)}
- **日内变化**: {random.choice(['+', '-'])}{round(random.uniform(0.5, 5), 2)}%
- **52周高点**: ${round(random.uniform(200, 400), 2)}
- **52周低点**: ${round(random.uniform(50, 150), 2)}

### 技术指标
- **RSI (14日)**: {round(random.uniform(30, 70), 1)}
- **MACD**: {'看涨' if action == 'BUY' else '看跌' if action == 'SELL' else '中性'}
- **移动平均线**: 价格{'高于' if action == 'BUY' else '低于' if action == 'SELL' else '接近'}20日均线

### 支撑阻力位
- **支撑位**: ${round(random.uniform(80, 120), 2)}
- **阻力位**: ${round(random.uniform(250, 350), 2)}

*注意: 这是演示数据，实际分析需要配置API密钥*
        """

    if 'fundamentals' in analysts:
        demo_state['fundamentals_report'] = f"""
## 💰 {stock_symbol} 基本面分析报告

### 财务指标
- **市盈率 (P/E)**: {round(random.uniform(15, 35), 1)}
- **市净率 (P/B)**: {round(random.uniform(1, 5), 1)}
- **净资产收益率 (ROE)**: {round(random.uniform(10, 25), 1)}%
- **毛利率**: {round(random.uniform(20, 60), 1)}%

### 盈利能力
- **营收增长**: {random.choice(['+', '-'])}{round(random.uniform(5, 20), 1)}%
- **净利润增长**: {random.choice(['+', '-'])}{round(random.uniform(10, 30), 1)}%
- **每股收益**: ${round(random.uniform(2, 15), 2)}

### 财务健康度
- **负债率**: {round(random.uniform(20, 60), 1)}%
- **流动比率**: {round(random.uniform(1, 3), 1)}
- **现金流**: {'正向' if action != 'SELL' else '需关注'}

*注意: 这是演示数据，实际分析需要配置API密钥*
        """

    if 'social' in analysts:
        demo_state['sentiment_report'] = f"""
## 💭 {stock_symbol} 市场情绪分析报告

### 社交媒体情绪
- **整体情绪**: {'积极' if action == 'BUY' else '消极' if action == 'SELL' else '中性'}
- **情绪强度**: {round(random.uniform(0.5, 0.9), 2)}
- **讨论热度**: {'高' if random.random() > 0.5 else '中等'}

### 投资者情绪指标
- **恐慌贪婪指数**: {round(random.uniform(20, 80), 0)}
- **看涨看跌比**: {round(random.uniform(0.8, 1.5), 2)}
- **期权Put/Call比**: {round(random.uniform(0.5, 1.2), 2)}

### 机构投资者动向
- **机构持仓变化**: {random.choice(['增持', '减持', '维持'])}
- **分析师评级**: {'买入' if action == 'BUY' else '卖出' if action == 'SELL' else '持有'}

*注意: 这是演示数据，实际分析需要配置API密钥*
        """

    if 'news' in analysts:
        demo_state['news_report'] = f"""
## 📰 {stock_symbol} 新闻事件分析报告

### 近期重要新闻
1. **财报发布**: 公司发布{'超预期' if action == 'BUY' else '低于预期' if action == 'SELL' else '符合预期'}的季度财报
2. **行业动态**: 所在行业面临{'利好' if action == 'BUY' else '挑战' if action == 'SELL' else '稳定'}政策环境
3. **公司公告**: 管理层{'乐观' if action == 'BUY' else '谨慎' if action == 'SELL' else '稳健'}展望未来

### 新闻情绪分析
- **正面新闻占比**: {round(random.uniform(40, 80), 0)}%
- **负面新闻占比**: {round(random.uniform(10, 40), 0)}%
- **中性新闻占比**: {round(random.uniform(20, 50), 0)}%

### 市场影响评估
- **短期影响**: {'正面' if action == 'BUY' else '负面' if action == 'SELL' else '中性'}
- **长期影响**: {'积极' if action != 'SELL' else '需观察'}

*注意: 这是演示数据，实际分析需要配置API密钥*
        """

    # 添加风险评估和投资建议
    demo_state['risk_assessment'] = f"""
## ⚠️ {stock_symbol} 风险评估报告

### 主要风险因素
1. **市场风险**: {'低' if action == 'BUY' else '高' if action == 'SELL' else '中等'}
2. **行业风险**: {'可控' if action != 'SELL' else '需关注'}
3. **公司特定风险**: {'较低' if action == 'BUY' else '中等'}

### 风险等级评估
- **总体风险等级**: {'低风险' if action == 'BUY' else '高风险' if action == 'SELL' else '中等风险'}
- **建议仓位**: {random.choice(['轻仓', '标准仓位', '重仓']) if action != 'SELL' else '建议减仓'}

*注意: 这是演示数据，实际分析需要配置API密钥*
    """

    demo_state['investment_plan'] = f"""
## 📋 {stock_symbol} 投资建议

### 具体操作建议
- **操作方向**: {action}
- **建议价位**: ${round(random.uniform(90, 310), 2)}
- **止损位**: ${round(random.uniform(80, 200), 2)}
- **目标价位**: ${round(random.uniform(150, 400), 2)}

### 投资策略
- **投资期限**: {'短期' if research_depth <= 2 else '中长期'}
- **仓位管理**: {'分批建仓' if action == 'BUY' else '分批减仓' if action == 'SELL' else '维持现状'}

*注意: 这是演示数据，实际分析需要配置API密钥*
    """

    return {
        'stock_symbol': stock_symbol,
        'analysis_date': analysis_date,
        'analysts': analysts,
        'research_depth': research_depth,
        'llm_provider': llm_provider,
        'llm_model': llm_model,
        'state': demo_state,
        'decision': demo_decision,
        'success': True,
        'error': None,
        'is_demo': True,
        'demo_reason': f"API调用失败，显示演示数据。错误信息: {error_msg}"
    }
