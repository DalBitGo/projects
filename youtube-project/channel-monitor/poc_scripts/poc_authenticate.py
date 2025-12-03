"""
OAuth 인증 테스트

각 YouTube 계정마다 실행 필요
- 브라우저가 자동으로 열림
- Google 로그인 및 권한 승인
- 토큰 저장 (tokens/{account_name}_token.json)
"""

import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

# OAuth Scopes
SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/yt-analytics.readonly'
]

def find_client_secrets():
    """client_secrets.json 파일 찾기"""
    possible_paths = [
        'client_secrets.json',
        '../client_secrets.json',
        '../../client_secrets.json',
    ]

    for path in possible_paths:
        full_path = os.path.abspath(path)
        if os.path.exists(full_path):
            return full_path

    return None

def authenticate(account_name):
    """OAuth 인증 및 토큰 저장"""

    # client_secrets.json 찾기
    client_secrets_path = find_client_secrets()
    if not client_secrets_path:
        print("❌ client_secrets.json 파일을 찾을 수 없습니다.")
        print()
        print("다음 단계:")
        print("1. GCP_SETUP_GUIDE.md를 참고하여 OAuth 클라이언트 생성")
        print("2. client_secrets.json 다운로드")
        print("3. 프로젝트 폴더에 저장")
        sys.exit(1)

    print(f"✅ client_secrets.json 파일 찾음: {client_secrets_path}")
    print()

    # OAuth 플로우 시작
    print("🔐 OAuth 인증 플로우 시작...")
    print()
    print("WSL 환경이므로 브라우저를 수동으로 열어야 합니다.")
    print()

    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_path,
            scopes=SCOPES
        )

        # 로컬 서버 실행 (브라우저 자동 열기 비활성화)
        print("="*60)
        print("다음 URL을 Windows 브라우저에 복사하여 붙여넣으세요:")
        print("="*60)
        print()

        credentials = flow.run_local_server(
            port=8080,
            open_browser=False,
            success_message='인증 성공! 이 창을 닫고 터미널로 돌아가세요.'
        )

    except Exception as e:
        print(f"❌ OAuth 인증 실패: {e}")
        print()
        print("문제 해결:")
        print("1. 포트 8080이 이미 사용 중인지 확인")
        print("2. 브라우저 팝업 차단 확인")
        print("3. 테스트 사용자로 추가되었는지 확인 (GCP OAuth 동의 화면)")
        sys.exit(1)

    # 토큰 저장 디렉토리 생성
    tokens_dir = os.path.join(os.path.dirname(client_secrets_path), 'tokens')
    os.makedirs(tokens_dir, exist_ok=True)

    # 토큰 파일 경로
    token_path = os.path.join(tokens_dir, f'{account_name}_token.json')

    # 토큰 저장
    with open(token_path, 'w') as token_file:
        token_file.write(credentials.to_json())

    print()
    print("="*60)
    print(f"✅ {account_name} 인증 완료!")
    print("="*60)
    print()
    print(f"토큰 저장 위치: {token_path}")
    print()
    print("다음 단계:")
    print(f"  python poc_test_api.py {account_name}")
    print()

    return credentials

def main():
    if len(sys.argv) < 2:
        print("사용법: python poc_authenticate.py <account_name>")
        print()
        print("예시:")
        print("  python poc_authenticate.py account1")
        print("  python poc_authenticate.py account2")
        print("  python poc_authenticate.py account3")
        print()
        print("설명:")
        print("  - account_name: 토큰 파일명에 사용될 이름")
        print("  - 각 YouTube 계정마다 다른 이름 사용")
        print("  - 예: account1, account2, main_account 등")
        sys.exit(1)

    account_name = sys.argv[1]

    print("="*60)
    print(f"🔐 {account_name} OAuth 인증")
    print("="*60)
    print()

    authenticate(account_name)

if __name__ == '__main__':
    main()
