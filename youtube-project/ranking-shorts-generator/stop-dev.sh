#!/bin/bash

# 개발 환경 전체 중지 스크립트
# 사용법: ./stop-dev.sh

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
echo -e "${BLUE}  Ranking Shorts Generator - 개발 환경 중지${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Frontend 중지
echo -e "${YELLOW}[1/4] Frontend 중지...${NC}"
if [ -f "$PROJECT_ROOT/logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PROJECT_ROOT/logs/frontend.pid")
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        echo -e "${GREEN}✓ Frontend 중지 완료 (PID: $FRONTEND_PID)${NC}"
    else
        echo -e "${YELLOW}  Frontend가 이미 중지되었습니다.${NC}"
    fi
    rm -f "$PROJECT_ROOT/logs/frontend.pid"
else
    echo -e "${YELLOW}  Frontend PID 파일을 찾을 수 없습니다.${NC}"
fi
echo ""

# Celery 중지
echo -e "${YELLOW}[2/4] Celery Worker 중지...${NC}"
if [ -f "$PROJECT_ROOT/logs/celery.pid" ]; then
    CELERY_PID=$(cat "$PROJECT_ROOT/logs/celery.pid")
    if kill -0 $CELERY_PID 2>/dev/null; then
        kill $CELERY_PID
        # Celery는 종료에 시간이 걸릴 수 있음
        sleep 2
        # 강제 종료가 필요한 경우
        if kill -0 $CELERY_PID 2>/dev/null; then
            kill -9 $CELERY_PID
        fi
        echo -e "${GREEN}✓ Celery Worker 중지 완료 (PID: $CELERY_PID)${NC}"
    else
        echo -e "${YELLOW}  Celery Worker가 이미 중지되었습니다.${NC}"
    fi
    rm -f "$PROJECT_ROOT/logs/celery.pid"
else
    echo -e "${YELLOW}  Celery PID 파일을 찾을 수 없습니다.${NC}"
fi
echo ""

# Backend 중지
echo -e "${YELLOW}[3/4] Backend 서버 중지...${NC}"
if [ -f "$PROJECT_ROOT/logs/backend.pid" ]; then
    BACKEND_PID=$(cat "$PROJECT_ROOT/logs/backend.pid")
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        echo -e "${GREEN}✓ Backend 중지 완료 (PID: $BACKEND_PID)${NC}"
    else
        echo -e "${YELLOW}  Backend가 이미 중지되었습니다.${NC}"
    fi
    rm -f "$PROJECT_ROOT/logs/backend.pid"
else
    echo -e "${YELLOW}  Backend PID 파일을 찾을 수 없습니다.${NC}"
fi
echo ""

# Redis 중지 (선택적)
echo -e "${YELLOW}[4/4] Redis 중지 여부 확인...${NC}"
if docker ps | grep -q ranking-redis; then
    read -p "Redis 컨테이너를 중지하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker stop ranking-redis
        echo -e "${GREEN}✓ Redis 중지 완료${NC}"
    else
        echo -e "${YELLOW}  Redis는 계속 실행됩니다.${NC}"
    fi
else
    echo -e "${YELLOW}  Redis가 실행 중이지 않습니다.${NC}"
fi
echo ""

# 추가 정리: 포트를 점유하고 있는 프로세스 종료
echo -e "${YELLOW}추가 정리 중...${NC}"

# 8000 포트 정리 (Backend)
if lsof -ti:8000 >/dev/null 2>&1; then
    echo -e "${YELLOW}  포트 8000을 점유 중인 프로세스 종료...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
fi

# 3000 포트 정리 (Frontend)
if lsof -ti:3000 >/dev/null 2>&1; then
    echo -e "${YELLOW}  포트 3000을 점유 중인 프로세스 종료...${NC}"
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
fi

# 5173 포트 정리 (Vite)
if lsof -ti:5173 >/dev/null 2>&1; then
    echo -e "${YELLOW}  포트 5173을 점유 중인 프로세스 종료...${NC}"
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  모든 서비스가 중지되었습니다! ✓${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
