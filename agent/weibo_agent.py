#!/usr/bin/env python3
"""
微博热搜分析 Agent - 使用 OpenAI 库
"""
import os
import sys
import json
import requests
from datetime import datetime
from openai import OpenAI


def get_weibo_hotsearch(max_count=20):
    """获取微博热搜"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://weibo.com',
    }

    try:
        resp = requests.get('https://weibo.com/ajax/side/hotSearch', headers=headers, timeout=15)
        resp.encoding = 'utf-8'
        data = resp.json()

        if data.get('ok') == 1:
            realtime = data.get('data', {}).get('realtime', [])
            results = []
            for item in realtime[:max_count]:
                word = item.get('word', '')
                if word:
                    results.append({
                        'word': word,
                        'num': item.get('num', 0),
                        'label': item.get('label_name', '')
                    })
            return results
    except Exception as e:
        print(f"获取热搜失败: {e}")

    return []


def call_ai(prompt, api_key, base_url, model):
    """调用 AI API"""
    from openai import OpenAI
    import time

    for attempt in range(3):
        try:
            client = OpenAI(api_key=api_key, base_url=base_url, timeout=120.0)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"  尝试 {attempt + 1}/3 失败: {e}")
            if attempt < 2:
                time.sleep(5)
    return None


def generate_html_report(analysis_data, output_dir="reports"):
    """生成HTML报告"""
    os.makedirs(output_dir, exist_ok=True)

    date_str = datetime.now().strftime("%y%m%d")
    time_str = datetime.now().strftime("%H%M")
    filename = f"微博热搜分析_{date_str}_{time_str}.html"
    filepath = os.path.join(output_dir, filename)

    data = analysis_data
    analysis_date = data.get('analysis_date', datetime.now().strftime("%Y-%m-%d"))
    topics = data.get('topics', [])

    total = len(topics)
    excellent = sum(1 for t in topics if t.get('scores', {}).get('total', 0) >= 80)
    good = sum(1 for t in topics if 60 <= t.get('scores', {}).get('total', 0) < 80)
    avg = sum(t.get('scores', {}).get('total', 0) for t in topics) / total if total > 0 else 0

    topics_html = ""
    for i, topic in enumerate(topics, 1):
        score = topic.get('scores', {}).get('total', 0)
        if score >= 80:
            score_class = "score-high"
        elif score >= 60:
            score_class = "score-mid"
        else:
            score_class = "score-low"

        products = topic.get('product_ideas', [])
        products_html = ""
        for p in products:
            funcs = p.get('features', [])
            funcs_html = "".join(f'<span class="func-tag">{f}</span>' for f in funcs)
            products_html += f'''
            <div class="product-card">
                <div class="product-name">{p.get('name', '未命名')}</div>
                <div class="product-funcs">{funcs_html}</div>
                <div class="product-users">目标用户: <strong>{p.get('target_users', '待定')}</strong></div>
            </div>'''

        topics_html += f'''
        <div class="detail-card">
            <div class="detail-header">
                <div class="detail-topic">{i}. {topic.get('title', '')}</div>
                <div class="detail-score">
                    <span class="score-badge {score_class}">{score}分</span>
                </div>
            </div>
            <div class="detail-bg">{topic.get('background', '暂无背景信息')}</div>
            <div class="products-grid">{products_html}</div>
        </div>'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>微博热搜产品创意分析报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #e4e4e7; min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ text-align: center; padding: 40px 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 40px; }}
        h1 {{ font-size: 2.5em; background: linear-gradient(90deg, #ffd700, #ff8c00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; }}
        .date {{ color: #9ca3af; font-size: 1.1em; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }}
        .stat-card {{ background: rgba(255,255,255,0.05); border-radius: 16px; padding: 24px; text-align: center; border: 1px solid rgba(255,255,255,0.1); }}
        .stat-value {{ font-size: 2.5em; font-weight: bold; margin-bottom: 8px; }}
        .stat-label {{ color: #9ca3af; font-size: 0.95em; }}
        .section-title {{ font-size: 1.8em; margin-bottom: 24px; padding-left: 16px; border-left: 4px solid #ffd700; }}
        .detail-card {{ background: rgba(255,255,255,0.03); border-radius: 16px; padding: 28px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.05); }}
        .detail-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }}
        .detail-topic {{ font-size: 1.3em; font-weight: 600; flex: 1; }}
        .score-badge {{ padding: 6px 14px; border-radius: 6px; font-weight: 600; }}
        .score-high {{ background: linear-gradient(135deg, #ffd700, #ff8c00); color: #1a1a2e; }}
        .score-mid {{ background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: #fff; }}
        .score-low {{ background: rgba(255,255,255,0.1); color: #9ca3af; }}
        .detail-bg {{ color: #9ca3af; margin-bottom: 20px; line-height: 1.6; padding: 12px 16px; background: rgba(0,0,0,0.2); border-radius: 8px; border-left: 3px solid #6366f1; }}
        .products-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }}
        .product-card {{ background: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; border: 1px solid rgba(255,255,255,0.08); }}
        .product-name {{ font-size: 1.1em; font-weight: 600; color: #818cf8; margin-bottom: 12px; }}
        .func-tag {{ display: inline-block; background: rgba(99, 102, 241, 0.2); color: #a5b4fc; padding: 4px 10px; border-radius: 4px; font-size: 0.85em; margin: 3px; }}
        .product-users {{ color: #9ca3af; font-size: 0.9em; margin-top: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>微博热搜产品创意分析</h1>
            <p class="date">{analysis_date} | 数据来源：微博热搜榜</p>
        </header>
        <div class="stats">
            <div class="stat-card"><div class="stat-value">{total}</div><div class="stat-label">热搜总数</div></div>
            <div class="stat-card"><div class="stat-value">{avg:.1f}</div><div class="stat-label">平均评分</div></div>
            <div class="stat-card"><div class="stat-value" style="color:#ffd700">{excellent}</div><div class="stat-label">优秀项目 (>=80)</div></div>
            <div class="stat-card"><div class="stat-value" style="color:#34d399">{good}</div><div class="stat-label">良好项目 (60-79)</div></div>
        </div>
        <h2 class="section-title">详细分析列表</h2>
        {topics_html}
    </div>
</body>
</html>'''

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    return filepath


def main():
    print("=" * 60)
    print("微博热搜产品创意分析 Agent")
    print("=" * 60)

    # 获取配置
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("错误: 未设置 ANTHROPIC_API_KEY")
        sys.exit(1)

    base_url = os.environ.get("ANTHROPIC_API_URL", "https://api.minimax.com/v1")
    model = os.environ.get("ANTHROPIC_MODEL", "MiniMax-M2.5")

    print(f"[*] API: {base_url}")
    print(f"[*] Model: {model}")

    # 1. 获取热搜
    print("\n[*] 获取微博热搜...")
    hot_searches = get_weibo_hotsearch(20)

    if len(hot_searches) < 5:
        print(f"热搜数量不足: {len(hot_searches)}")
        sys.exit(1)

    print(f"[*] 获取到 {len(hot_searches)} 条热搜")

    # 热搜列表转文本
    topics_text = "\n".join([f"{i+1}. {t['word']} (热度: {t['num']})" for i, t in enumerate(hot_searches)])

    # 2. 构建 Prompt
    prompt = f"""请分析以下微博热搜榜单，从产品创意角度对每个话题进行评分和创意提取。

