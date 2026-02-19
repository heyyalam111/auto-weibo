#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微博热搜获取工具 - 多备用方案
"""

import requests
import json
import time
from datetime import datetime

class WeiboHotSearch:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://weibo.com',
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        self.api_keys = [
            '76f000a3377212e17c8f5d716761f2f4',  # 备用key
        ]

    def get_from_weibo(self):
        """方案1: 微博官方接口"""
        urls = [
            'https://weibo.com/ajax/side/hotSearch',
            'https://weibo.com/ajax/statuses/hot/recommend',
        ]
        for url in urls:
            try:
                resp = requests.get(url, headers=self.headers, timeout=10)
                resp.encoding = 'utf-8'
                data = resp.json()
                if data.get('ok') == 1:
                    return self._parse_weibo_data(data)
            except Exception as e:
                print(f"Weibo API error: {e}")
                continue
        return None

    def _parse_weibo_data(self, data):
        """解析微博数据"""
        hot_searches = []
        realtime = data.get('data', {}).get('realtime', [])
        for item in realtime[:20]:
            word = item.get('word', '')
            if word:
                hot_searches.append({
                    'word': word,
                    'num': item.get('num', 0)
                })

        # 政府热搜
        hotgovs = data.get('data', {}).get('hotgovs', [])
        for item in hotgovs[:5]:
            word = item.get('word', '')
            if word:
                hot_searches.append({
                    'word': word,
                    'num': item.get('num', 0)
                })
        return hot_searches

    def get_from_tianxing(self):
        """方案2: 天行数据API (备用)"""
        api_url = "https://apis.tianapi.com/weibohot/index"
        for key in self.api_keys:
            try:
                for attempt in range(3):
                    resp = requests.get(api_url, params={'key': key}, timeout=10)
                    data = resp.json()
                    if data.get('code') == 200:
                        newslist = data.get('result', {}).get('newslist', [])
                        if newslist:  # 有数据才返回
                            return [{'word': item.get('word', ''), 'num': item.get('hotword_num', 0)} for item in newslist[:20]]
                        else:
                            print(f"Tianxing: 返回数据为空 (code=200, items=0)")
                            return None
                    elif data.get('code') != 200:
                        print(f"Tianxing API error: {data.get('msg')}")
                        break
                    time.sleep(5)  # 重试间隔
            except Exception as e:
                print(f"Tianxing error: {e}")
        return None

    def get_hot_search(self):
        """获取热搜 - 自动尝试多个方案"""
        print("正在获取微博热搜...")

        # 方案1: 微博官方接口 (优先)
        print("尝试方案1: 微博官方接口...")
        result = self.get_from_weibo()
        if result and len(result) >= 5:
            print(f"[OK] 方案1成功: 获取{len(result)}条热搜")
            return result
        print("[X] 方案1失败")

        # 方案2: 天行数据API (备用)
        print("尝试方案2: 天行数据API...")
        result = self.get_from_tianxing()
        if result and len(result) >= 5:
            print(f"[OK] 方案2成功: 获取{len(result)}条热搜")
            return result
        print("[X] 方案2失败")

        print("所有方案均失败")
        return None

if __name__ == '__main__':
    weibo = WeiboHotSearch()
    result = weibo.get_hot_search()
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
