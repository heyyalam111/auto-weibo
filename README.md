# 微博热搜产品创意分析器

语言：中文 | [English](README_EN.md)

`auto-weibo` 是一个面向 Claude Code / Agent 工作流的微博热搜产品创意分析工具。它会抓取当前微博热搜，按“有趣度 + 有用度”评分，从热点中提炼可落地的产品创意，并生成 HTML 报告。

## 核心能力

- 获取当前微博热搜榜单，默认最多分析 20 条。
- 为每个热点生成背景摘要、评分和产品创意。
- 输出包含统计卡片、评分分层和创意卡片的 HTML 报告。
- 提供两种使用方式：Python 脚本直接运行，或作为 Claude Code Skill 触发。
- `agent/weibo_agent.py` 支持 OpenAI-compatible API 端点，用于更完整的 AI 分析流程。

## 仓库结构

```text
.
├── weibo_analyzer.py                     # 简化版主脚本：抓取、评分、生成报告
├── weibo_hotsearch.py                    # 微博官方接口与备用数据源封装
├── generate_report_demo.py               # 报告生成示例
├── agent/
│   ├── weibo_agent.py                    # AI 分析 Agent
│   ├── tools.py                          # 工具函数
│   └── prompts.py                        # 分析提示词
├── skills/weibo-product-analyzer/
│   ├── SKILL.md                          # Claude Code Skill 定义
│   ├── README.md                         # Skill 目录说明
│   └── templates/report_template.html    # HTML 报告模板
└── reports/                              # 示例与生成报告
```

## 安装

```bash
git clone https://github.com/heyyalam111/auto-weibo.git
cd auto-weibo

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install requests openai
```

## 快速使用

### 直接运行脚本

```bash
python weibo_analyzer.py
```

运行后会生成类似下面的文件：

```text
reports/微博热搜分析_260219_1430.html
```

### 使用 Claude Code Skill

将 `skills/weibo-product-analyzer` 放到 Claude Code 可发现的 `skills/` 目录下，然后输入：

```text
分析微博热搜
```

Skill 会按 `SKILL.md` 中定义的静默流程执行：抓取热搜、补充背景、评分、提取产品创意、生成并打开报告。

### 使用 AI Agent 入口

```bash
set ANTHROPIC_API_KEY=your-api-key
set ANTHROPIC_API_URL=https://your-openai-compatible-endpoint/v1
set ANTHROPIC_MODEL=your-model
python agent/weibo_agent.py
```

PowerShell:

```powershell
$env:ANTHROPIC_API_KEY="your-api-key"
$env:ANTHROPIC_API_URL="https://your-openai-compatible-endpoint/v1"
$env:ANTHROPIC_MODEL="your-model"
python agent/weibo_agent.py
```

## 配置项

| 项目 | 默认值 | 说明 |
|---|---:|---|
| `MAX_TOPICS` | 20 | 最多分析的热搜数量 |
| `MIN_TOPICS` | 5 | 低于该数量时停止分析 |
| `REPORT_DIR` | `reports` | HTML 报告输出目录 |
| `ANTHROPIC_API_KEY` | 无 | Agent 模式使用的模型 API Key |
| `ANTHROPIC_API_URL` | 代码默认值 | OpenAI-compatible API 地址 |
| `ANTHROPIC_MODEL` | 代码默认值 | 模型名称 |

## 输出内容

HTML 报告包含：

- 分析时间、热搜总数、平均分、优秀/良好项目数量。
- 每条热搜的标题、热度值、背景摘要和综合评分。
- 每条高价值热点对应的产品创意、核心功能和目标用户。

## 安全提醒

历史文件中可能出现过示例 API Key。公开仓库中不要提交真实密钥；建议将所有 API Key 迁移到环境变量或本地 `.env`，并轮换已经暴露过的密钥。

## 许可证

MIT
