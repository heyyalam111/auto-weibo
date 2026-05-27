# Weibo Hot Search Product Idea Analyzer

Language: [中文](README.md) | English

`auto-weibo` is a Claude Code / agent-oriented workflow for turning Weibo hot-search topics into product ideas. It fetches current trending topics, scores them by interest and utility, extracts product concepts, and generates an HTML report.

## Features

- Fetch current Weibo hot-search topics, with a default cap of 20 topics.
- Produce topic background, scoring, and product-idea summaries.
- Generate an HTML report with overview metrics, score tiers, and product cards.
- Run either as standalone Python scripts or as a Claude Code Skill.
- Use `agent/weibo_agent.py` with an OpenAI-compatible API endpoint for deeper AI analysis.

## Repository Layout

```text
.
├── weibo_analyzer.py                     # Basic script: fetch, score, report
├── weibo_hotsearch.py                    # Weibo and fallback hot-search fetchers
├── generate_report_demo.py               # Report-generation demo
├── agent/
│   ├── weibo_agent.py                    # AI analysis agent
│   ├── tools.py                          # Helper tools
│   └── prompts.py                        # Analysis prompts
├── skills/weibo-product-analyzer/
│   ├── SKILL.md                          # Claude Code Skill definition
│   ├── README.md                         # Skill-level guide
│   └── templates/report_template.html    # HTML report template
└── reports/                              # Sample and generated reports
```

## Installation

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

## Quick Start

### Run the standalone script

```bash
python weibo_analyzer.py
```

The script writes reports like:

```text
reports/微博热搜分析_260219_1430.html
```

### Use as a Claude Code Skill

Copy `skills/weibo-product-analyzer` into a `skills/` directory discoverable by Claude Code, then say:

```text
分析微博热搜
```

The Skill follows the workflow in `SKILL.md`: fetch topics, enrich background, score topics, extract product ideas, generate a report, and open it.

### Use the AI agent entrypoint

```bash
export ANTHROPIC_API_KEY="your-api-key"
export ANTHROPIC_API_URL="https://your-openai-compatible-endpoint/v1"
export ANTHROPIC_MODEL="your-model"
python agent/weibo_agent.py
```

PowerShell:

```powershell
$env:ANTHROPIC_API_KEY="your-api-key"
$env:ANTHROPIC_API_URL="https://your-openai-compatible-endpoint/v1"
$env:ANTHROPIC_MODEL="your-model"
python agent/weibo_agent.py
```

## Configuration

| Item | Default | Description |
|---|---:|---|
| `MAX_TOPICS` | 20 | Maximum number of hot-search topics to analyze |
| `MIN_TOPICS` | 5 | Stop if fewer topics are available |
| `REPORT_DIR` | `reports` | Output directory for HTML reports |
| `ANTHROPIC_API_KEY` | unset | API key used by the agent entrypoint |
| `ANTHROPIC_API_URL` | code default | OpenAI-compatible API base URL |
| `ANTHROPIC_MODEL` | code default | Model name |

## Output

The HTML report includes:

- Analysis time, topic count, average score, and tier counts.
- Topic title, heat value, background summary, and score.
- Product ideas with product name, key features, and target users.

## Security Note

Do not commit real API keys to a public repository. Move secrets to environment variables or a local `.env` file, and rotate any key that has already been exposed.

## License

MIT
