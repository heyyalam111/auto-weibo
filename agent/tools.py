"""
微博热搜分析 Agent 工具定义
支持自定义 API 端点 (MiniMax 兼容 Anthropic)
"""
import os
import json
import requests
from datetime import datetime
from typing import Optional
from anthropic import BetaTool


class GetWeiboHotsearchTool(BetaTool):
    """获取微博热搜榜单工具"""

    def __init__(self):
        self.name = "get_weibo_hotsearch"
        self.description = "获取当前微博热搜榜单，返回热搜话题列表。返回格式为JSON数组，每个元素包含话题名称、热度值和标签。"

    def __call__(self, max_count: int = 20) -> str:
        """
        执行获取热搜

        Args:
            max_count: 最大获取数量，默认20

        Returns:
            JSON格式的热搜列表
        """
        # 方案1: 微博官方接口
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://weibo.com',
            'Accept': 'application/json',
        }

        try:
            resp = requests.get(
                'https://weibo.com/ajax/side/hotSearch',
                headers=headers,
                timeout=15
            )
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
                            'label': item.get('label_name', ''),
                            'flag': item.get('flag', 0)
                        })

                if results:
                    return json.dumps(results, ensure_ascii=False, indent=2)

        except Exception as e:
            pass

        # 方案2: 天行数据API (备用)
        api_key = os.environ.get("TIANXING_API_KEY")
        if api_key:
            try:
                resp = requests.get(
                    'https://apis.tianapi.com/weibohot/index',
                    params={'key': api_key},
                    timeout=15
                )
                data = resp.json()
                if data.get('code') == 200:
                    newslist = data.get('result', {}).get('newslist', [])
                    results = []
                    for item in newslist[:max_count]:
                        results.append({
                            'word': item.get('hotword', ''),
                            'num': item.get('hotwordnum', 0),
                            'label': item.get('hottag', '')
                        })
                    return json.dumps(results, ensure_ascii=False, indent=2)
            except Exception as e:
                pass

        return json.dumps({"error": "获取热搜失败，请稍后重试"})


class GenerateHtmlReportTool(BetaTool):
    """生成HTML报告工具"""

    def __init__(self):
        self.name = "generate_html_report"
        self.description = "根据分析数据生成精美的HTML报告文件，保存到reports目录"

    def __call__(self, analysis_data: str, filename: Optional[str] = None) -> str:
        """
        生成HTML报告

        Args:
            analysis_data: JSON格式的分析数据
            filename: 可选的自定义文件名

        Returns:
            生成报告的路径
        """
        import re

        # 解析分析数据
        try:
            data = json.loads(analysis_data)
        except:
            return json.dumps({"error": "分析数据格式无效"})

        # 生成文件名
        if not filename:
            date_str = datetime.now().strftime("%y%m%d")
            time_str = datetime.now().strftime("%H%M")
            filename = f"微博热搜分析_{date_str}_{time_str}.html"

        # 确保目录存在
        os.makedirs("reports", exist_ok=True)
        filepath = os.path.join("reports", filename)

        # 读取模板
        template_path = "skills/weibo-product-analyzer/templates/report_template.html"
        if not os.path.exists(template_path):
            # 使用内置模板
            html = self._generate_default_template(data)
        else:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            html = self._render_template(template, data)

        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        return json.dumps({"success": True, "filepath": filepath}, ensure_ascii=False)

    def _generate_default_template(self, data: dict) -> str:
        """生成默认模板"""
        analysis_date = data.get('analysis_date', datetime.now().strftime("%Y-%m-%d"))
        topics = data.get('topics', [])

        # 计算统计
        total = len(topics)
        excellent = sum(1 for t in topics if t.get('scores', {}).get('total', 0) >= 80)
        good = sum(1 for t in topics if 60 <= t.get('scores', {}).get('total', 0) < 80)
        avg = sum(t.get('scores', {}).get('total', 0) for t in topics) / total if total > 0 else 0

        # 生成话题列表HTML
        topics_html = ""
        for i, topic in enumerate(topics, 1):
            score = topic.get('scores', {}).get('total', 0)
            if score >= 80:
                score_class = "score-high"
            elif score >= 60:
                score_class = "score-mid"
            else:
                score_class = "score-low"

            # 产品创意
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
                </div>
                '''

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
            </div>
            '''

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
        @media (max-width: 768px) {{ .detail-header {{ flex-direction: column; }} .products-grid {{ grid-template-columns: 1fr; }} }}
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
            <div class="stat-card"><div class="stat-value" style="color:#ffd700">{excellent}</div><div class="stat-label">优秀项目 (≥80)</div></div>
            <div class="stat-card"><div class="stat-value" style="color:#34d399">{good}</div><div class="stat-label">良好项目 (60-79)</div></div>
        </div>
        <h2 class="section-title">📱 详细分析列表</h2>
        {topics_html}
    </div>
</body>
</html>'''
        return html

    def _render_template(self, template: str, data: dict) -> str:
        """渲染模板"""
        analysis_date = data.get('analysis_date', datetime.now().strftime("%Y-%m-%d"))
        topics = data.get('topics', [])

        # 计算统计
        total = len(topics)
        excellent = sum(1 for t in topics if t.get('scores', {}).get('total', 0) >= 80)
        good = sum(1 for t in topics if 60 <= t.get('scores', {}).get('total', 0) < 80)
        avg = sum(t.get('scores', {}).get('total', 0) for t in topics) / total if total > 0 else 0

        html = template
        html = html.replace('{{ANALYSIS_DATE}}', analysis_date)
        html = html.replace('{{TOTAL_TOPICS}}', str(total))
        html = html.replace('{{EXCELLENT_COUNT}}', str(excellent))
        html = html.replace('{{GOOD_COUNT}}', str(good))
        html = html.replace('{{AVG_SCORE}}', str(round(avg, 1)))
        html = html.replace('{{TOPICS_DATA}}', json.dumps(topics, ensure_ascii=False))

        return html


# 导出工具实例
get_weibo_hotsearch_tool = GetWeiboHotsearchTool()
generate_html_report_tool = GenerateHtmlReportTool()
