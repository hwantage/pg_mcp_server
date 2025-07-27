from mcp.server.fastmcp import FastMCP
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
mcp = FastMCP("pg_mcp")

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

# 사용자 이름으로 조회하는 함수
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
        # query = """
        #     SELECT *
        #     FROM my_db.users
        #     WHERE empname = %s
        # """
        # cur.execute(query, (empname.strip(),))
        # result = cur.fetchall()

        # 디버그용 더미 데이터 바인딩
        result = [
            (1, "개발팀", "홍길동"),
            (2, "인사팀", "이순신"),
            (3, "영업팀", "김철수")
        ]
        
        # 결과를 딕셔너리 형태로 변환
        formatted_result = []
        for row in result:
            formatted_result.append(
                {
                    "userid": row[0],
                    "deptname": row[1],
                    "empname": row[2]
                }
            )
        
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

def main():
    mcp.run()

if __name__ == "__main__":
    main()
