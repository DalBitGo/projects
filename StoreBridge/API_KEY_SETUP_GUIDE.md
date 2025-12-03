# API 키 발급 가이드

StoreBridge를 실제로 사용하기 위해 필요한 API 키 발급 방법을 설명합니다.

---

## 📋 필요한 API 키

| API | 용도 | 난이도 | 소요 시간 |
|-----|------|--------|-----------|
| 도매꾹 OpenAPI | 도매 상품 정보 가져오기 | ⭐ 쉬움 | 10분 |
| 네이버 Commerce API | 스마트스토어 상품 등록 | ⭐⭐⭐ 어려움 | 1-3일 |

---

## 1️⃣ 도매꾹 OpenAPI 발급 (쉬움)

### 📌 요구사항
- ✅ **개인도 가능** (사업자 등록 불필요)
- ✅ 이메일 인증만으로 가입 가능
- ⚠️ 사업자 인증 권장 (더 많은 기능)

### 📝 발급 절차

#### Step 1: 도매꾹 회원가입
```
1. https://www.domeggook.com 접속
2. 우측 상단 [회원가입] 클릭
3. 개인 또는 사업자 선택
4. 이메일 인증 후 가입 완료
```

**💡 팁**: 도매꾹과 도매매는 아이디를 공유합니다.

#### Step 2: API 키 발급
```
1. 로그인 후 https://openapi.domeggook.com 접속
2. 상단 메뉴 [API 키 관리] 클릭
3. [추가발급] 버튼 클릭
4. 발급 정보 입력
   - API 키 이름: "StoreBridge"
   - 사용 목적: "상품 자동 등록 시스템"
5. 발급 완료 → API 키 복사
```

**발급 가능 개수**: 1개 계정당 최대 5개

#### Step 3: .env 파일에 등록
```bash
# .env 파일 수정
DOMEGGOOK_API_KEY=여기에_발급받은_API_키_붙여넣기
DOMEGGOOK_API_URL=https://openapi.domeggook.com
```

#### Step 4: 테스트
```bash
curl -X GET "https://openapi.domeggook.com/getItemList?key=YOUR_API_KEY&page=1&page_size=10"
```

### 🚨 제한 사항
| 항목 | 제한 |
|------|------|
| **Rate Limit** | 분당 180회, 하루 15,000회 |
| **초과 시** | HTTP 429 에러 (차단) |
| **인코딩** | EUC-KR만 지원 |
| **IP 제한** | 없음 |

### 📞 문의
- 이메일: techsupport@ggook.com
- 문서: https://openapi.domeggook.com/main/guide/start

---

## 2️⃣ 네이버 Commerce API 발급 (어려움) ⚠️

### 📌 요구사항 (모두 필수)
1. ✅ **스마트스토어 개설** (필수)
2. ✅ **통합매니저 권한** (필수)
3. ✅ **개인/사업자 모두 가능**
4. ⚠️ 사업자 전환 권장 (더 많은 기능)

### 🏪 스마트스토어 개설 (먼저 해야 함)

#### Step 0: 스마트스토어 판매자 가입
```
1. https://sell.smartstore.naver.com 접속
2. [판매 시작하기] 클릭
3. 개인 판매자 또는 사업자 선택
   - 개인: 본인 인증만
   - 사업자: 사업자 등록증 업로드
4. 판매자 정보 입력
   - 상호명/이름
   - 연락처
   - 정산 계좌
5. 심사 대기 (1-3일)
6. 승인 완료 → 스마트스토어 개설
```

**💡 개인 판매자로 시작 가능**:
- 사업자 등록 없이도 개인 판매자로 활동 가능
- 나중에 '판매자 정보 > 사업자 전환' 메뉴로 전환 가능

#### 스마트스토어 승인 조건:
- ✅ 본인 인증 완료
- ✅ 정산 계좌 등록
- ⚠️ 판매 금지 품목 확인
- ⚠️ 최소 상품 1개 등록 (선택)

---

### 📝 네이버 Commerce API 발급 절차

#### Step 1: 커머스 API 센터 접속
```
1. https://apicenter.commerce.naver.com/ko/basic/main 접속
2. 스마트스토어 ID로 로그인
   ⚠️ 반드시 "통합매니저" 권한 있는 계정으로 로그인
```

