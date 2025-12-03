"""
YouTube API Quota 사용량 체크 도구
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.feed_operations import get_feed_stats
import sqlite3


DB_PATH = Path(__file__).parent.parent / "data" / "youtube.db"


def get_today_quota_usage() -> int:
    """오늘 사용한 API quota 조회"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 오늘 날짜
    today = datetime.now().date()

    cursor.execute("""
        SELECT SUM(api_quota_used)
        FROM feed_collection_history
        WHERE DATE(collected_at) = ?
    """, (today.isoformat(),))

    result = cursor.fetchone()[0]
    conn.close()

    return result if result else 0


def get_quota_history(days: int = 7):
    """최근 N일간 quota 사용 내역"""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    start_date = (datetime.now() - timedelta(days=days)).date()

    cursor.execute("""
        SELECT
            DATE(collected_at) as date,
            SUM(api_quota_used) as total_quota,
            COUNT(*) as collection_count
        FROM feed_collection_history
        WHERE DATE(collected_at) >= ?
        GROUP BY DATE(collected_at)
        ORDER BY date DESC
    """, (start_date.isoformat(),))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def check_quota_status():
    """Quota 상태 체크 및 출력"""

    DAILY_LIMIT = 10000  # YouTube API v3 기본 할당량

    print("\n" + "="*60)
    print("📊 YouTube API Quota 사용 현황")
    print("="*60 + "\n")

    # 오늘 사용량
    today_usage = get_today_quota_usage()
    remaining = DAILY_LIMIT - today_usage
    usage_percent = (today_usage / DAILY_LIMIT) * 100

    print(f"📅 오늘 날짜: {datetime.now().strftime('%Y-%m-%d')}\n")

    print(f"📊 오늘 사용량:")
    print(f"   사용: {today_usage:,} units")
    print(f"   남음: {remaining:,} units")
    print(f"   비율: {usage_percent:.2f}%\n")

    # 상태 표시
    if usage_percent < 50:
        print("✅ 상태: 안전 (50% 미만)")
    elif usage_percent < 80:
        print("⚠️ 상태: 주의 (50-80%)")
    elif usage_percent < 100:
        print("🚨 상태: 위험 (80% 이상)")
    else:
        print("❌ 상태: 할당량 초과!")

    print()

    # 예상 가능 수집 횟수
    avg_quota_per_collection = 245  # 채널 81개 기준
    possible_collections = remaining // avg_quota_per_collection

    print(f"💡 오늘 추가 수집 가능 횟수: 약 {possible_collections}회")
    print(f"   (채널 81개 기준, 1회당 ~245 units)\n")

    # 최근 7일 이력
    print("="*60)
    print("📈 최근 7일 사용 내역")
    print("="*60 + "\n")

    history = get_quota_history(days=7)

    if not history:
        print("📭 사용 내역이 없습니다\n")
    else:
        print(f"{'날짜':<12} {'사용량':<15} {'수집 횟수':<10} {'비율'}")
        print("-" * 60)

        for record in history:
            date = record['date']
            quota = record['total_quota']
            count = record['collection_count']
            percent = (quota / DAILY_LIMIT) * 100

            print(f"{date:<12} {quota:>6,} units    {count:>3}회        {percent:>5.1f}%")

        print()

    print("="*60)
    print("💡 참고 정보")
    print("="*60 + "\n")
    print("• 일일 할당량: 10,000 units (무료)")
    print("• 할당량 초과 시:")
    print("  → API 호출 실패 (quotaExceeded 에러)")
    print("  → 다음날 오전 12시(PST)에 리셋")
    print("  → 즉시 필요하면 GCP에서 할당량 증가 요청")
    print()
    print("• API 비용 (할당량 증가 시):")
    print("  → 10,000 units 초과분: $0 (일일 무료)")
    print("  → Quota 증가 요청: 무료 (승인 필요)")
    print("  → 비용 발생은 선택적 (Billing 활성화 시에만)")
    print()
    print("• 수집 최적화 팁:")
    print("  → 하루 1-2회만 수집")
    print("  → 필요한 채널만 선택 (채널 관리)")
    print("  → 채널당 영상 수 조절 (기본 30개)")
    print()


def estimate_collection_quota(num_channels: int, videos_per_channel: int = 30) -> int:
    """수집 시 예상 quota 계산"""

    # subscriptions.list (페이지당) = 1 unit
    subscriptions_quota = 2  # 보통 2페이지 (81개 채널)

    # channels.list = 1 unit per channel
    # playlistItems.list = 1 unit per channel
    # videos.list = 1 unit per channel
    per_channel_quota = 3

    total_quota = subscriptions_quota + (num_channels * per_channel_quota)

    return total_quota


if __name__ == "__main__":
    check_quota_status()

    # 예상 사용량 계산
    print("\n" + "="*60)
    print("🧮 예상 사용량 계산")
    print("="*60 + "\n")

    scenarios = [
        (20, "최소 (20개 채널)"),
        (50, "중간 (50개 채널)"),
        (81, "현재 (81개 채널)"),
    ]

    for num_channels, label in scenarios:
        estimated = estimate_collection_quota(num_channels)
        print(f"{label:<25} → {estimated:>4} units ({estimated/10000*100:.2f}%)")

    print()
