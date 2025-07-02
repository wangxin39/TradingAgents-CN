# TradingAgents 中文增强版

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Documentation](https://img.shields.io/badge/docs-中文文档-green.svg)](./docs/)
[![Original](https://img.shields.io/badge/基于-TauricResearch/TradingAgents-orange.svg)](https://github.com/TauricResearch/TradingAgents)

基于多智能体大语言模型的中文金融交易决策框架。本项目基于 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) 开发，专为中文用户提供完整的文档体系和本地化支持。

## 🎯 项目目标

### 原始项目简介

[TradingAgents](https://github.com/TauricResearch/TradingAgents) 是由 Tauric Research 开发的创新性多智能体交易框架，模拟真实交易公司的协作决策流程，通过多个专业化AI智能体的协作来评估市场条件并做出交易决策。

### 我们的增强目标

本项目旨在为中文用户提供：

- 📚 **完整的中文文档体系** - 详细的架构说明、使用指南和最佳实践
- 🇨🇳 **中国市场适配** - 支持A股、港股等中国金融市场
- 🧠 **国产LLM集成** - 集成文心一言、通义千问等国产大模型
- 📊 **中文数据源** - 整合Tushare、AkShare等中文金融数据源
- 🎓 **教育和研究** - 为中文用户提供金融AI学习和研究平台

## ✨ 核心特性

### 🤖 多智能体协作架构

- **分析师团队**: 基本面、技术面、新闻面、社交媒体四大专业分析师
- **研究员团队**: 看涨/看跌研究员进行结构化辩论
- **交易员智能体**: 基于所有输入做出最终交易决策
- **风险管理**: 多层次风险评估和管理机制
- **管理层**: 协调各团队工作，确保决策质量

### 🧠 多LLM模型支持

- **阿里百炼**: qwen-turbo, qwen-plus, qwen-max ✅
- **Google AI**: gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash ✅
- **OpenAI**: GPT-4o, GPT-4o-mini, GPT-3.5-turbo
- **Anthropic**: Claude-3-Opus, Claude-3-Sonnet, Claude-3-Haiku
- **智能混合**: Google AI推理 + 阿里百炼嵌入 ✅

### 🌐 Web管理界面 (v0.1.2新增)

- **Streamlit Web平台**: 直观的股票分析界面 ✅
- **实时进度显示**: 分析过程可视化跟踪 ✅
- **多模型选择**: 支持阿里百炼和Google AI切换 ✅
- **分析师配置**: 灵活的分析师组合选择 ✅
- **结果可视化**: 专业的分析报告展示 ✅
- **响应式设计**: 支持桌面和移动端访问 ✅

### 📊 全面数据集成

- **实时数据**: FinnHub、Yahoo Finance ✅
- **新闻数据**: Google News、财经新闻 ✅
- **社交数据**: Reddit、Twitter情绪分析 ✅
- **中文数据** (计划中): Tushare、AkShare、东方财富

### 🚀 高性能特性

- **并行处理**: 多智能体并行分析，提高效率
- **智能缓存**: 多层缓存策略，减少API调用成本
- **实时分析**: 支持实时市场数据分析
- **灵活配置**: 高度可定制的智能体行为和模型选择

## 🆚 与原版的主要区别

### ✅ 已完成的增强


| 功能     | 原版     | 中文增强版             |
| -------- | -------- | ---------------------- |
| 文档语言 | 英文     | 完整中文文档体系       |
| 架构说明 | 基础说明 | 详细的架构设计文档     |
| 使用指南 | 简单示例 | 从入门到高级的完整指南 |
| 配置说明 | 基础配置 | 详细的配置优化指南     |
| 故障排除 | 无       | 完整的FAQ和故障排除    |
| 代码注释 | 英文     | 中文注释和说明         |

### 🔄 计划中的增强

- **中国市场支持**: A股、港股、新三板数据集成
- **中文数据源**: Tushare、AkShare、Wind等数据源
- **国产LLM**: 文心一言、通义千问、智谱清言等
- **中文金融术语**: 优化中文金融分析术语和表达
- **监管合规**: 符合中国金融监管要求的风险提示
- **本地化部署**: 支持私有化部署和数据安全

## 🚀 快速开始

### 环境要求

- Python 3.10+ (推荐 3.11)
- 4GB+ RAM (推荐 8GB+)
- 稳定的网络连接

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/wangxin39/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 创建虚拟环境
python -m venv tradingagents
source tradingagents/bin/activate  # Linux/macOS
# tradingagents\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt
```

### 配置API密钥

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加您的API密钥
# 阿里百炼API（推荐，国产模型）
DASHSCOPE_API_KEY=your_dashscope_api_key

# Google AI API（可选，支持Gemini模型）
GOOGLE_API_KEY=your_google_api_key

# 金融数据API（可选）
FINNHUB_API_KEY=your_finnhub_api_key

# Reddit API（可选，用于社交媒体分析）
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_reddit_user_agent
```

### 🌐 Web界面使用 (推荐)

```bash
# 启动Web管理界面
python -m streamlit run web/app.py

# 或使用快捷脚本
# Windows
start_web.bat

# Linux/macOS
./start_web.sh
```

然后在浏览器中访问 `http://localhost:8501`，您可以：

- 🎯 选择LLM提供商（阿里百炼/Google AI）
- 🤖 选择AI模型（qwen-plus/gemini-2.0-flash等）
- 📊 配置分析师组合（市场/基本面/新闻/社交媒体）
- 📈 输入股票代码进行分析
- 📋 查看详细的分析报告和投资建议

### 🖥️ 命令行界面

```bash
# 启动交互式命令行界面
python cli/main.py

# 直接分析指定股票
python cli/main.py --stock AAPL --analysts market fundamentals
```

### 🐍 Python API使用

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 配置使用阿里百炼模型
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "dashscope"
config["deep_think_llm"] = "qwen-plus"
config["quick_think_llm"] = "qwen-turbo"

# 创建交易智能体
ta = TradingAgentsGraph(["market", "fundamentals"], config=config)

# 分析股票 (以苹果公司为例)
state, decision = ta.propagate("AAPL", "2025-06-27")

# 输出分析结果
print(f"推荐动作: {decision['action']}")
print(f"置信度: {decision['confidence']:.1%}")
print(f"风险评分: {decision['risk_score']:.1%}")
print(f"推理过程: {decision['reasoning']}")
```

## 📚 完整文档

我们提供了详细的中文文档，涵盖从入门到高级的所有内容：

### 📖 概览文档

- [📋 项目概述](docs/overview/project-overview.md) - 详细的项目背景和特性介绍
- [🚀 快速开始](docs/overview/quick-start.md) - 从安装到第一次运行的完整指南
- [⚙️ 详细安装](docs/overview/installation.md) - 各平台详细安装说明

### 🏗️ 架构文档

- [🏛️ 系统架构](docs/architecture/system-architecture.md) - 完整的系统架构设计
- [🤖 智能体架构](docs/architecture/agent-architecture.md) - 智能体设计模式和协作机制
- [📊 数据流架构](docs/architecture/data-flow-architecture.md) - 数据获取、处理和分发流程
- [🔄 图结构设计](docs/architecture/graph-structure.md) - LangGraph工作流程设计

### 🤖 智能体文档

- [📈 分析师团队](docs/agents/analysts.md) - 四类专业分析师详解
- [🔬 研究员团队](docs/agents/researchers.md) - 看涨/看跌研究员和辩论机制
- [💼 交易员智能体](docs/agents/trader.md) - 交易决策制定流程
- [🛡️ 风险管理](docs/agents/risk-management.md) - 多层次风险评估体系
- [👔 管理层智能体](docs/agents/managers.md) - 协调和决策管理

### 📊 数据处理

- [🔌 数据源集成](docs/data/data-sources.md) - 支持的数据源和API集成
- [⚙️ 数据处理流程](docs/data/data-processing.md) - 数据清洗、转换和验证
- [💾 缓存策略](docs/data/caching.md) - 多层缓存优化性能

### ⚙️ 配置与部署

- [📝 配置指南](docs/configuration/config-guide.md) - 详细的配置选项说明
- [🧠 LLM配置](docs/configuration/llm-config.md) - 大语言模型配置优化

### 💡 示例和教程

- [📚 基础示例](docs/examples/basic-examples.md) - 8个实用的基础示例
- [🚀 高级示例](docs/examples/advanced-examples.md) - 复杂场景和扩展开发

### ❓ 帮助文档

- [🆘 常见问题](docs/faq/faq.md) - 详细的FAQ和解决方案

## 💰 成本控制

### 典型使用成本

- **经济模式**: $0.01-0.05/次分析 (使用 gpt-4o-mini)
- **标准模式**: $0.05-0.15/次分析 (使用 gpt-4o)
- **高精度模式**: $0.10-0.30/次分析 (使用 gpt-4o + 多轮辩论)

### 成本优化建议

```python
# 低成本配置示例
cost_optimized_config = {
    "deep_think_llm": "gpt-4o-mini",
    "quick_think_llm": "gpt-4o-mini", 
    "max_debate_rounds": 1,
    "online_tools": False  # 使用缓存数据
}
```

## 🤝 贡献指南

我们欢迎各种形式的贡献：

### 贡献类型

- 🐛 **Bug修复** - 发现并修复问题
- ✨ **新功能** - 添加新的功能特性
- 📚 **文档改进** - 完善文档和教程
- 🌐 **本地化** - 翻译和本地化工作
- 🎨 **代码优化** - 性能优化和代码重构

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目基于 Apache 2.0 许可证开源。详见 [LICENSE](LICENSE) 文件。

### 许可证说明

- ✅ 商业使用
- ✅ 修改和分发
- ✅ 私人使用
- ✅ 专利使用
- ❗ 需要保留版权声明
- ❗ 需要包含许可证副本

## 🙏 致谢

### 原始项目

感谢 [Tauric Research](https://github.com/TauricResearch) 团队开发的优秀 TradingAgents 框架，为金融AI领域做出的重要贡献。

### 开源社区

感谢所有为本项目贡献代码、文档和建议的开发者和用户。

## 📞 联系方式

- **GitHub Issues**: [提交问题和建议](https://github.com/wangxin39/TradingAgents-CN/issues)
- **邮箱**: wangxin@yundsm.com
- **原项目**: [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)
- **原项目中文版**: [hsliuping/TradingAgents-CN](https://github.com/hsliuping/TradingAgents-CN)

## ⚠️ 风险提示

**重要声明**: 本框架仅用于研究和教育目的，不构成投资建议。

- 📊 交易表现可能因多种因素而异
- 🤖 AI模型的预测存在不确定性
- 💰 投资有风险，决策需谨慎
- 👨‍💼 建议咨询专业财务顾问

---

<div align="center">

**🌟 如果这个项目对您有帮助，请给我们一个 Star！**

[⭐ Star this repo](https://github.com/hsliuping/TradingAgents-CN) | [🍴 Fork this repo](https://github.com/hsliuping/TradingAgents-CN/fork) | [📖 Read the docs](./docs/)

</div>
