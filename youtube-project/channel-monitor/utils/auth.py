"""
YouTube OAuth 인증 관리
"""

import os
import sys
from pathlib import Path
from google.oauth2.credentials import Credentials


def find_token_file(account_name: str) -> str:
    """토큰 파일 찾기"""
    # 프로젝트 루트에서 tokens 폴더 찾기
    project_root = Path(__file__).parent.parent
    token_path = project_root / "tokens" / f"{account_name}_token.json"

    if token_path.exists():
        return str(token_path)

    raise FileNotFoundError(
        f"토큰 파일을 찾을 수 없습니다: {token_path}\n"
        f"먼저 OAuth 인증을 진행하세요:\n"
        f"  python poc_scripts/poc_authenticate.py {account_name}"
    )


def load_credentials(account_name: str) -> Credentials:
    """저장된 토큰 로드"""
    token_path = find_token_file(account_name)

    scopes = [
        'https://www.googleapis.com/auth/youtube.readonly',
        'https://www.googleapis.com/auth/yt-analytics.readonly'
    ]

    credentials = Credentials.from_authorized_user_file(token_path, scopes=scopes)
    return credentials
