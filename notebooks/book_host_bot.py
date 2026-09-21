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
BOOK_SERVER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "book_server.py")

async def main():
    # 환경로딩 & openai API 연결
    load_dotenv()
    llm = ChatOpenAI(model='gpt-4o-mini')
   
    # MCP 서버 연결
    client = MultiServerMCPClient({"review": {"command": sys.executable, "args": [BOOK_SERVER], "transport": "stdio"}})

    # MCP 도구 확인
    tools = await client.get_tools()          # 서버 도구 → LangChain 도구로 변환
    print("서버로부터 받은 도구 목록:", [t.name for t in tools])

    # llm에 도구 바인딩
    llm_with_tools = llm.bind_tools(tools)

    # 툴 맵 생성
    tool_map = {t.name: t for t in tools}

    questions = ['베스트셀러 1위가 뭐야?', '헤세가 쓴 책 뭐 있어?']

    for q in questions:
        # HumanMessage 생성
        messages = [HumanMessage(q)]

        # 툴콜즈
        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

        # 툴실행
        for t in ai_msg.tool_calls:
            t_result = await tool_map[t['name']].ainvoke(t['args'])
            messages.append(ToolMessage(str(t_result), tool_call_id=t['id']))

        #최종요청
        result = llm_with_tools.invoke(messages) # [ HM, AI_MSG, TM ]
        print('질문: ', q)
        print('응답: ', result.content)


if __name__ == '__main__':
    asyncio.run(main())
