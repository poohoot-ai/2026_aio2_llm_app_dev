from mcp.server.fastmcp import FastMCP
import sqlite3
import os

mcp = FastMCP("Book")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'my_database.db')

# 도구 정의
@mcp.tool()
def get_book_by_rank(rank: int) -> str:
    "베스트셀러 순위(rank)로 책 정보를 조회한다."

    # 쿼리 준비
    select_sql = "SELECT rank, title, author, price FROM books WHERE rank = ?"

    # DB연결
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # select sql
        cursor.execute(select_sql, (rank,))
        row = cursor.fetchone()

        if row is None :
            return f'{rank}의 책 정보를 찾을 수 없습니다.'

        book_rank, title, author, price = row
        return f'{book_rank}위 : {title} / {author} / {price:,}원'
    except Exception as e:
        print(str(e))
    finally: # 예외 발생 여부와 무관하게 항상 실행
        conn.close()


@mcp.tool()
def search_book(keyword: str) -> str:
    "제목이나 저자에 특정 키워드가 들어간 책 정보를 조회한다."

    # 쿼리 준비
    select_sql = "SELECT rank, title, author, price FROM books WHERE title LIKE ? OR author LIKE ?"

    # DB연결
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 쿼리실행
    try:    
        cursor.execute(select_sql, (f'%{keyword}%', f'%{keyword}%')) # title like '%최태성%' 
        rows = cursor.fetchall()    

        if not rows : # falsy 한 값들
            return f'{keyword}가 포함된 책 정보를 찾을 수 없습니다.'
        
        return '\n'.join(f'{r}위 : {title} / {author} / {price:,}원' for r, title, author, price in rows)

    except Exception as e:
        print(str(e))
    finally: # 예외 발생 여부와 무관하게 항상 실행
        conn.close()

if __name__ == "__main__":
    mcp.run(transport='stdio')