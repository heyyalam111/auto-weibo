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
    """创建 Anthropic 客户端"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("错误: 未设置 ANTHROPIC_API_KEY 环境变量")
        sys.exit(1)

    base_url = os.environ.get("ANTHROPIC_API_URL", "https://api.minimaxi.com/anthropic")
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
    print("微博热搜产品创意分析 Agent")
    print("=" * 60)

    client, model = create_anthropic_client()

    tools = [get_weibo_hotsearch_tool, generate_html_report_tool]
    messages = [{"role": "user", "content": USER_PROMPT}]

    print("\n[*] 开始执行分析...")

    try:
        # 使用 beta.messages.create 而非 tool_runner
        response = client.beta.messages.create(
            model=model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        )

        # 处理响应
        for content_block in response.content:
            if content_block.type == "text":
                print(content_block.text)
            elif content_block.type == "tool_use":
                tool_name = content_block.name
                tool_input = content_block.input

                print(f"\n\n[调用工具: {tool_name}]")

                if tool_name == "get_weibo_hotsearch":
                    result = get_weibo_hotsearch_tool(max_count=20)
                    print(f"    获取到热搜数据")
                elif tool_name == "generate_html_report":
                    analysis_data = json.dumps(tool_input, ensure_ascii=False)
                    result = generate_html_report_tool(analysis_data)
                    print(f"    报告已生成")

                # 将工具结果添加到响应中继续对话
                messages.append({"role": "user", "content": json.dumps({"result": result})})

                # 再次调用获取最终结果
                response = client.beta.messages.create(
                    model=model,
                    max_tokens=4096,
                    system=SYSTEM_PROMPT,
                    tools=tools,
                    messages=messages
                )

                for content_block in response.content:
                    if hasattr(content_block, 'text'):
                        print(content_block.text)

        print("\n\n[*] 分析完成!")

    except Exception as e:
        print(f"\n执行错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_agent()