**권한 확인 방법**:
```
스마트스토어 센터 > 설정 > 권한관리
→ 본인 계정이 "통합매니저"인지 확인
```

#### Step 2: 커머스 API 계정 생성
```
1. 우측 상단 [계정생성] 클릭
2. 정보 입력
   - 개발업체 계정명: "StoreBridge"
   - 장애대응 연락처: 본인 전화번호
   - 이메일: 본인 이메일
3. 약관 동의 후 [가입하기] 클릭
4. [확인] 클릭
```

#### Step 3: 애플리케이션 등록
```
1. [애플리케이션 등록하기] 클릭
2. 기본 정보 입력
   - 애플리케이션 이름: "StoreBridge"
   - 설명: "도매꾹 상품 자동 등록 시스템"
   - 사용 용도: "상품 자동 등록"
```

#### Step 4: API 호출 IP 등록 (중요!) ⚠️
```
내 IP 확인:
curl https://ifconfig.me

API 센터에서 IP 등록:
1. [API호출 IP] 항목에 본인 IP 입력
2. 최대 3개까지 등록 가능
   - 집 IP
   - 회사 IP
   - 서버 IP
```

**⚠️ 중요**: IP를 등록하지 않으면 API 호출이 전부 차단됩니다!

#### Step 5: API 그룹 선택
```
다음 5개 항목 모두 선택:
☑️ 상품 (Product)
☑️ 주문 (Order)
☑️ 문의 (QnA)
☑️ 리뷰 (Review)
☑️ 정산 (Settlement)
```

#### Step 6: 등록 완료
```
[등록] 버튼 클릭
→ 애플리케이션 ID, 시크릿 발급 완료
```

#### Step 7: .env 파일에 등록
```bash
# .env 파일 수정
NAVER_CLIENT_ID=여기에_애플리케이션_ID_붙여넣기
NAVER_CLIENT_SECRET=여기에_시크릿_붙여넣기
NAVER_API_URL=https://api.commerce.naver.com
```

### 🚨 제한 사항 (매우 중요!)

| 항목 | 제한 |
|------|------|
| **Rate Limit** | **초당 2회 (2 TPS)** ⚠️ 매우 엄격! |
| **알고리즘** | 토큰 버킷 (Token Bucket) |
| **초과 시** | HTTP 429 에러 |
| **IP 제한** | 최대 3개 IP만 등록 가능 |
| **애플리케이션** | 스토어당 1개만 등록 가능 |
| **비용** | 무료 |

**⚠️ 2 TPS는 매우 엄격한 제한입니다**:
- 1초에 2번만 호출 가능
- 3번째 호출은 무조건 429 에러
- StoreBridge의 Rate Limiter가 자동으로 제어

### 📊 2 TPS로 처리 가능한 상품 수

| 시간 | 최대 API 호출 | 예상 상품 등록 수 |
|------|--------------|------------------|
| 1시간 | 7,200회 | ~1,000개 |
| 1일 | 172,800회 | ~20,000개 |

**계산 근거**:
- 상품 1개 등록: 약 5-7번 API 호출
  1. 카테고리 속성 조회 (1회)
  2. 이미지 업로드 (3-5회)
  3. 상품 등록 (1회)
  4. 옵션 등록 (1회)

---

## 3️⃣ 발급 완료 후 테스트

### 전체 .env 파일 예시
```bash
# Environment
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql+psycopg://storebridge@localhost:5432/storebridge

# Redis
REDIS_URL=redis://localhost:6379/0

# 도매꾹 API (발급 완료)
DOMEGGOOK_API_KEY=dmk_1234567890abcdef
DOMEGGOOK_API_URL=https://openapi.domeggook.com

# 네이버 Commerce API (발급 완료)
NAVER_CLIENT_ID=AbC1234567890XyZ
NAVER_CLIENT_SECRET=0987654321zyxWvU
NAVER_API_URL=https://api.commerce.naver.com
```

### 도매꾹 API 테스트
```bash
# Python으로 테스트
python3 -c "
import asyncio
from app.connectors.domeggook_client import DomeggookClient

async def test():
    async with DomeggookClient() as client:
        response = await client.get_item_list(page=1, page_size=10)
        print(f'✅ 성공! 상품 {len(response[\"items\"])}개 조회됨')
        print(f'첫 번째 상품: {response[\"items\"][0][\"item_name\"]}')

asyncio.run(test())
"
```

