from mcp.server.fastmcp import FastMCP

# uv add mcp[cli]

# 서버 : 도구

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    "두 수를 더한다."
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    "두 수를 곱한다."
    return a * b

if __name__ == "__main__":
    mcp.run(transport="stdio")