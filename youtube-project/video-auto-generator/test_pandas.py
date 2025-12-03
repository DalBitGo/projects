"""
Test 3: Pandas CSV 데이터 처리 테스트
목적: CSV 읽기, 데이터 검증, 랭킹 처리 확인
"""
import pandas as pd
import os

def test_pandas_installed():
    """Pandas 설치 확인"""
    print("=" * 50)
    print("Test 3-1: Pandas 설치 확인")
    print("=" * 50)

    try:
        print(f"✅ Pandas 버전: {pd.__version__}")
        return True
    except Exception as e:
        print(f"❌ Pandas 에러: {e}")
        return False

def test_create_sample_csv():
    """샘플 랭킹 CSV 생성"""
    print("\n" + "=" * 50)
    print("Test 3-2: 샘플 랭킹 CSV 생성")
    print("=" * 50)

    try:
        # 샘플 데이터
        data = {
            'rank': [1, 2, 3, 4, 5],
            'title': [
                '웃긴 고양이 영상 🐱',
                '강아지가 수영하는 영상 🐕',
                '귀여운 햄스터 먹방 🐹',
                '앵무새가 노래하는 영상 🦜',
                '토끼가 뛰어다니는 영상 🐰'
            ],
            'clip_path': [
                'assets/clips/cat.mp4',
                'assets/clips/dog.mp4',
                'assets/clips/hamster.mp4',
                'assets/clips/parrot.mp4',
                'assets/clips/rabbit.mp4'
            ],
            'emoji': ['😹', '🏊', '🍕', '🎵', '🏃'],
            'score': [9.8, 9.5, 9.3, 9.1, 8.9]
        }

        df = pd.DataFrame(data)

        # 저장
        os.makedirs('data', exist_ok=True)
        csv_path = 'data/test_ranking.csv'
        df.to_csv(csv_path, index=False, encoding='utf-8')

        print(f"✅ CSV 생성 성공: {csv_path}")
        print(f"\n샘플 데이터:\n{df.to_string(index=False)}")

        return True

    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_read_csv():
    """CSV 읽기 및 기본 검증"""
    print("\n" + "=" * 50)
    print("Test 3-3: CSV 읽기 및 검증")
    print("=" * 50)

    try:
        csv_path = 'data/test_ranking.csv'
        if not os.path.exists(csv_path):
            print(f"❌ CSV 파일 없음: {csv_path}")
            return False

        # CSV 읽기
        df = pd.read_csv(csv_path)
        print(f"✅ CSV 읽기 성공")

        # 기본 정보
        print(f"\n📊 데이터 정보:")
        print(f"  - 행 수: {len(df)}")
        print(f"  - 열 수: {len(df.columns)}")
        print(f"  - 컬럼: {', '.join(df.columns)}")

        # 필수 컬럼 확인
        required_columns = ['rank', 'title', 'clip_path', 'emoji', 'score']
        missing = [col for col in required_columns if col not in df.columns]

        if missing:
            print(f"❌ 필수 컬럼 누락: {missing}")
            return False
        else:
            print(f"✅ 필수 컬럼 모두 존재")

        # 데이터 타입 확인
        print(f"\n📋 데이터 타입:")
        for col in df.columns:
            print(f"  - {col}: {df[col].dtype}")

        return True

    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_validation():
    """데이터 검증 (결측치, 중복 등)"""
    print("\n" + "=" * 50)
    print("Test 3-4: 데이터 검증")
    print("=" * 50)

    try:
        df = pd.read_csv('data/test_ranking.csv')

        # 1. 결측치 확인
        null_counts = df.isnull().sum()
        if null_counts.sum() == 0:
            print("✅ 결측치 없음")
        else:
            print(f"⚠️  결측치 발견:")
            for col, count in null_counts.items():
                if count > 0:
                    print(f"  - {col}: {count}개")

        # 2. 중복 확인
        duplicates = df.duplicated().sum()
        if duplicates == 0:
            print("✅ 중복 행 없음")
        else:
            print(f"⚠️  중복 행: {duplicates}개")

        # 3. 랭킹 순서 확인
        expected_ranks = list(range(1, len(df) + 1))
        actual_ranks = df['rank'].tolist()

        if actual_ranks == expected_ranks:
            print("✅ 랭킹 순서 정상 (1부터 연속)")
        else:
            print(f"⚠️  랭킹 순서 이상:")
            print(f"  - 예상: {expected_ranks}")
            print(f"  - 실제: {actual_ranks}")

        # 4. 점수 범위 확인
        scores = df['score']
        if (scores >= 0).all() and (scores <= 10).all():
            print(f"✅ 점수 범위 정상 (0-10)")
            print(f"  - 최소: {scores.min()}, 최대: {scores.max()}")
        else:
            print(f"⚠️  점수 범위 이상")

        return True

    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_processing():
    """데이터 가공 (정렬, 필터링, 변환)"""
    print("\n" + "=" * 50)
    print("Test 3-5: 데이터 가공")
    print("=" * 50)

    try:
        df = pd.read_csv('data/test_ranking.csv')

        # 1. 정렬 (점수 내림차순)
        df_sorted = df.sort_values('score', ascending=False)
        print("✅ 점수 정렬:")
        print(df_sorted[['rank', 'title', 'score']].head(3).to_string(index=False))

        # 2. 필터링 (점수 9.0 이상)
        df_filtered = df[df['score'] >= 9.0]
        print(f"\n✅ 필터링 (점수 ≥ 9.0): {len(df_filtered)}개")

        # 3. 새 컬럼 추가 (등급)
        def get_grade(score):
            if score >= 9.5:
                return 'S'
            elif score >= 9.0:
                return 'A'
            elif score >= 8.5:
                return 'B'
            else:
                return 'C'

        df['grade'] = df['score'].apply(get_grade)
        print(f"\n✅ 등급 컬럼 추가:")
        print(df[['rank', 'title', 'score', 'grade']].to_string(index=False))

        # 4. 그룹 통계
        grade_counts = df['grade'].value_counts()
        print(f"\n✅ 등급별 통계:")
        for grade, count in grade_counts.items():
            print(f"  - {grade}등급: {count}개")

        return True

    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n📊 Pandas 기능 테스트 시작\n")

    results = {}

    results['installed'] = test_pandas_installed()
    results['create_csv'] = test_create_sample_csv()
    results['read_csv'] = test_read_csv()
    results['validation'] = test_data_validation()
    results['processing'] = test_data_processing()

    print("\n" + "=" * 50)
    print("📊 테스트 결과")
    print("=" * 50)
    print(f"Pandas 설치: {'✅ PASS' if results['installed'] else '❌ FAIL'}")
    print(f"CSV 생성: {'✅ PASS' if results['create_csv'] else '❌ FAIL'}")
    print(f"CSV 읽기: {'✅ PASS' if results['read_csv'] else '❌ FAIL'}")
    print(f"데이터 검증: {'✅ PASS' if results['validation'] else '❌ FAIL'}")
    print(f"데이터 가공: {'✅ PASS' if results['processing'] else '❌ FAIL'}")

    if all(results.values()):
        print("\n✅ 모든 Pandas 테스트 통과!")
    else:
        print("\n❌ 일부 테스트 실패")