### 네이버 API 테스트
```bash
# Python으로 테스트
python3 -c "
import asyncio
from app.connectors.naver_client import NaverClient

async def test():
    async with NaverClient() as client:
        # 카테고리 속성 조회 (테스트)
        result = await client.get_category_attributes('50000000')
        print('✅ 네이버 API 연결 성공!')
        print(f'카테고리 ID: {result[\"categoryId\"]}')

asyncio.run(test())
"
```

**예상 결과**:
```
✅ 네이버 API 연결 성공!
카테고리 ID: 50000000
```

---

## 🐛 트러블슈팅

### 도매꾹 API 문제

#### 문제 1: 429 에러 (Rate Limit 초과)
```
에러: HTTP Response Code 429
원인: 분당 180회 또는 하루 15,000회 초과
해결: 10-30분 대기 후 재시도
```

#### 문제 2: 한글 깨짐
```
원인: EUC-KR 인코딩 문제
해결: DomeggookClient._decode_response()가 자동 처리
```

#### 문제 3: API 키 인증 실패
```
에러: Invalid API Key
해결:
1. API 키가 .env에 정확히 입력되었는지 확인
2. 공백이나 줄바꿈 없는지 확인
3. 도매꾹 사이트에서 API 키 활성화 여부 확인
```

---

### 네이버 Commerce API 문제

#### 문제 1: 401 Unauthorized
```
원인 1: 잘못된 Client ID/Secret
해결: .env 파일의 NAVER_CLIENT_ID, NAVER_CLIENT_SECRET 재확인

원인 2: IP 화이트리스트 미등록
해결:
1. curl https://ifconfig.me 로 현재 IP 확인
2. 커머스 API 센터에서 IP 등록
3. 5분 대기 후 재시도
```

#### 문제 2: 429 Too Many Requests
```
원인: 2 TPS 초과
해결: StoreBridge Rate Limiter가 자동으로 제어
- 수동 호출 시: 0.5초 대기 후 재시도
```

#### 문제 3: 403 Forbidden
```
원인 1: API 그룹 권한 없음
해결: 커머스 API 센터에서 API 그룹 추가

원인 2: 스토어 인증 안 됨
해결:
1. 커머스 API 센터 > 애플리케이션 > [스토어 인증]
2. 스마트스토어 선택 후 인증
```

#### 문제 4: 연결이 안 됨 (Connection Refused)
```
원인: IP 제한
해결:
1. 현재 IP 확인: curl https://ifconfig.me
2. 커머스 API 센터에서 IP 등록 확인
3. 집/회사 IP가 달라지면 다시 등록 필요
```

---

## 📚 추가 자료

### 도매꾹 OpenAPI
- 공식 문서: https://openapi.domeggook.com/main/guide/start
- API 명세서: https://openapi.domeggook.com/main/guide/api
- 문의: techsupport@ggook.com

### 네이버 Commerce API
- 커머스 API 센터: https://apicenter.commerce.naver.com
- GitHub: https://github.com/commerce-api-naver/commerce-api
- 개발자 포럼: https://github.com/commerce-api-naver/commerce-api/discussions

---

## ✅ 체크리스트

발급 완료 확인:

**도매꾹 OpenAPI**:
- [ ] 도매꾹 회원가입 완료
- [ ] API 키 발급 완료
- [ ] .env 파일에 DOMEGGOOK_API_KEY 등록
- [ ] 테스트 성공 (상품 리스트 조회)

**네이버 Commerce API**:
- [ ] 스마트스토어 개설 완료
- [ ] 통합매니저 권한 확인
- [ ] 커머스 API 계정 생성
- [ ] 애플리케이션 등록 완료
- [ ] API 호출 IP 등록 (최대 3개)
- [ ] .env 파일에 NAVER_CLIENT_ID, NAVER_CLIENT_SECRET 등록
- [ ] 테스트 성공 (카테고리 조회)

**StoreBridge 테스트**:
- [ ] FastAPI 서버 실행 확인
- [ ] Celery Worker 실행 확인
- [ ] Job 생성 테스트
- [ ] 실제 상품 1개 등록 성공

---

**작성일**: 2025-10-17
**업데이트**: 필요 시 최신 정보 확인
**프로젝트**: StoreBridge
