---
description: 分析微博热搜并提取产品创意
---

# 微博热搜产品创意分析器

## 执行步骤

### 1. 获取微博热搜数据
使用天行数据API获取当前微博热搜榜单：

```python
import requests
import json
from datetime import datetime

api_url = "https://apis.tianapi.com/weibohot/index"
api_key = "76f000a3377212e17c8f5d716761f2f4"

response = requests.get(api_url, params={"key": api_key}, timeout=10)
data = response.json()

if data.get("code") == 200:
    hot_searches = data.get("result", {}).get("newslist", [])[:20]
else:
    print(f"API错误: {data.get('msg')}")
```

### 2. 搜索每个热点的背景信息
对每个热搜话题使用 `search_web` 工具搜索背景信息。

### 3. AI分析并评分
对每个热点进行分析：
- **有趣度 (80分)**：话题性(30分) + 新奇性(25分) + 传播度(25分)
- **有用度 (20分)**：实用性(10分) + 市场需求(10分)
- **总分** = 有趣度 × 0.8 + 有用度 × 0.2

### 4. 提取产品创意
为每个热点提取1-3个产品创意，包含：
- 产品名称
- 核心功能（3-5个）
- 目标用户

### 5. 生成HTML报告
创建精美的HTML报告，包含：
- 分析概览
- 高分热点排行（≥60分）
- 详细分析列表（评分、时间线、产品创意）

保存到：`F:\CC SKILLLS\微博热搜提取\reports\微博热搜分析_{日期}_{时间}.html`

### 6. 自动打开报告
使用 PowerShell 打开生成的报告：

```powershell
Start-Process "报告文件路径.html"
```

## 注意事项
- 一次性完成所有步骤，不要中途询问
- API失败时自动重试3次
- 单个话题搜索失败时继续处理其他话题
- 最少需要5条热搜数据才能继续分析
