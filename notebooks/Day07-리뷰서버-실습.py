# Day 7(M2 Day03) 실습
# 실행: uv run python notebooks\Day07-리뷰서버-실습.py
#
# 목표: MCP 서버(review_server.py)에 연결해 도구를 불러와 실행하고,
#       회사이름으로 리뷰를 제공하는 MCP 툴을 정의한다.


# Host프로그램 작성

import asyncio
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from dotenv import load_dotenv

os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

REVIEW_SERVER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "review_server.py")

async def main():
    # llm API 연결
    load_dotenv()
    llm = ChatOpenAI(model='gpt-4o-mini')

    # 클라이언트가 연결하려는 서버 정보를 포함해 클라이언트 객체를 생성한다.
    client = MultiServerMCPClient({"review": {"command": sys.executable, "args": [REVIEW_SERVER], "transport": "stdio"}})

    tools = await client.get_tools()          # 서버 도구 → LangChain 도구로 변환
    print("서버로부터 받은 도구 목록:", [t.name for t in tools])

    # LLM에 툴 바인딩
    llm_with_tools = llm.bind_tools(tools)

    # 툴 맵 생성
    tool_map = {t.name: t for t in tools}    

    # 메시지로 생성
    question = '라인 회사 리뷰해줘!'
    messages = [HumanMessage(question)]

    # LLM에 툴 콜링
    ai_msg = llm_with_tools.invoke(messages)
    # print(f'툴콜링 결과 : {ai_msg}')

    # 툴 콜링 결과를 메시지에 추가
    messages.append(ai_msg)

    # 툴실행
    for tc in ai_msg.tool_calls:
        result = await tool_map[tc['name']].ainvoke(tc['args'])
        # print(f"툴 호출 : {tc['name']} 실행결과 : {result}")
        messages.append(ToolMessage(str(result), tool_call_id=tc['id']))

    # 최종 응답 호출
    final = llm_with_tools.invoke(messages)
    print('최종 응답 : ', final.content)

if __name__ == "__main__":
    asyncio.run(main())