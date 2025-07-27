# PostgreSQL MCP 서버 예제

이 프로젝트는 PostgreSQL 데이터베이스와 연동하여 사용자 정보를 조회하는 MCP(Model Context Protocol) 서버의 두 가지 구현 방식을 제공합니다.

## 📋 프로젝트 구조

```
pg_mcp/
├── pg_mcp.py          # STDIO 방식 MCP 서버
├── pg_mcp_sse.py      # SSE 방식 MCP 서버  
├── sample.env         # 환경변수 설정 예제
└── README.md          # 프로젝트 문서
```



## 🔍 두 방식의 차이점

### STDIO 방식 특징
- **통신 방식**: 표준 입출력(Standard Input/Output)을 통한 로컬 통신
- **사용 환경**: 운영체제 내에서 실행되는 응용 프로그램과 직접 연동
- **구현 복잡도**: 간단한 구현, 최소한의 설정 필요
- **성능**: 로컬 환경에서 빠른 통신, 네트워크 오버헤드 없음
- **용도**: 명령줄 도구, 로컬 MCP 클라이언트와의 직접 연동

### SSE 방식 특징
- **통신 방식**: HTTP 기반 Server-Sent Events를 통한 네트워크 통신
- **사용 환경**: 웹 브라우저와 웹 서버 간, 원격 클라이언트 지원
- **구현 복잡도**: 상대적으로 복잡, HTTP 서버 설정 필요
- **성능**: 네트워크 통신으로 인한 오버헤드 존재, 실시간 스트리밍 지원
- **용도**: 웹 기반 애플리케이션, 원격 접근, 실시간 데이터 푸시

### 상세 비교표

| **구분** | **STDIO 방식** | **SSE 방식** |
|----------|---------------|--------------|
| **통신 방식** | 표준 입출력 (로컬 I/O) | HTTP/SSE (네트워크 통신) |
| **연결 대상** | 로컬 MCP 클라이언트 | 웹 기반 클라이언트/원격 클라이언트 |
| **구현 난이도** | 간단 | 상대적으로 복잡 |
| **설정 요구사항** | 최소화 | HTTP 서버 설정 필요 |
| **접근성** | 로컬 시스템 내부만 | 네트워크를 통한 원격 접근 |
| **주요 장점** | 설정 간단, 빠른 통신 | 원격 접근, 웹 호환성 |
| **주요 단점** | 로컬 환경 제한 | 서버 설정 복잡, 네트워크 오버헤드 |
| **적합한 사용 사례** | 개발/테스트, 로컬 도구 | 프로덕션, 웹 서비스 |

## 🚀 주요 기능

- **사용자 이름으로 직원 정보 조회**: `search_user_by_name` 도구를 통해 직원 정보 검색
- **두 가지 서버 방식 지원**:
  - **STDIO 방식**: 표준 입출력을 통한 통신
  - **SSE 방식**: Server-Sent Events를 통한 웹 기반 통신

## 📦 설치 및 설정

### 1. 의존성 설치

```bash
pip install mcp psycopg2-binary python-dotenv starlette uvicorn
```

### 2. 환경변수 설정

`sample.env` 파일을 `.env`로 복사하고 실제 값으로 수정하세요:

```bash
cp sample.env .env
```

`.env` 파일 예시:
```env
# SSE 서버 설정
HOST=0.0.0.0
PORT=8000

# PostgreSQL 데이터베이스 설정
DB_NAME=your_database
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 3. PostgreSQL 데이터베이스 준비

SSE 방식을 사용하려면 다음과 같은 테이블 구조가 필요합니다:

```sql
CREATE SCHEMA IF NOT EXISTS my_db;

CREATE TABLE my_db.users (
    userid SERIAL PRIMARY KEY,
    deptname VARCHAR(100) NOT NULL,
    empname VARCHAR(100) NOT NULL
);

-- 테스트 데이터 삽입
INSERT INTO my_db.users (userid, deptname, empname) VALUES
(1, '개발팀', '홍길동'),
(2, '인사팀', '이순신'),
(3, '영업팀', '김철수');
```

## 🖥️ 사용 방법

### STDIO 방식 (pg_mcp.py)

테스트 목적으로 더미 데이터를 사용합니다. MCP 호스트 앱에 등록하여 사용합니다.

**서버 연결 테스트 방법:**
* cursor ai IDE 에서 설정 > Tools and Integrations 메뉴에서 새 mcp 서버를 등록합니다.
* 아래와 같이 mcp.json 파일에 서버를 등록합니다.
```json
{
  "mcpServers": {
    "pg_mcp": {
      "command": "python",
      "args": ["d:\\python\\pg_mcp\\pg_mcp.py"],
      "description": "PG MCP Server (STDIO 모드)"
    }
  }
}
```

### SSE 방식 (pg_mcp_sse.py)

실제 PostgreSQL 데이터베이스와 연동하여 웹 기반으로 서비스를 제공합니다. 

아래의 명령어로 MCP 서버를 실행합니다.
```bash
python pg_mcp_sse.py
```

**서버 연결 테스트 방법:**
- 서버 주소: `http://localhost:8000/sse`

* cursor ai IDE 에서 설정 > Tools and Integrations 메뉴에서 새 mcp 서버를 등록합니다.
* 아래와 같이 mcp.json 파일에 서버를 등록합니다.
```json
{
  "mcpServers": {
    "pg_mcp_sse": {
      "type": "http",
      "url": "http://127.0.0.1:8000/sse",
      "description": "PG MCP Server (HTTP 모드)"
    }
  }
}
```


## 🔧 API 사용법

### search_user_by_name 도구

직원 이름으로 사용자 정보를 조회합니다.

**매개변수:**
- `empname` (string): 검색할 직원 이름

**반환값:**
```json
[
  {
    "userid": 1,
    "deptname": "개발팀", 
    "empname": "홍길동"
  }
]
```

**오류 응답:**
```json
[
  {
    "error": "직원 이름을 입력해주세요."
  }
]
```


## 📄 라이선스

MIT
