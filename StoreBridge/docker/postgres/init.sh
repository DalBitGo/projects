#!/bin/bash
# PostgreSQL 초기화 스크립트
# Docker 컨테이너 시작 시 자동 실행됨

set -e

echo "🔧 PostgreSQL 초기 설정 중..."

# pg_hba.conf에 외부 연결 trust 규칙 추가
if ! grep -q "host all all 0.0.0.0/0 trust" /var/lib/postgresql/data/pg_hba.conf; then
    echo "host all all 0.0.0.0/0 trust" >> /var/lib/postgresql/data/pg_hba.conf
    echo "✅ pg_hba.conf에 외부 연결 trust 규칙 추가됨"
fi

# 설정 리로드
psql -U storebridge -d storebridge -c 'SELECT pg_reload_conf();' > /dev/null 2>&1 || true

echo "✅ PostgreSQL 초기 설정 완료"
