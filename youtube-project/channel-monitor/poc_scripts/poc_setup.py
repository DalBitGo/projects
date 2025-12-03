"""
Google Cloud Console 설정 체크리스트

실행 전 수동으로 완료해야 할 항목들
"""

import os
import sys

def check_setup():
    """설정 체크리스트 출력 및 파일 확인"""

    print("="*60)
    print("🔧 Google Cloud Console 설정 체크리스트")
    print("="*60)
    print()

    checklist = """
□ 1. Google Cloud Console 접속
     https://console.cloud.google.com

□ 2. 프로젝트 생성
     프로젝트 이름: YouTube Intelligence

□ 3. YouTube Data API v3 활성화
     API 및 서비스 → 라이브러리 → 검색 → 활성화

□ 4. YouTube Analytics API 활성화
     API 및 서비스 → 라이브러리 → 검색 → 활성화

□ 5. OAuth 동의 화면 구성
     - 사용자 유형: 외부
     - 앱 이름: YouTube Intelligence
     - 사용자 지원 이메일: (본인 이메일)
     - 테스트 사용자 추가:
       * account1@example.com
       * account2@example.com
       * account3@example.com

□ 6. OAuth 클라이언트 ID 생성
     - 애플리케이션 유형: 데스크톱 앱 ⭐ (중요!)
     - 이름: Local App

□ 7. client_secrets.json 다운로드
     - 사용자 인증 정보 화면에서 다운로드 아이콘 클릭
     - 파일명 변경: client_secrets.json
     - 프로젝트 루트 폴더에 저장
"""

    print(checklist)
    print()
    print("="*60)
    print("📋 파일 확인")
    print("="*60)
    print()

    # 현재 디렉토리 확인
    current_dir = os.getcwd()
    print(f"현재 디렉토리: {current_dir}")
    print()

    # 상위 디렉토리에서 client_secrets.json 찾기
    possible_paths = [
        'client_secrets.json',
        '../client_secrets.json',
        '../../client_secrets.json',
    ]

    found = False
    for path in possible_paths:
        full_path = os.path.abspath(path)
        if os.path.exists(full_path):
            print(f"✅ client_secrets.json 파일을 찾았습니다!")
            print(f"   위치: {full_path}")
            found = True

            # 파일 내용 간단 검증
            try:
                import json
                with open(full_path, 'r') as f:
                    data = json.load(f)

                if 'installed' in data:
                    print(f"✅ 파일 형식 검증: 데스크톱 앱 (정상)")
                    print(f"   Client ID: {data['installed']['client_id']}")
                elif 'web' in data:
                    print(f"❌ 파일 형식 오류: 웹 앱용 파일입니다!")
                    print(f"   → OAuth 클라이언트를 '데스크톱 앱'으로 다시 생성하세요.")
                    return False
                else:
                    print(f"⚠️  파일 형식이 예상과 다릅니다. 확인 필요.")

            except json.JSONDecodeError:
                print(f"❌ JSON 파싱 오류. 파일이 손상되었을 수 있습니다.")
                return False
            except Exception as e:
                print(f"⚠️  파일 검증 중 오류: {e}")

            break

    if not found:
        print("❌ client_secrets.json 파일이 없습니다.")
        print()
        print("다음 단계:")
        print("1. 위 체크리스트를 완료하세요")
        print("2. client_secrets.json 파일을 다운로드하세요")
        print("3. 프로젝트 폴더에 저장하세요")
        print("4. 다시 이 스크립트를 실행하세요")
        return False

    print()
    print("="*60)
    print("✅ 설정 완료!")
    print("="*60)
    print()
    print("다음 단계:")
    print("1. 가상환경 활성화 (선택):")
    print("   python -m venv venv")
    print("   source venv/bin/activate  # Windows: venv\\Scripts\\activate")
    print()
    print("2. 패키지 설치:")
    print("   pip install google-auth google-auth-oauthlib google-api-python-client")
    print()
    print("3. OAuth 인증 (각 계정마다):")
    print("   python poc_authenticate.py account1")
    print("   python poc_authenticate.py account2")
    print("   python poc_authenticate.py account3")
    print()
    print("4. API 테스트:")
    print("   python poc_test_api.py account1")
    print()

    return True

if __name__ == '__main__':
    success = check_setup()
    sys.exit(0 if success else 1)
