# Day 7(M2 Day03) 실습 — MCP 연결과 FC vs MCP 비교
# 실행: uv run python notebook/M2-도구에이전트/Day07-MCP연결과FCvsMCP비교-실습.py
#
# 목표: MCP 서버(math_server.py)에 연결해 도구를 불러와 실행하고,
#       같은 기능(곱셈)을 Function Calling과 MCP 두 방식으로 만들어 비교한다.
#
# 참고: Windows·Jupyter에서는 MCP stdio 연결이 서브프로세스 제약으로 막힌다.
#       그래서 오늘 실습은 노트북이 아니라 .py 스크립트 + asyncio.run()으로 실행한다.

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

# math_server.py·review_server.py의 절대경로 (실행 위치가 어디든 안전)
MATH_SERVER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "math_server.py")
# REVIEW_SERVER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "review_server.py")


# Part 2에서 쓸 Function Calling 버전 도구 (앱 코드 안에 직접 정의)


# Part 2-확장·Part 3에서 쓸 FC 버전 도구 (M2 Day02(Day06)와 동일한 mock)

async def main():
    # llm API 연결
    load_dotenv()
    llm = ChatOpenAI(model='gpt-4o-mini')

    # 클라이언트가 연결하려는 서버 정보를 포함해 클라이언트 객체를 생성한다.
    client = MultiServerMCPClient({"math": {"command": sys.executable, "args": [MATH_SERVER], "transport": "stdio"}})

    tools = await client.get_tools()          # 서버 도구 → LangChain 도구로 변환
    print("서버로부터 받은 도구 목록:", [t.name for t in tools])

    # LLM에 툴 바인딩
    llm_with_tools = llm.bind_tools(tools)

    # 툴 맵 생성
    tool_map = {t.name: t for t in tools}    

    # 메시지로 생성
    question = '3 더하기 12는'
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

# # ===== Part 2-확장. 다른 도메인에 적용하기 — 회사 리뷰 도구도 FC vs MCP로 review_server.py =====
# print()
# print("===== Part 2-확장. 회사 리뷰 도구 — FC vs MCP =====")


