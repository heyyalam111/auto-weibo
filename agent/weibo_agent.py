#!/usr/bin/env python3
"""
微博热搜分析 Agent 主程序
支持 MiniMax 兼容 Anthropic API
"""
import os
import sys
import json
from anthropic import Anthropic
from agent.tools import get_weibo_hotsearch_tool, generate_html_report_tool
from agent.prompts import SYSTEM_PROMPT, USER_PROMPT


def create_anthropic_client():
    """
    创建 Anthropic 客户端
    支持自定义 API 端点 (MiniMax 兼容)
    """
    # 从环境变量获取配置
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("错误: 未设置 ANTHROPIC_API_KEY 环境变量")
        print("请设置: export ANTHROPIC_API_KEY=your_api_key")
        sys.exit(1)

    # API 端点 (MiniMax 或官方)
    base_url = os.environ.get("ANTHROPIC_API_URL", "https://api.minimaxi.com/anthropic")

    # 模型选择
    model = os.environ.get("ANTHROPIC_MODEL", "MiniMax-M2.5")

    print(f"[*] API 端点: {base_url}")
    print(f"[*] 使用模型: {model}")

    client = Anthropic(
        api_key=api_key,
        base_url=base_url,
    )

    return client, model


def run_agent():
    """运行 Agent"""
    print("=" * 60)
    print("🚀 微博热搜产品创意分析 Agent")
    print("=" * 60)

    # 1. 初始化客户端
    client, model = create_anthropic_client()

    # 2. 定义工具
    tools = [get_weibo_hotsearch_tool, generate_html_report_tool]

    # 3. 构建消息
    messages = [
        {"role": "user", "content": USER_PROMPT}
    ]

    print("\n[*] 开始执行分析...")

    # 4. 运行 Agent
    try:
        with client.beta.messages.tool_runner(
            model=model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        ) as runner:
            for event in runner:
                if event.type == "message_start":
                    print("\n[*] 助手消息开始")
                elif event.type == "content_block_start":
                    print("", end="", flush=True)
                elif event.type == "content_block_delta":
                    if hasattr(event.delta, 'text'):
                        print(event.delta.text, end="", flush=True)
                elif event.type == "tool_use":
                    print(f"\n\n[🔧 调用工具: {event.name}]")
                    if event.name == "get_weibo_hotsearch":
                        result = get_weibo_hotsearch_tool(max_count=20)
                        print(f"    获取到热搜数据")
                        runner.add_tool_result(event.id, result)
                    elif event.name == "generate_html_report":
                        # 解析参数
                        input_json = event.input
                        if isinstance(input_json, dict):
                            analysis_data = json.dumps(input_json, ensure_ascii=False)
                        else:
                            analysis_data = str(input_json)
                        result = generate_html_report_tool(analysis_data)
                        print(f"    报告已生成: {result}")
                        runner.add_tool_result(event.id, result)
                elif event.type == "message_delta":
                    if hasattr(event.delta, 'text'):
                        print(event.delta.text, end="", flush=True)
                elif event.type == "message_stop":
                    print("\n\n[*] 分析完成!")

    except Exception as e:
        print(f"\n❌ 执行错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """主入口"""
    run_agent()


if __name__ == "__main__":
    main()
