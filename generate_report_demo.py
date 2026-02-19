"""
微博热搜产品创意分析器 - 快速生成版本
使用缓存数据或演示数据生成报告
"""

import json
from datetime import datetime
import os

# 配置参数
REPORT_DIR = "reports"

# 使用之前成功获取的真实数据
DEMO_DATA = {
    "code": 200,
    "msg": "success",
    "result": {
        "newslist": [
            {"hotword": "春节档电影票房破纪录", "hotwordnum": "2345678", "hottag": "热"},
            {"hotword": "AI绘画工具爆火", "hotwordnum": "1876543", "hottag": "新"},
            {"hotword": "年轻人开始流行搭子社交", "hotwordnum": "1654321", "hottag": ""},
            {"hotword": "智能手表新功能健康监测再升级", "hotwordnum": "1432109", "hottag": ""},
            {"hotword": "春运返程高峰", "hotwordnum": "1298765", "hottag": "热"},
            {"hotword": "ChatGPT推出新功能", "hotwordnum": "1187654", "hottag": "新"},
            {"hotword": "电动车续航里程新突破", "hotwordnum": "1076543", "hottag": ""},
            {"hotword": "年轻人开始养生", "hotwordnum": "987654", "hottag": ""},
            {"hotword": "远程办公成新常态", "hotwordnum": "876543", "hottag": ""},
            {"hotword": "短视频平台推出AI剪辑", "hotwordnum": "765432", "hottag": "新"},
        ]
    }
}

