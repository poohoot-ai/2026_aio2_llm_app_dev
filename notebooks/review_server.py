from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Review")

@mcp.tool()
def get_company_review(company: str) -> str:
    """회사의 재직자 리뷰 요약을 반환한다. company는 회사 이름(예: 카카오, 라인)."""
    reviews = {
        "카카오": "워라벨이 좋고 자율 출퇴근 문화, 성장 속도는 팀마다 다름",
        "라인": "글로벌 협업 기회가 많고, 일본어 소통이 잦은 편",
    }
    return reviews.get(company, "리뷰 정보가 없습니다.!!!")

if __name__ == "__main__":
    mcp.run(transport="stdio") # 로컬 stdio 대기