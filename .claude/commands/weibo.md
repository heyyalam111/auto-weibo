---
name: weibo
description: 分析微博热搜并提取产品创意
---

# 微博热搜产品创意分析器

请按照以下步骤分析当前的微博热搜榜单并提取产品创意：

## 第1步：获取微博热搜数据

使用天行数据API获取当前微博热搜榜单（最多20条）：

```python
import requests
import json
from datetime import datetime

api_url = "https://apis.tianapi.com/weibohot/index"
api_key = "76f000a3377212e17c8f5d716761f2f4"

try:
    response = requests.get(api_url, params={"key": api_key}, timeout=10)
    data = response.json()
    
    if data.get("code") == 200:
        hot_searches = data.get("result", {}).get("newslist", [])[:20]
        print(f"成功获取 {len(hot_searches)} 条热搜")
    else:
        print(f"API错误: {data.get('msg')}")
except Exception as e:
    print(f"请求失败: {e}")
```

## 第2步：搜索背景信息

对每个热搜话题使用 `search_web` 工具搜索背景信息，提取事件脉络。

## 第3步：AI分析并评分

对每个热点进行分析评分：
- **有趣度 (80分)**：话题性(30) + 新奇性(25) + 传播度(25)
- **有用度 (20分)**：实用性(10) + 市场需求(10)
- **总分** = 有趣度 × 0.8 + 有用度 × 0.2

## 第4步：提取产品创意

为每个热点提取1-3个产品创意：
- 产品名称（简洁有力）
- 核心功能（3-5个关键功能点）
- 目标用户（明确的用户画像）

## 第5步：生成HTML报告

创建精美的HTML报告，包含：
- 📊 分析概览（日期、总数、平均分、优秀/良好项目数）
- 🏆 高分热点排行（≥60分）
- 📱 详细分析列表（评分可视化、时间线、产品创意卡片）

**文件命名**：`微博热搜分析_{YYMMDD}_{HHMM}.html`  
**保存位置**：`F:\CC SKILLLS\微博热搜提取\reports\`

**样式要求**：
- 现代简洁设计，深色主题
- 响应式布局
- 评分可视化：≥80分金色、60-79分蓝色、<60分灰色

## 第6步：自动打开报告

使用 PowerShell 打开生成的报告：

```powershell
Start-Process "F:\CC SKILLLS\微博热搜提取\reports\微博热搜分析_YYMMDD_HHMM.html"
```

## 重要提示

⚠️ **静默执行协议**：
- 一次性完成所有步骤，不要中途询问
- API失败时自动重试3次（间隔5秒）
- 单个话题搜索失败时继续处理其他话题
- 最少需要5条热搜数据才能继续分析
- 禁止询问"是否继续"或"需要我继续吗"