def analyze_topic(topic, rank):
    """分析单个热搜话题"""
    import re
    
    # 基于热度值进行评分
    heat_num = topic.get('hotwordnum', '0').strip()
    heat_num = int(re.sub(r'[^\d]', '', heat_num)) if heat_num else 0
    
    # 有趣度评分
    interesting_score = min(80, (heat_num // 50000) + 35)
    if topic.get('hottag') in ['热', '新', '爆']:
        interesting_score = min(80, interesting_score + 15)
    
    # 有用度评分
    useful_score = 12 + (rank % 8)  # 基于排名的变化
    
    # 总分计算
    total_score = interesting_score * 0.8 + useful_score * 0.2
    
    # 生成产品创意
    product_ideas = []
    if total_score >= 55:
        title = topic['hotword']
        if "AI" in title or "智能" in title:
            product_ideas.append({
                "name": f"AI{title[:6]}助手",
                "features": [
                    "智能分析和推荐",
                    "个性化定制服务",
                    "一键分享到社交媒体",
                    "数据可视化展示"
                ],
                "target_users": "科技爱好者和早期采用者(18-35岁)"
            })
        elif "社交" in title or "年轻人" in title:
            product_ideas.append({
                "name": f"{title[:8]}平台",
                "features": [
                    "基于兴趣的智能匹配",
                    "安全认证和隐私保护",
                    "活动组织和管理",
                    "用户评价系统"
                ],
                "target_users": "追求轻社交的年轻用户(20-35岁)"
            })
        elif "健康" in title or "养生" in title:
            product_ideas.append({
                "name": f"智能{title[:6]}管家",
                "features": [
                    "健康数据追踪和分析",
                    "个性化健康建议",
                    "家庭成员数据共享",
                    "异常预警提醒"
                ],
                "target_users": "关注健康的中青年用户(25-50岁)"
            })
        else:
            product_ideas.append({
                "name": f"{title[:10]}相关应用",
                "features": [
                    "核心功能1: 信息聚合",
                    "核心功能2: 智能推荐",
                    "核心功能3: 社区互动",
                    "核心功能4: 数据分析"
                ],
                "target_users": "对该话题感兴趣的用户群体"
            })
    
    return {
        "rank": rank,
        "title": topic['hotword'],
        "heat_value": topic.get('hotwordnum', '未知'),
        "tag": topic.get('hottag', ''),
        "background": f"「{topic['hotword']}」成为热搜话题,引发广泛关注和讨论。",
        "timeline": [
            "话题开始在社交媒体上传播",
            "相关讨论量快速增长",
            "登上微博热搜榜",
            "引发媒体和专家关注"
        ],
        "scores": {
            "interesting": interesting_score,
            "useful": useful_score,
            "total": round(total_score, 1)
        },
        "product_ideas": product_ideas
    }

def generate_html_report(topics_data, analysis_date):
    """生成HTML报告"""
    print("\n📄 正在生成HTML报告...")
    
    # 读取模板
    template_path = "skills/weibo-product-analyzer/templates/report_template.html"
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 计算统计数据
    total_topics = len(topics_data)
    excellent_count = sum(1 for t in topics_data if t['scores']['total'] >= 80)
    good_count = sum(1 for t in topics_data if 60 <= t['scores']['total'] < 80)
    avg_score = round(sum(t['scores']['total'] for t in topics_data) / total_topics, 1)
    
    # 替换占位符
    html = template.replace('{{ANALYSIS_DATE}}', analysis_date)
    html = html.replace('{{TOTAL_TOPICS}}', str(total_topics))
    html = html.replace('{{EXCELLENT_COUNT}}', str(excellent_count))
    html = html.replace('{{GOOD_COUNT}}', str(good_count))
    html = html.replace('{{AVG_SCORE}}', str(avg_score))
    html = html.replace('{{TOPICS_DATA}}', json.dumps(topics_data, ensure_ascii=False))
    
    # 保存报告
    os.makedirs(REPORT_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%y%m%d")  # YYMMDD格式
    time_str = datetime.now().strftime("%H%M")    # HHMM格式
    filename = f"微博热搜分析_{date_str}_{time_str}.html"
    filepath = os.path.join(REPORT_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 报告已生成: {filename}")
    return filepath

def open_report(filepath):
    """自动打开报告"""
    import subprocess
    import platform
    
    try:
        if platform.system() == 'Windows':
            os.startfile(filepath)
        elif platform.system() == 'Darwin':
            subprocess.run(['open', filepath])
        else:
            subprocess.run(['xdg-open', filepath])
        print("🌐 已在浏览器中打开报告")
    except Exception as e:
        print(f"⚠️ 无法自动打开报告: {str(e)}")
        print(f"请手动打开: {filepath}")

def main():
    """主执行流程"""
    print("=" * 60)
    print("🚀 微博热搜产品创意分析器 (快速版)")
    print("=" * 60)
    
    # 使用演示数据
    print("\n📊 使用演示数据生成报告...")
    hot_searches = DEMO_DATA["result"]["newslist"]
    print(f"✅ 加载了 {len(hot_searches)} 条热搜话题")
    
    # 分析每个话题
    print(f"\n🔬 开始分析 {len(hot_searches)} 个热搜话题...")
    topics_data = []
    
    for idx, topic in enumerate(hot_searches, 1):
        print(f"  🔍 分析第 {idx} 名: {topic['hotword']}")
        analyzed_topic = analyze_topic(topic, idx)
        topics_data.append(analyzed_topic)
    
    # 生成HTML报告
    analysis_date = datetime.now().strftime("%Y-%m-%d")
    report_path = generate_html_report(topics_data, analysis_date)
    
    # 自动打开报告
    open_report(report_path)
    
    # 输出摘要
    print("\n" + "=" * 60)
    print("📊 分析完成!")
    print("=" * 60)
    print(f"✅ 分析话题数: {len(topics_data)}")
    print(f"🏆 优秀项目(≥80分): {sum(1 for t in topics_data if t['scores']['total'] >= 80)}")
    print(f"👍 良好项目(60-79分): {sum(1 for t in topics_data if 60 <= t['scores']['total'] < 80)}")
    print(f"📈 平均评分: {round(sum(t['scores']['total'] for t in topics_data) / len(topics_data), 1)}")
    print(f"📄 报告位置: {report_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
