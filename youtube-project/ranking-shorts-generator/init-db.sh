#!/bin/bash

# 데이터베이스 초기화 스크립트
# 사용법:
#   ./init-db.sh          # 테이블만 생성 (데이터 유지)
#   ./init-db.sh --reset  # 완전 초기화 (데이터 삭제)

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_PATH="$PROJECT_ROOT/backend/app.db"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  데이터베이스 초기화${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd "$PROJECT_ROOT/backend"

# --reset 옵션 확인
if [ "$1" == "--reset" ]; then
    echo -e "${YELLOW}⚠️  완전 초기화 모드${NC}"
    echo -e "${RED}모든 데이터가 삭제됩니다!${NC}"
    echo ""
    read -p "계속하시겠습니까? (yes/no): " -r
    echo

    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo -e "${YELLOW}취소되었습니다.${NC}"
        exit 0
    fi

    # 백업 생성
    if [ -f "$DB_PATH" ]; then
        BACKUP_PATH="$DB_PATH.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$DB_PATH" "$BACKUP_PATH"
        echo -e "${GREEN}✓ 백업 생성: $BACKUP_PATH${NC}"
    fi

    # 데이터베이스 파일 삭제
    rm -f "$DB_PATH"
    echo -e "${GREEN}✓ 기존 데이터베이스 삭제 완료${NC}"
    echo ""
fi

# 데이터베이스 초기화
echo -e "${YELLOW}데이터베이스 테이블 생성 중...${NC}"

python -c "
from app.db.base import Base
from app.database import engine
from app.models import Search, Video, Project, ProjectVideo, FinalVideo

# 테이블 생성
Base.metadata.create_all(bind=engine)

# 결과 확인
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()

print('생성된 테이블:')
for table in tables:
    print(f'  ✓ {table}')
print(f'\\n총 {len(tables)}개 테이블')
"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  데이터베이스 초기화 완료! ✓${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}데이터베이스 위치:${NC}"
    echo -e "  $DB_PATH"
    echo ""

    # 파일 정보
    if [ -f "$DB_PATH" ]; then
        FILE_SIZE=$(du -h "$DB_PATH" | cut -f1)
        echo -e "${YELLOW}파일 크기:${NC} $FILE_SIZE"
    fi

    echo ""
    echo -e "${YELLOW}다음 명령어:${NC}"
    echo -e "  데이터 확인 → ${BLUE}sqlite3 $DB_PATH \"SELECT * FROM searches;\"${NC}"
    echo -e "  서비스 시작 → ${BLUE}./start-dev.sh${NC}"
else
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}  초기화 실패!${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}문제 해결:${NC}"
    echo -e "  1. Python 환경 확인: python --version"
    echo -e "  2. 패키지 설치 확인: pip install -r requirements.txt"
    echo -e "  3. 권한 확인: ls -l backend/"
    exit 1
fi
