#!/bin/bash

# 기존 프로세스 종료
echo "Checking for existing processes..."

# 포트를 사용하는 프로세스 강제 종료
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Killing process on port 8000..."
    kill -9 $(lsof -t -i:8000) 2>/dev/null
fi

if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null ; then
    echo "Killing process on port 5173..."
    kill -9 $(lsof -t -i:5173) 2>/dev/null
fi

# 추가로 이름으로도 종료
pkill -f "uvicorn app.main:app" 2>/dev/null
pkill -f "vite dev" 2>/dev/null

sleep 2

# 백엔드 서버 실행
echo "Starting backend server..."
cd backend
source ../venv/bin/activate
uvicorn app.main:app --reload &
BACKEND_PID=$!

# 프론트엔드 서버 실행
echo "Starting frontend server..."
cd ../frontend
npm run dev -- --port 5173 &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Servers are running:"
echo "- Backend: http://localhost:8000"
echo "- Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"

# Ctrl+C 처리
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# 프로세스가 종료될 때까지 대기
wait