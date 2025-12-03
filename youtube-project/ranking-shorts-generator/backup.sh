#!/bin/bash

# 백업 스크립트
# 사용법: ./backup.sh

BACKUP_DIR="$HOME/ranking-shorts-backups"
DATE=$(date +%Y%m%d_%H%M%S)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔄 백업 시작..."

# 백업 디렉토리 생성
mkdir -p "$BACKUP_DIR"

# 백업 파일 생성
BACKUP_FILE="$BACKUP_DIR/ranking-shorts-$DATE.tar.gz"

# 중요한 데이터만 백업
tar -czf "$BACKUP_FILE" \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='logs/*.log' \
    -C "$(dirname "$PROJECT_ROOT")" \
    "$(basename "$PROJECT_ROOT")"

echo "✅ 백업 완료!"
echo "📁 위치: $BACKUP_FILE"
echo "📊 크기: $(du -h "$BACKUP_FILE" | cut -f1)"

# 30일 이상 된 백업 자동 삭제
find "$BACKUP_DIR" -name "ranking-shorts-*.tar.gz" -mtime +30 -delete

echo ""
echo "📂 전체 백업 목록:"
ls -lh "$BACKUP_DIR"
