# Day 8(M2 Day04) 확장 — 브라우저를 직접 조작하는 도구 (Playwright)
# 실행: uv run python notebook/M2-도구에이전트/Day08-MultiToolAgent구현-브라우저도구-실습.py
#
# 배우는 대상은 "위키백과의 정보"가 아니라 "브라우저를 조작하는 방법"이다.
# 정보만 필요하다면 위키백과는 API가 더 빠르고 안정적이다. 실무라면 API를 쓴다.
# 도구 1(click_and_check)은 requests로는 아예 불가능한 일이고, 도구 2는 조작 패턴 연습이다.
#
# TODO를 채운 뒤 실행한다. 선택자·locator·대기 기준 설명은 정답 파일에 있다.

import os
import sys
import urllib.parse

sys.stdout.reconfigure(encoding="utf-8")

os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from playwright.sync_api import sync_playwright
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from dotenv import load_dotenv

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")


# 도구 1. 동적 페이지 조작 — 버튼을 눌러야 없던 요소가 생긴다
@tool
def click_and_check() -> str:
    """실습용 데모 페이지에서 버튼을 클릭하고, 로딩 후 나타나는 텍스트를 확인한다."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto("https://the-internet.herokuapp.com/dynamic_loading/1")
                # TODO: "#start button"을 클릭하고, "#finish h4"가 나타날 때까지 기다린 뒤
                #       그 텍스트를 text 변수에 담으세요
                page.locator("#start button").click()
                text = page.wait_for_selector("#finish h4").text_content().strip()

                return f"버튼 클릭 후 나타난 텍스트: {text}"
            finally:
                browser.close()
    except Exception as e:
        return f"클릭 실패: {type(e).__name__} - {str(e).splitlines()[0][:150]}"


# 도구 2. 조작 패턴 연습 — 이동·대기·분기·클릭·읽기
@tool
def search_wikipedia(query: str) -> str:
    """위키백과에서 검색어를 찾아 문서 제목과 첫 문단 요약을 반환한다."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                url = (
                    "https://ko.wikipedia.org/w/index.php?search="
                    + urllib.parse.quote(query)
                    + "&title=" + urllib.parse.quote("특수:검색", safe=":")
                )
                # TODO: url로 이동하고, "#firstHeading"이 나타날 때까지 기다리세요
                page.goto(url)
                page.wait_for_selector("#firstHeading")

                # TODO: ".mw-search-result-heading a"의 count()가 0보다 크면 first를 클릭하세요.
                #       클릭 뒤에는 wait_for_url("**/wiki/**")로 문서 페이지 도착을 확인한 다음,
                #       "#firstHeading"을 기다리세요.
                #       (왜 여기서만 URL로 기다리는지는 정답 파일 주석 참고)
                if page.locator(".mw-search-result-heading a").count() > 0:
                    page.locator(".mw-search-result-heading a").first.click()
                    page.wait_for_url("**/wiki/**")
                    page.wait_for_selector("#firstHeading")

                #서브 페이지가 열린 다음
                title = page.locator("#firstHeading").text_content().strip()
                summary = ""
                paragraphs = page.locator("#mw-content-text p")
                for i in range(paragraphs.count()):
                    text = (paragraphs.nth(i).text_content() or "").strip()
                    if text:
                        summary += text
                        break

                return f"[{title}] {summary[:200]}"
            finally:
                browser.close()
    except Exception as e:
        return f"검색 실패: {type(e).__name__} - {str(e).splitlines()[0][:150]}"


# TODO: click_and_check, search_wikipedia 두 도구로 browser_agent를 만드세요
browser_agent = create_agent(llm, tools=[click_and_check, search_wikipedia])

print("===== 1. 버튼 클릭 (requests로는 불가능한 동적 페이지) =====")
# TODO: "실습용 데모 페이지에서 버튼을 눌러보고 뭐가 나오는지 확인해줘"를 browser_agent에
#       넣어 result에 담고, 최종 답을 출력하세요
# agent.invoke() -> 요청 -> tool_calls -> [ tool action -> observation ] -> 최종 요청
# 필요하면 [tool action -> observation] 반복
# result = browser_agent.invoke({
#     "messages": [{"role": "user",
#                   "content": "실습용 데모 페이지에서 버튼을 눌러보고 뭐가 나오는지 확인해줘"
#                   }]
# })

# print(f"최종 답 {result['messages'][-1].content}")

print()
print("===== 2. 위키백과 검색 (조작 패턴 연습 — 실무라면 API를 쓴다) =====")
# TODO: "위키백과에서 랭체인(LangChain)이 뭔지 찾아줘"를 실행하고 최종 답을 출력하세요
result = browser_agent.invoke({
    "messages": [{"role": "user",
                #   "content": "위키백과에서 랭체인(LangChain)이 뭔지 찾아줘"
                  "content": "암묵지를 찾아줘"
                  }]
})

print(f"최종 답 {result['messages'][-1].content}")


print()
print("===== 3. 실행 과정 — 어떤 도구가 호출됐는지 =====")
# TODO: result의 messages를 순회하며 pretty_print()로 실행 과정을 확인하세요
for m in result['messages']:
    m.pretty_print()