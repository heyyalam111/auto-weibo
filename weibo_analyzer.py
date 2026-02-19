"""
微博热搜产品创意分析器 - 主执行脚本
自动抓取微博热搜,分析并生成产品创意报告
"""

import requests
import json
from datetime import datetime
import os
import re

# API配置
WEIBO_API_URL = "https://apis.tianapi.com/weibohot/index"
API_KEY = "76f000a3377212e17c8f5d716761f2f4"

# 配置参数
MAX_TOPICS = 20  # 最多分析的话题数量
MIN_TOPICS = 5   # 最少需要的话题数量
REPORT_DIR = "reports"

def fetch_weibo_hot_search():
    """获取微博热搜榜单"""
    print("📡 正在获取微博热搜榜单...")
    
    max_retries = 3
    timeout = 30  # 增加超时时间到30秒
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"  尝试 {attempt}/{max_retries}...")
            response = requests.get(
                WEIBO_API_URL,
                params={"key": API_KEY},
                timeout=timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") == 200:
                newslist = data.get("result", {}).get("newslist", [])
                print(f"✅ 成功获取 {len(newslist)} 条热搜话题")
                return newslist[:MAX_TOPICS]
            else:
                print(f"❌ API返回错误: {data.get('msg', '未知错误')}")
                if attempt < max_retries:
                    import time
                    wait_time = attempt * 5  # 递增等待时间
                    print(f"  等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    
        except requests.exceptions.Timeout:
            print(f"⏱️ 请求超时 (超过{timeout}秒)")
            if attempt < max_retries:
                import time
                wait_time = attempt * 5
                print(f"  等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
        except Exception as e:
            print(f"❌ API调用失败: {str(e)}")
            if attempt < max_retries:
                import time
                wait_time = attempt * 5
                print(f"  等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
    
    print("❌ 所有重试均失败")
    return []

def search_background_info(topic_title):
    """
    搜索热点背景信息
    注意: 这里需要使用Claude的search_web工具
    在实际运行时,Claude会自动调用search_web
    """
    # 这是一个占位函数,实际执行时由Claude的search_web工具完成
    return f"关于「{topic_title}」的背景信息将通过web搜索获取"

def analyze_topic(topic, rank):
    """
    分析单个热搜话题
    使用AI评分: 有趣度(80%) + 有用度(20%)
    """
    print(f"  🔍 分析第 {rank} 名: {topic['hotword']}")
    
    # 这里是简化版评分逻辑
    # 实际运行时,Claude会使用AI进行深度分析
    
    # 基于热度值进行初步评分
    heat_num = topic.get('hotwordnum', '0').strip()
    heat_num = int(re.sub(r'[^\d]', '', heat_num)) if heat_num else 0
    
    # 有趣度评分 (基于热度和标签)
    interesting_score = min(80, (heat_num // 10000) + 40)
    if topic.get('hottag') in ['热', '新', '爆']:
        interesting_score = min(80, interesting_score + 10)
    
    # 有用度评分 (需要AI分析,这里给默认值)
    useful_score = 15
    
    # 总分计算
    total_score = interesting_score * 0.8 + useful_score * 0.2
    
    return {
        "rank": rank,
        "title": topic['hotword'],
        "heat_value": topic.get('hotwordnum', '未知'),
        "tag": topic.get('hottag', ''),
        "background": f"「{topic['hotword']}」相关背景信息",
        "timeline": [
            "事件起因: 待AI分析",
            "事件发展: 待AI分析",
            "当前状态: 待AI分析"
        ],
        "scores": {
            "interesting": interesting_score,
            "useful": useful_score,
            "total": round(total_score, 1)
        },
        "product_ideas": generate_product_ideas(topic['hotword'], total_score)
    }

def generate_product_ideas(topic_title, score):
    """
    生成产品创意
    实际运行时由Claude AI生成
    """
    # 这是示例创意,实际会由AI生成
    if score >= 60:
        return [
            {
                "name": f"{topic_title[:10]}相关产品",
                "features": [
                    "核心功能1: 待AI生成",
                    "核心功能2: 待AI生成",
                    "核心功能3: 待AI生成"
                ],
                "target_users": "目标用户群体待AI分析"
            }
        ]
    else:
        return []

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
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', filepath])
        else:  # Linux
            subprocess.run(['xdg-open', filepath])
        print("🌐 已在浏览器中打开报告")
    except Exception as e:
        print(f"⚠️ 无法自动打开报告: {str(e)}")
        print(f"请手动打开: {filepath}")

def main():
    """主执行流程"""
    print("=" * 60)
    print("🚀 微博热搜产品创意分析器")
    print("=" * 60)
    
    # Step 1: 获取热搜榜单
    hot_searches = fetch_weibo_hot_search()
    
    if len(hot_searches) < MIN_TOPICS:
        print(f"\n❌ 获取的热搜数量不足({len(hot_searches)}条),需要至少{MIN_TOPICS}条")
        return
    
    # Step 2-4: 分析每个话题
    print(f"\n🔬 开始分析 {len(hot_searches)} 个热搜话题...")
    topics_data = []
    
    for idx, topic in enumerate(hot_searches, 1):
        analyzed_topic = analyze_topic(topic, idx)
        topics_data.append(analyzed_topic)
    
    # Step 5: 生成HTML报告
    analysis_date = datetime.now().strftime("%Y-%m-%d")
    report_path = generate_html_report(topics_data, analysis_date)
    
    # Step 6: 自动打开报告
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
