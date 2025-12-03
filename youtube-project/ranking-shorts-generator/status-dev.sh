#!/bin/bash

# 개발 환경 상태 확인 스크립트
# 사용법: ./status-dev.sh

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 프로젝트 루트 디렉토리
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Ranking Shorts Generator - 서비스 상태${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 1. Redis 상태
echo -e "${YELLOW}[1/4] Redis${NC}"
if docker ps | grep -q ranking-redis; then
    echo -e "  상태: ${GREEN}● 실행 중${NC}"
    echo -e "  포트: 6379"
    echo -e "  연결: $(docker exec ranking-redis redis-cli ping 2>/dev/null || echo 'FAIL')"
else
    echo -e "  상태: ${RED}○ 중지됨${NC}"
fi
echo ""

# 2. Backend 상태
echo -e "${YELLOW}[2/4] Backend (FastAPI)${NC}"
if [ -f "$PROJECT_ROOT/logs/backend.pid" ]; then
    BACKEND_PID=$(cat "$PROJECT_ROOT/logs/backend.pid")
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "  상태: ${GREEN}● 실행 중${NC}"
        echo -e "  PID: $BACKEND_PID"
        echo -e "  URL: http://localhost:8000"

        # Health check
        HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null || echo "FAIL")
        if [ "$HEALTH" != "FAIL" ]; then
            echo -e "  헬스체크: ${GREEN}✓ 정상${NC}"
        else
            echo -e "  헬스체크: ${RED}✗ 응답 없음${NC}"
        fi
    else
        echo -e "  상태: ${RED}○ 중지됨 (PID 파일은 존재)${NC}"
    fi
else
    echo -e "  상태: ${RED}○ 중지됨${NC}"
fi
echo ""

# 3. Celery Worker 상태
echo -e "${YELLOW}[3/4] Celery Worker${NC}"
if [ -f "$PROJECT_ROOT/logs/celery.pid" ]; then
    CELERY_PID=$(cat "$PROJECT_ROOT/logs/celery.pid")
    if kill -0 $CELERY_PID 2>/dev/null; then
        echo -e "  상태: ${GREEN}● 실행 중${NC}"
        echo -e "  PID: $CELERY_PID"

        # Worker 수 확인
        WORKER_COUNT=$(ps aux | grep "celery" | grep "worker" | grep -v grep | wc -l)
        echo -e "  워커 수: $WORKER_COUNT"
    else
        echo -e "  상태: ${RED}○ 중지됨 (PID 파일은 존재)${NC}"
    fi
else
    echo -e "  상태: ${RED}○ 중지됨${NC}"
fi
echo ""

# 4. Frontend 상태
echo -e "${YELLOW}[4/4] Frontend (React)${NC}"
if [ -f "$PROJECT_ROOT/logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PROJECT_ROOT/logs/frontend.pid")
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "  상태: ${GREEN}● 실행 중${NC}"
        echo -e "  PID: $FRONTEND_PID"

        # 포트 확인
        if lsof -ti:3000 >/dev/null 2>&1; then
            echo -e "  URL: http://localhost:3000"
        elif lsof -ti:5173 >/dev/null 2>&1; then
            echo -e "  URL: http://localhost:5173"
        fi
    else
        echo -e "  상태: ${RED}○ 중지됨 (PID 파일은 존재)${NC}"
    fi
else
    echo -e "  상태: ${RED}○ 중지됨${NC}"
fi
echo ""

# 포트 사용 상태
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}포트 사용 상태:${NC}"
echo ""

for port in 3000 5173 6379 8000; do
    if lsof -ti:$port >/dev/null 2>&1; then
        PID=$(lsof -ti:$port)
        PROCESS=$(ps -p $PID -o comm= 2>/dev/null || echo "unknown")
        echo -e "  $port → ${GREEN}사용 중${NC} (PID: $PID, Process: $PROCESS)"
    else
        echo -e "  $port → ${RED}사용 안 함${NC}"
    fi
done

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}명령어:${NC}"
echo -e "  서비스 시작 → ${BLUE}./start-dev.sh${NC}"
echo -e "  서비스 중지 → ${BLUE}./stop-dev.sh${NC}"
echo -e "  로그 확인   → ${BLUE}tail -f logs/[backend|celery|frontend].log${NC}"
echo ""
