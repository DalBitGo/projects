#!/bin/bash

# 개발 환경 전체 실행 스크립트
# 사용법: ./start-dev.sh

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 프로젝트 루트 디렉토리
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Ranking Shorts Generator - 개발 환경 시작${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 1. Redis 확인 및 실행
echo -e "${YELLOW}[1/4] Redis 상태 확인...${NC}"
if docker ps | grep -q ranking-redis; then
    echo -e "${GREEN}✓ Redis가 이미 실행 중입니다.${NC}"
else
    echo -e "${YELLOW}  Redis 컨테이너를 시작합니다...${NC}"
    if docker ps -a | grep -q ranking-redis; then
        docker start ranking-redis
    else
        docker run -d -p 6379:6379 --name ranking-redis redis:latest
    fi
    sleep 2
    echo -e "${GREEN}✓ Redis 시작 완료${NC}"
fi
echo ""

# 2. Backend 실행
echo -e "${YELLOW}[2/4] Backend 서버 시작...${NC}"
cd "$PROJECT_ROOT/backend"

# 가상환경 활성화 확인
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 데이터베이스 초기화 (테이블이 없는 경우에만)
if [ ! -f "app.db" ] || [ ! -s "app.db" ]; then
    echo -e "${YELLOW}  데이터베이스 초기화 중...${NC}"
    python -c "
from app.db.base import Base
from app.database import engine
from app.models import Search, Video, Project, ProjectVideo, FinalVideo
Base.metadata.create_all(bind=engine)
" 2>/dev/null || echo -e "${RED}  데이터베이스 초기화 실패 (수동으로 확인 필요)${NC}"
    echo -e "${GREEN}✓ 데이터베이스 초기화 완료${NC}"
fi

# Backend 백그라운드 실행
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../logs/backend.pid
echo -e "${GREEN}✓ Backend 시작 완료 (PID: $BACKEND_PID)${NC}"
echo -e "  URL: ${BLUE}http://localhost:8000${NC}"
echo -e "  로그: ${BLUE}logs/backend.log${NC}"
echo ""

# 3. Celery Worker 실행
echo -e "${YELLOW}[3/4] Celery Worker 시작...${NC}"
nohup celery -A celery_app worker --loglevel=info > ../logs/celery.log 2>&1 &
CELERY_PID=$!
echo $CELERY_PID > ../logs/celery.pid
echo -e "${GREEN}✓ Celery Worker 시작 완료 (PID: $CELERY_PID)${NC}"
echo -e "  로그: ${BLUE}logs/celery.log${NC}"
echo ""

# 4. Frontend 실행
echo -e "${YELLOW}[4/4] Frontend 개발 서버 시작...${NC}"
cd "$PROJECT_ROOT/frontend"
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../logs/frontend.pid

# Frontend가 시작될 때까지 대기
sleep 5

echo -e "${GREEN}✓ Frontend 시작 완료 (PID: $FRONTEND_PID)${NC}"
echo -e "  URL: ${BLUE}http://localhost:3000${NC} (또는 http://localhost:5173)"
echo -e "  로그: ${BLUE}logs/frontend.log${NC}"
echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  모든 서비스가 시작되었습니다! 🚀${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}실행 중인 서비스:${NC}"
echo -e "  • Redis       → localhost:6379"
echo -e "  • Backend     → http://localhost:8000"
echo -e "  • Celery      → 백그라운드 (8 workers)"
echo -e "  • Frontend    → http://localhost:3000"
echo ""
echo -e "${YELLOW}로그 실시간 확인:${NC}"
echo -e "  Backend  → ${BLUE}tail -f logs/backend.log${NC}"
echo -e "  Celery   → ${BLUE}tail -f logs/celery.log${NC}"
echo -e "  Frontend → ${BLUE}tail -f logs/frontend.log${NC}"
echo ""
echo -e "${YELLOW}서비스 중지:${NC}"
echo -e "  ${BLUE}./stop-dev.sh${NC}"
echo ""
