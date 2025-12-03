#!/usr/bin/env python3
"""
pyktok 라이브러리로 TikTok 해시태그 검색 테스트
공식 API: save_tiktok_multi_page
"""
import pyktok as pyk
import pandas as pd
import os

def test_pyktok_hashtag():
    print("=" * 60)
    print("pyktok으로 TikTok 해시태그 검색 테스트")
    print("=" * 60)

    keyword = "skills"
    output_file = "skills_hashtag.csv"

    print(f"\n해시태그: #{keyword}")
    print("데이터 가져오는 중...\n")

    try:
        # 기존 파일 삭제
        if os.path.exists(output_file):
            os.remove(output_file)
            print(f"기존 {output_file} 삭제")

        # pyktok 공식 API 사용
        print("pyktok.save_tiktok_multi_page 실행 중...")
        pyk.save_tiktok_multi_page(
            keyword,
            ent_type="hashtag",      # 해시태그 타입
            save_video=False,        # 메타데이터만 수집
            metadata_fn=output_file  # CSV로 저장
        )

        # 결과 확인
        if os.path.exists(output_file):
            df = pd.read_csv(output_file)
            print(f"\n✓ 성공! {len(df)}개 비디오 발견\n")

            # 컬럼 확인
            print(f"수집된 컬럼: {list(df.columns)[:10]}...")

            # 첫 3개 샘플 출력
            print("\n첫 3개 비디오 정보:")
            for i, row in df.head(3).iterrows():
                print(f"\n{i+1}. ID: {row.get('id', 'N/A')}")
                print(f"   작성자: {row.get('author_name', row.get('author', 'N/A'))}")
                print(f"   설명: {str(row.get('video_description', row.get('desc', 'N/A')))[:50]}...")
                print(f"   조회수: {row.get('video_playCount', row.get('playCount', 'N/A'))}")
                print(f"   좋아요: {row.get('video_diggCount', row.get('diggCount', 'N/A'))}")

            return True, df
        else:
            print(f"✗ 실패: {output_file} 파일이 생성되지 않았습니다")
            return False, None

    except Exception as e:
        print(f"✗ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        return False, None

if __name__ == "__main__":
    success, data = test_pyktok_hashtag()
    print("\n" + "=" * 60)
    if success:
        print("결과: pyktok으로 TikTok 스크래핑 가능 ✓")
        print(f"CSV 파일: skills_hashtag.csv")
    else:
        print("결과: pyktok으로 TikTok 스크래핑 불가능 ✗")
    print("=" * 60)
