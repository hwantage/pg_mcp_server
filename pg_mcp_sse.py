from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
import uvicorn
import psycopg2
import json
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수에서 설정값 읽기
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# FastMCP 서버 초기화
mcp = FastMCP("pg_mcp_sse")

# PostgreSQL 연결 설정
def get_db_connection():
    """PostgreSQL 데이터베이스 연결을 생성합니다."""
    try:
        return psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT,
            connect_timeout=10
        )
    except Exception as e:
        raise Exception(f"데이터베이스 연결 실패: {str(e)}")

@mcp.tool()
def search_user_by_name(empname: str) -> str:
    """
    사용자 이름으로 직원 정보를 조회합니다.
    Args:
        empname: 검색할 직원 이름
    Returns:
        직원 정보 JSON 문자열 (userid, deptname, empname)
    """
    if not empname or not empname.strip():
        return json.dumps([{"error": "직원 이름을 입력해주세요."}], ensure_ascii=False, indent=2)
    
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # SQL 쿼리 실행
        query = """
            SELECT *
            FROM my_db.users
            WHERE empname = %s
        """
        cur.execute(query, (empname.strip(),))
        result = cur.fetchall()
        
        # 결과를 딕셔너리 형태로 변환
        formatted_result = []
        for row in result:
            formatted_result.append({
                "userid": row[0],
                "deptname": row[1],
                "empname": row[2]
            })
        
        if not formatted_result:
            return json.dumps([{"message": f"'{empname}' 이름으로 등록된 직원을 찾을 수 없습니다."}], ensure_ascii=False, indent=2)
        
        return json.dumps(formatted_result, ensure_ascii=False, indent=2)
        
    except psycopg2.Error as e:
        return json.dumps([{"error": f"데이터베이스 오류: {str(e)}"}], ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps([{"error": f"조회 중 오류 발생: {str(e)}"}], ensure_ascii=False, indent=2)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Starlette 앱 설정
def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """
        Create a Starlette application that can server the provied mcp server with SSE.
    """
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
            await mcp_server.run(read_stream, write_stream, mcp_server.create_initialization_options())

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

if __name__ == "__main__":
    mcp_server = mcp._mcp_server

    # Bind SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)

    uvicorn.run(starlette_app, host=HOST, port=PORT)