热搜榜单:
{topics_text}

请返回JSON格式的分析结果:
{{
  "analysis_date": "{datetime.now().strftime("%Y-%m-%d")}",
  "total_topics": {len(hot_searches)},
  "topics": [
    {{
      "rank": 1,
      "title": "热搜标题",
      "heat_value": 1234567,
      "background": "事件背景(2-3句话)",
      "scores": {{
        "interesting": 75,
        "useful": 18,
        "total": 63.6
      }},
      "product_ideas": [
        {{
          "name": "产品名称",
          "features": ["功能1", "功能2", "功能3"],
          "target_users": "目标用户描述"
        }}
      ]
    }}
  ]
}}

评分标准:
- 有趣度(80分): 话题性(30) + 新奇性(25) + 传播度(25)
- 有用度(20分): 实用性(10) + 市场需求(10)
- 总分 = 有趣度 x 0.8 + 有用度 x 0.2

请直接返回JSON，不要其他内容。"""

    # 3. 调用 API
    print("[*] 调用 AI 分析...")
    result = call_ai(prompt, api_key, base_url, model)

    if not result:
        print("API 调用失败")
        sys.exit(1)

    print(f"[*] 收到响应，长度: {len(result)}")

    # 4. 解析 JSON
    print("[*] 解析分析结果...")

    # 清理响应：移除 thinking 标签
    cleaned = result
    if '</think>' in cleaned:
        cleaned = cleaned.split('</think>')[-1]
    if '<thinking>' in cleaned:
        cleaned = cleaned.split('<thinking>')[-1]
    cleaned = cleaned.strip()

    print(f"[*] 清理后长度: {len(cleaned)}")

    try:
        # 尝试提取 JSON
        json_start = cleaned.find('{')
        json_end = cleaned.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = cleaned[json_start:json_end]
            analysis_data = json.loads(json_str)
        else:
            analysis_data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"JSON 解析失败: {e}")
        print(f"清理后内容前500字: {cleaned[:500]}")
        sys.exit(1)

    # 5. 生成报告
    print("[*] 生成 HTML 报告...")
    filepath = generate_html_report(analysis_data)

    print(f"\n成功! 报告已生成: {filepath}")
    print("=" * 60)


if __name__ == "__main__":
    main()
