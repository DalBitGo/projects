# YouTube Intelligence Dashboard - 설계 가이드

## 📊 목차
1. [성공 사례 분석](#1-성공-사례-분석)
2. [대시보드 디자인 베스트 프랙티스](#2-대시보드-디자인-베스트-프랙티스)
3. [레이아웃 패턴](#3-레이아웃-패턴)
4. [기술 스택 비교](#4-기술-스택-비교)
5. [우리 프로젝트 적용안](#5-우리-프로젝트-적용안)

---

## 1. 성공 사례 분석

### 1.1 YouTube Studio Analytics (공식)

**타겟 사용자:** YouTube 크리에이터 본인

**핵심 기능:**
- **Overview 탭**: 핵심 KPI (조회수, 시청 시간, 구독자 증가)
- **Content 탭**: 영상별 성과 비교
- **Audience 탭**: 시청자 인구통계, 시청 시간대
- **Research 탭**: 트렌드 키워드, 경쟁 분석

**디자인 특징:**
```
┌─────────────────────────────────────────┐
│  [최근 28일 요약]                        │
│  조회수: 1.2M  시청시간: 10K시간         │
│  구독자: +5K   평균 시청시간: 5:30      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  [시계열 그래프]                         │
│  조회수 추이 (선 그래프)                 │
└─────────────────────────────────────────┘

┌──────────────┬──────────────────────────┐
│  인기 영상    │  실시간 데이터            │
│  (리스트)     │  (현재 시청자 수)         │
└──────────────┴──────────────────────────┘
```

**배울 점:**
- ✅ 상단에 핵심 메트릭 (5초 안에 파악)
- ✅ 시계열 그래프로 트렌드 시각화
- ✅ 탭으로 정보 계층화 (Overview → Detailed)
- ✅ 실시간 데이터 강조

---

### 1.2 Social Blade

**타겟 사용자:** 마케터, 분석가, 경쟁 분석

**핵심 기능:**
- 여러 채널 동시 추적
- 구독자 증가 예측
- 수익 추정 (광고 수익)
- 순위 추적 (카테고리별, 국가별)

**디자인 특징:**
```
┌─────────────────────────────────────────┐
│  채널명 | 구독자 | 순위 | 예상 수익        │
├─────────────────────────────────────────┤
│  [그래프: 구독자 증가 추이]              │
│  - 일일 증가량 표시                      │
│  - 미래 예측 라인                        │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  [최근 업로드 영상]                      │
│  제목 | 조회수 | 좋아요 | 업로드 시간     │
└─────────────────────────────────────────┘
```

**배울 점:**
- ✅ 비교 기능 (여러 채널 나란히)
- ✅ 예측/추정 기능 (미래 트렌드)
- ✅ 순위 시각화 (경쟁 위치 파악)
- ⚠️ 초기 진입장벽 높음 (정보 과다)

---

### 1.3 VidIQ

**타겟 사용자:** 콘텐츠 크리에이터, SEO 최적화

**핵심 기능:**
- 채널 감사 (Channel Audit)
- SEO 점수 (영상별)
- 키워드 추적
- 경쟁사 벤치마크

**디자인 특징:**
```
[현대적, 깔끔한 UI]

사이드바:
  - 대시보드
  - 채널 감사
  - 키워드 리서치
  - 경쟁사 분석

메인 영역:
┌─────────────────────────────────────────┐
│  📊 채널 건강도: 85/100                 │
│  ┌───────┬───────┬───────┬───────┐      │
│  │ 조회수 │ 참여도 │ SEO  │ 성장률│      │
│  │  92   │  78   │  85  │  90  │      │
│  └───────┴───────┴───────┴───────┘      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  [상위 성과 영상]                        │
│  [개선 필요 영상]                        │
└─────────────────────────────────────────┘
```

**배울 점:**
- ✅ 점수화 (복잡한 메트릭을 숫자로 단순화)
- ✅ 액션 가능한 인사이트 (개선 제안)
- ✅ 카테고리별 분류 (상위/하위 성과)
- ✅ 직관적인 네비게이션

---

### 1.4 TubeBuddy

**타겟 사용자:** YouTube 크리에이터

**핵심 기능:**
- 채널 분석
- 경쟁사 비교 그래프
- A/B 테스팅
- 키워드 순위 추적

**디자인 특징:**
```
[비교 중심 대시보드]

┌─────────────────────────────────────────┐
│  우리 채널 vs 경쟁사 A (최근 30일)       │
│                                         │
│  [이중 라인 그래프]                      │
│  - 파란선: 우리 조회수                   │
│  - 빨간선: 경쟁사 조회수                 │
└─────────────────────────────────────────┘

┌──────────────┬──────────────────────────┐
│  우리 채널    │  경쟁사 A                 │
│  조회수: 10K  │  조회수: 50K              │
│  구독자: +50  │  구독자: +200             │
└──────────────┴──────────────────────────┘
```

**배울 점:**
- ✅ 비교 시각화 (우리 vs 타인)
- ✅ 브라우저 확장 + 웹 대시보드 조합
- ⚠️ 웹 대시보드는 다소 구식 느낌

---

### 1.5 Power BI YouTube Analytics Templates

**타겟 사용자:** 데이터 분석가, 마케터

**핵심 기능:**
- 다차원 분석 (슬라이서, 필터)
- 고급 시계열 분석 (예측, 이동평균)
- 크로스 플랫폼 분석 (YouTube + Facebook + Instagram)

**디자인 특징:**
```
[전문가용 대시보드]

상단: 날짜 필터, 채널 선택기

┌─────────────────────────────────────────┐
│  KPI 카드 (4개)                          │
│  [조회수] [시청시간] [구독자] [참여율]    │
└─────────────────────────────────────────┘

┌──────────────────┬──────────────────────┐
│  시계열 그래프     │  채널별 비교 막대     │
│  (예측 라인 포함)  │  그래프              │
├──────────────────┴──────────────────────┤
│  [지도 시각화: 국가별 조회수]             │
├─────────────────────────────────────────┤
│  [테이블: 영상별 상세 메트릭]             │
└─────────────────────────────────────────┘
```

**배울 점:**
- ✅ 대시보드 계층화 (Overview → Detail)
- ✅ 예측 분석 (통계 모델 적용)
- ✅ 필터/슬라이서로 동적 분석
- ⚠️ 학습 곡선 높음, 설정 복잡

---

## 2. 대시보드 디자인 베스트 프랙티스

### 2.1 핵심 원칙

#### **1) The Five-Second Rule** ⭐
> 5초 안에 가장 중요한 정보를 찾을 수 있어야 함

**적용 방법:**
```
❌ 잘못된 예:
모든 메트릭이 동일한 크기, 동일한 색상
→ 무엇이 중요한지 모름

✅ 올바른 예:
상단에 큰 숫자로 핵심 KPI
→ 일일 신규 영상 수, 급상승 영상 수
색상으로 긍정/부정 표시
→ 초록색: 증가, 빨간색: 감소
```

#### **2) Visual Hierarchy** (시각적 계층)

**3단 구조:**
```
┌─────────────────────────────────────────┐
│  TOP: 핵심 KPI (가장 중요)               │
│  - 큰 숫자, 눈에 띄는 색상               │
│  - 예: 신규 영상 7개, 급상승 영상 3개    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  MIDDLE: 트렌드 그래프 (중요)            │
│  - 시계열 변화 시각화                    │
│  - 예: 조회수 증가 추이                  │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  BOTTOM: 상세 데이터 (필요시)            │
│  - 테이블, 리스트                        │
│  - 예: 영상별 상세 통계                  │
└─────────────────────────────────────────┘
```

#### **3) Progressive Disclosure** (점진적 정보 공개)

**개념:**
- 처음엔 요약만 보여주기
- 클릭하면 상세 정보 표시

**예시:**
```
[초기 화면]
━━━━━━━━━━━━━━━━━━━━━━━━━━━
채널 A: 신규 영상 2개 ▼
━━━━━━━━━━━━━━━━━━━━━━━━━━━

[클릭 후 확장]
━━━━━━━━━━━━━━━━━━━━━━━━━━━
채널 A: 신규 영상 2개 ▲

  📹 영상 1: "제목..."
      조회수: 10K (+500%)
      좋아요: 500

  📹 영상 2: "제목..."
      조회수: 5K (+200%)
      좋아요: 200
━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### **4) Grid System** (그리드 레이아웃)

**12-Column Grid 표준:**
```
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │10 │11 │12 │
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘

[예시 1: 3개 KPI 카드]
┌───────────┬───────────┬───────────┐
│  KPI 1    │  KPI 2    │  KPI 3    │
│  (4 cols) │  (4 cols) │  (4 cols) │
└───────────┴───────────┴───────────┘

[예시 2: 메인 그래프 + 사이드바]
┌─────────────────────┬───────────┐
│  메인 그래프          │  필터     │
│  (8 cols)           │  (4 cols) │
└─────────────────────┴───────────┘
```

#### **5) Color Strategy** (색상 전략)

**목적별 색상:**
```python
# 상태 표시
긍정 = "#10B981"  # 초록 (증가, 성공)
부정 = "#EF4444"  # 빨강 (감소, 경고)
중립 = "#6B7280"  # 회색 (변화 없음)

# 브랜드 색상
주색상 = "#3B82F6"  # 파랑 (주요 요소)
보조색 = "#8B5CF6"  # 보라 (보조 요소)

# 카테고리 구분
채널A = "#F59E0B"  # 주황
채널B = "#EC4899"  # 핑크
채널C = "#14B8A6"  # 청록
```

**접근성 고려:**
- 색맹 사용자 고려 (색상만으로 정보 전달 X)
- 아이콘, 패턴 조합
- 충분한 대비 (WCAG AA 기준)

---

### 2.2 차트 타입 선택 가이드

| 데이터 유형 | 추천 차트 | 예시 |
|------------|----------|------|
| **시계열** | 선 그래프 | 조회수 추이 |
| **비교** | 막대 그래프 | 채널별 성과 비교 |
| **비율** | 파이/도넛 차트 | 트래픽 소스 분포 |
| **분포** | 히스토그램 | 영상 길이 분포 |
| **상관관계** | 산점도 | 조회수 vs 좋아요 |
| **순위** | 수평 막대 | 상위 10개 영상 |
| **KPI 단일값** | 숫자 카드 | 신규 영상 수 |

**안티 패턴 (피해야 할 것):**
- ❌ 3D 차트 (왜곡된 시각화)
- ❌ 과도한 파이 차트 (5개 이상 항목)
- ❌ 이중 축 그래프 (혼란 유발)

---

### 2.3 메트릭 표시 패턴

#### **패턴 1: Big Number + Sparkline**
```
┌─────────────────────┐
│  총 조회수           │
│                     │
│  1,234,567         │
│  ▲ +12.5%          │
│  ━━━━━━━━━━━━━━━━  │ ← 미니 그래프
└─────────────────────┘
```

#### **패턴 2: Comparison Card**
```
┌─────────────────────┐
│  신규 영상           │
│                     │
│  7개                │
│  vs 어제: 3개 (+133%)│
│  vs 평균: 5개 (+40%) │
└─────────────────────┘
```

#### **패턴 3: Target Progress**
```
┌─────────────────────┐
│  주간 목표           │
│                     │
│  35 / 50 영상 확인   │
│  ████████░░ 70%     │
└─────────────────────┘
```

---

### 2.4 대시보드 타입별 설계

#### **Executive Dashboard** (경영진용)
```
특징:
- 최소한의 정보
- 핵심 KPI만 표시
- 큰 숫자, 간단한 그래프

예시:
┌─────────────────────────────────────────┐
│  이번 주 요약                            │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐       │
│  │ 7개 │ │ 3개 │ │ 85% │ │ +15%│       │
│  │신규 │ │급상승│ │평균 │ │성장 │       │
│  └─────┘ └─────┘ └─────┘ └─────┘       │
└─────────────────────────────────────────┘
```

#### **Operational Dashboard** (운영자용)
```
특징:
- 상세한 메트릭
- 실시간 데이터
- 드릴다운 가능
- 필터 많음

예시:
┌─────────────────────────────────────────┐
│  [필터] 채널: 전체 | 기간: 최근 7일      │
├─────────────────────────────────────────┤
│  [테이블: 전체 영상 목록]                │
│  제목 | 조회수 | 증가율 | 좋아요 | 댓글  │
│  ...                                    │
│  (페이지네이션)                          │
└─────────────────────────────────────────┘
```

#### **Analytical Dashboard** (분석가용)
```
특징:
- 다차원 분석
- 커스텀 메트릭
- 통계 분석
- 데이터 내보내기

예시:
┌─────────────────────────────────────────┐
│  [슬라이서] 채널 | 카테고리 | 날짜       │
├──────────────────┬──────────────────────┤
│  [산점도]         │  [상관계수 매트릭스]  │
│  조회수 vs 길이   │  각 메트릭 간 관계    │
└──────────────────┴──────────────────────┘
```

---

## 3. 레이아웃 패턴

### 3.1 패턴 1: F-Pattern (F자 시선 이동)

사람들은 화면을 F자로 읽음:
```
E = 많이 보는 영역
- = 적게 보는 영역

EEEEEEEEEE----------
EEE-----------------
EEEEEEEE------------
EEE-----------------
EEEE----------------
```

**적용:**
```
┌─────────────────────────────────────────┐
│  [상단 KPI] ← 가장 많이 봄               │
├─────────────────────────────────────────┤
│  [왼쪽 메뉴]  [중앙 컨텐츠]              │
│              [그래프, 표]                │
└─────────────────────────────────────────┘
```

### 3.2 패턴 2: Z-Pattern (Z자 시선 이동)

간단한 페이지에서 사용:
```
1───────────→2
 ↘
   ↘
3←───────────4
```

**적용:**
```
┌─────────────────────────────────────────┐
│ 1.제목/로고            2.날짜 필터        │
├─────────────────────────────────────────┤
│          [중앙 메인 그래프]              │
├─────────────────────────────────────────┤
│ 3.상세 정보            4.액션 버튼        │
└─────────────────────────────────────────┘
```

### 3.3 패턴 3: Card Layout (카드 레이아웃)

**모바일 친화적:**
```
┌───────────┐ ┌───────────┐ ┌───────────┐
│  카드 1    │ │  카드 2    │ │  카드 3    │
│  [메트릭]  │ │  [메트릭]  │ │  [메트릭]  │
└───────────┘ └───────────┘ └───────────┘

┌─────────────────────────────────────────┐
│  카드 4: 큰 그래프                       │
└─────────────────────────────────────────┘

┌───────────┐ ┌───────────┐
│  카드 5    │ │  카드 6    │
└───────────┘ └───────────┘
```

### 3.4 패턴 4: Split Screen (분할 화면)

**비교 중심:**
```
┌─────────────────────┬─────────────────────┐
│  우리 채널           │  경쟁사 채널         │
│                     │                     │
│  [메트릭]           │  [메트릭]           │
│  [그래프]           │  [그래프]           │
│                     │                     │
└─────────────────────┴─────────────────────┘
```

---

## 4. 기술 스택 비교

### 4.1 옵션 1: Streamlit ⭐ **추천**

**장점:**
- ✅ 순수 Python (프론트엔드 지식 불필요)
- ✅ 빠른 프로토타이핑 (50줄로 대시보드)
- ✅ 풍부한 위젯 (필터, 버튼, 슬라이더)
- ✅ 실시간 업데이트 지원
- ✅ 무료, 오픈소스
- ✅ 쉬운 배포 (Streamlit Cloud)

**단점:**
- ⚠️ 제한적인 커스터마이징 (CSS 직접 수정 어려움)
- ⚠️ 복잡한 레이아웃은 코드가 길어짐
- ⚠️ 사용자 인증 기본 제공 X (직접 구현 필요)

**코드 예시:**
```python
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="YouTube Intelligence", layout="wide")

# 상단 KPI
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("신규 영상", "7개", "+4")
with col2:
    st.metric("총 조회수", "1.2M", "+15%")
with col3:
    st.metric("평균 조회수", "85K", "+8%")
with col4:
    st.metric("급상승 영상", "3개", "+2")

# 필터
channel = st.selectbox("채널 선택", ["전체", "채널A", "채널B"])
date_range = st.date_input("기간 선택", [])

# 그래프
df = load_data()
fig = px.line(df, x="date", y="views", color="channel")
st.plotly_chart(fig, use_container_width=True)

# 테이블
st.dataframe(df, use_container_width=True)
```

**언제 사용?**
- Python으로 빠르게 시작하고 싶을 때
- 데이터 팀이 주 사용자일 때
- MVP를 빠르게 만들고 싶을 때

---

### 4.2 옵션 2: Metabase

**장점:**
- ✅ 코드 없이 대시보드 생성 (드래그 앤 드롭)
- ✅ SQL 직접 작성 가능
- ✅ 사용자 관리 내장
- ✅ 알림/스케줄링 기능
- ✅ 무료 오픈소스 (Pro 버전도 있음)

**단점:**
- ⚠️ 별도 서버 필요 (Docker 설치)
- ⚠️ Python 코드와 분리 (ETL 따로, 대시보드 따로)
- ⚠️ 커스텀 로직 구현 어려움

**언제 사용?**
- 비개발자도 대시보드 수정해야 할 때
- 여러 데이터 소스 통합할 때
- 기업용 기능 필요할 때

---

### 4.3 옵션 3: Power BI / Tableau

**장점:**
- ✅ 강력한 시각화 기능
- ✅ 전문적인 외관
- ✅ 고급 분석 기능 (예측, AI)
- ✅ 모바일 앱 제공

**단점:**
- ❌ 비용 (Power BI: 월 $10-20, Tableau: 더 비쌈)
- ❌ 학습 곡선 높음
- ❌ Windows 환경 선호 (Power BI Desktop)

**언제 사용?**
- 예산 있을 때
- 이미 사용 중일 때
- 최고 수준의 시각화 필요할 때

---

### 4.4 옵션 4: Custom (React + Chart.js)

**장점:**
- ✅ 완전한 자유도
- ✅ 최신 웹 기술 활용
- ✅ 반응형 디자인 완벽 제어
- ✅ 브랜딩 완벽 적용

**단점:**
- ❌ 개발 시간 오래 걸림 (2-3주)
- ❌ 프론트엔드 + 백엔드 다 만들어야 함
- ❌ 유지보수 부담

**언제 사용?**
- 프론트엔드 개발 연습하고 싶을 때
- 완전히 커스텀한 디자인 필요할 때
- 장기 프로젝트일 때

---

### 4.5 기술 스택 비교 표

| 항목 | Streamlit | Metabase | Power BI | Custom |
|------|-----------|----------|----------|--------|
| **개발 속도** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **커스터마이징** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **학습 곡선** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| **비용** | 무료 | 무료 | $10-20/월 | 시간 |
| **배포 난이도** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Python 통합** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |

**추천 순위 (이 프로젝트 기준):**
1. **Streamlit** - MVP 빠르게, 나중에 확장 가능
2. **Custom** - 학습 목적이라면 도전 가치 있음
3. **Metabase** - 비개발자 협업 필요시
4. **Power BI** - 예산 있고 이미 익숙하다면

---

## 5. 우리 프로젝트 적용안

### 5.1 두 가지 대시보드 설계

#### **대시보드 A: 우리 채널 성과 모니터링**

**목적:** 오전 9시 회의에서 우리 채널 성과 파악

**핵심 질문:**
1. 어제 올린 영상 성과는?
2. 어떤 영상이 알고리즘에 선택됐나?
3. 채널별 성과 비교는?

**레이아웃 (Streamlit 기준):**

```python
# dashboard_performance.py

import streamlit as st

st.title("📊 우리 채널 성과 대시보드")

# 1. 날짜 필터
col1, col2 = st.columns([3, 1])
with col1:
    date_range = st.date_input("기간 선택", value=(today-7days, today))
with col2:
    refresh_btn = st.button("🔄 새로고침")

# 2. 핵심 KPI (상단)
st.subheader("📌 오늘의 요약")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric(
        label="신규 영상",
        value="7개",
        delta="+4 vs 어제",
        delta_color="normal"
    )
with kpi2:
    st.metric("총 조회수", "1.2M", "+15%")
with kpi3:
    st.metric("평균 조회수", "85K", "+8%")
with kpi4:
    st.metric("급상승 영상", "3개", "+2")

# 3. 채널별 성과 비교
st.subheader("📺 채널별 성과")
chart_col, table_col = st.columns([2, 1])

with chart_col:
    # 막대 그래프: 채널별 조회수
    fig = px.bar(df, x="channel", y="views", color="channel")
    st.plotly_chart(fig, use_container_width=True)

with table_col:
    # 요약 테이블
    st.dataframe(channel_summary, use_container_width=True)

# 4. 시계열 분석
st.subheader("📈 조회수 추이")
fig2 = px.line(df, x="date", y="views", color="channel")
st.plotly_chart(fig2, use_container_width=True)

# 5. 급상승 영상 (알고리즘 선택)
st.subheader("🔥 급상승 영상")
for video in top_videos:
    with st.expander(f"📹 {video.title}"):
        col1, col2, col3 = st.columns(3)
        col1.metric("조회수", f"{video.views:,}", f"+{video.growth}%")
        col2.metric("좋아요", video.likes)
        col3.metric("댓글", video.comments)

        # 미니 그래프
        st.line_chart(video.hourly_views)

# 6. 상세 데이터 (확장 가능)
with st.expander("📋 전체 영상 목록"):
    st.dataframe(all_videos, use_container_width=True)
```

**화면 구성:**
```
┌─────────────────────────────────────────────────────┐
│  📊 우리 채널 성과 대시보드                          │
│  [기간: 최근 7일 ▼]                    [🔄 새로고침] │
├─────────────────────────────────────────────────────┤
│  📌 오늘의 요약                                      │
│  ┌──────────┬──────────┬──────────┬──────────┐     │
│  │ 신규 7개  │ 조회 1.2M │ 평균 85K │ 급상승 3개│     │
│  │ +4       │ +15%     │ +8%      │ +2       │     │
│  └──────────┴──────────┴──────────┴──────────┘     │
├─────────────────────────────────────────────────────┤
│  📺 채널별 성과                                      │
│  ┌──────────────────┬──────────────────────────┐   │
│  │ [막대 그래프]     │ 채널  | 영상 | 조회수    │   │
│  │                  │ ───────────────────────  │   │
│  │                  │ 메인  | 3    | 500K      │   │
│  │                  │ 서브1 | 2    | 400K      │   │
│  └──────────────────┴──────────────────────────┘   │
├─────────────────────────────────────────────────────┤
│  📈 조회수 추이 (최근 7일)                           │
│  [선 그래프: 채널별 조회수 변화]                     │
├─────────────────────────────────────────────────────┤
│  🔥 급상승 영상                                      │
│  📹 "영상 제목 1..." ▼                               │
│     조회수: 100K (+500%) | 좋아요: 5K | 댓글: 200   │
│     [시간별 조회수 미니 그래프]                      │
│                                                     │
│  📹 "영상 제목 2..." ▼                               │
│  📹 "영상 제목 3..." ▼                               │
└─────────────────────────────────────────────────────┘
```

---

#### **대시보드 B: 트렌드 추적 시스템**

**목적:** 인기 채널 모니터링으로 콘텐츠 아이디어 발굴

**핵심 질문:**
1. 요즘 어떤 주제가 인기인가?
2. 어떤 채널이 무엇을 올렸나?
3. 카테고리별 트렌드는?

**레이아웃:**

```python
# dashboard_trends.py

import streamlit as st

st.title("🔍 YouTube 트렌드 대시보드")

# 1. 필터
col1, col2, col3 = st.columns(3)
with col1:
    date_range = st.date_input("기간", value=(today-7days, today))
with col2:
    category = st.multiselect("카테고리", ["전체", "게임", "먹방", "브이로그"])
with col3:
    sort_by = st.selectbox("정렬", ["조회수", "업로드 시간", "증가율"])

# 2. 핵심 인사이트 (자동 생성)
st.subheader("💡 오늘의 인사이트")
st.info("""
🔥 **주요 발견:**
- "특정 키워드" 주제 영상 5개 업로드 (전주 대비 +300%)
- 평균 조회수 50만 돌파 (역대 최고)
- 게임 카테고리에서 새로운 트렌드 감지

📌 **추천 액션:**
- 우리도 "특정 키워드" 주제 기획 고려
- 썸네일 스타일 참고 (밝은 색상 + 텍스트)
""")

# 3. 카테고리별 신규 영상 수
st.subheader("📊 카테고리별 동향")
fig = px.bar(category_counts, x="category", y="count", color="count")
st.plotly_chart(fig, use_container_width=True)

# 4. 급상승 키워드 (워드 클라우드 또는 막대)
st.subheader("🔤 인기 키워드")
col1, col2 = st.columns(2)
with col1:
    # 워드 클라우드 (Streamlit은 기본 지원 X, 이미지로 표시)
    st.image("wordcloud.png")
with col2:
    # Top 10 키워드
    st.bar_chart(top_keywords)

# 5. 채널별 신규 영상
st.subheader("📺 채널별 신규 영상")
for channel in channels:
    with st.expander(f"{channel.name} ({channel.new_video_count}개)"):
        for video in channel.new_videos:
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(video.thumbnail, width=120)
            with col2:
                st.write(f"**{video.title}**")
                st.write(f"조회수: {video.views:,} | 업로드: {video.published_at}")
                st.write(f"키워드: {', '.join(video.tags[:5])}")

# 6. 비교 분석
st.subheader("🆚 성과 비교")
fig3 = px.scatter(
    df,
    x="video_length",
    y="views",
    size="likes",
    color="channel",
    hover_data=["title"]
)
st.plotly_chart(fig3, use_container_width=True)
```

**화면 구성:**
```
┌─────────────────────────────────────────────────────┐
│  🔍 YouTube 트렌드 대시보드                          │
│  [기간 ▼] [카테고리 ▼] [정렬 ▼]                     │
├─────────────────────────────────────────────────────┤
│  💡 오늘의 인사이트                                  │
│  ┌─────────────────────────────────────────────┐   │
│  │ 🔥 주요 발견:                                │   │
│  │ - "특정 키워드" 주제 폭발적 증가              │   │
│  │                                             │   │
│  │ 📌 추천 액션:                                │   │
│  │ - 우리도 이 주제 기획 고려                   │   │
│  └─────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────┤
│  📊 카테고리별 동향                                  │
│  [막대 그래프: 카테고리별 신규 영상 수]              │
├─────────────────────────────────────────────────────┤
│  🔤 인기 키워드                                      │
│  ┌──────────────┬──────────────────────────────┐   │
│  │ [워드클라우드] │ Top 10:                      │   │
│  │              │ 1. 키워드1 (50회)            │   │
│  │              │ 2. 키워드2 (45회)            │   │
│  └──────────────┴──────────────────────────────┘   │
├─────────────────────────────────────────────────────┤
│  📺 채널별 신규 영상                                 │
│  ▼ 인기 게임 채널 A (3개)                            │
│     [썸네일] "영상 제목..."                          │
│              조회수: 50만 | 키워드: #게임, #리뷰     │
│                                                     │
│  ▼ 인기 먹방 채널 B (2개)                            │
└─────────────────────────────────────────────────────┘
```

---

### 5.2 공통 컴포넌트 설계

두 대시보드가 공유하는 컴포넌트:

```python
# components.py

import streamlit as st
import plotly.express as px

def render_kpi_card(label, value, delta=None, delta_color="normal"):
    """KPI 카드 렌더링"""
    st.metric(
        label=label,
        value=value,
        delta=delta,
        delta_color=delta_color
    )

def render_video_card(video):
    """영상 카드 렌더링"""
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(video.thumbnail, width=120)
    with col2:
        st.write(f"**{video.title}**")
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.caption(f"👁️ {video.views:,}")
        with metric_col2:
            st.caption(f"👍 {video.likes:,}")
        with metric_col3:
            st.caption(f"💬 {video.comments:,}")

def render_channel_selector(channels):
    """채널 선택기"""
    return st.multiselect(
        "채널 선택",
        options=channels,
        default=channels
    )

def render_time_series_chart(df, x, y, color=None, title=""):
    """시계열 차트"""
    fig = px.line(df, x=x, y=y, color=color, title=title)
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
```

---

### 5.3 데이터베이스 스키마 (재검토)

**두 대시보드를 지원하기 위한 스키마 수정:**

```sql
-- 채널 정보 (확장)
CREATE TABLE channels (
    channel_id VARCHAR(255) PRIMARY KEY,
    channel_name VARCHAR(255) NOT NULL,
    channel_handle VARCHAR(255),

    -- 소유 여부 (핵심!)
    ownership_type VARCHAR(50) DEFAULT 'benchmark',  -- 'owned' or 'benchmark'

    -- 카테고리 (트렌드 분석용)
    category VARCHAR(100),  -- 'gaming', 'food', 'vlog' 등

    -- 통계
    subscribers INTEGER,
    total_videos INTEGER,
    total_views INTEGER,

    -- 모니터링 설정
    monitor_enabled BOOLEAN DEFAULT TRUE,
    check_interval_minutes INTEGER DEFAULT 60,

    -- 메타데이터
    thumbnail_url TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 영상 정보 (확장)
CREATE TABLE videos (
    video_id VARCHAR(255) PRIMARY KEY,
    channel_id VARCHAR(255) NOT NULL,

    -- 기본 정보
    video_title TEXT NOT NULL,
    video_description TEXT,
    published_at TIMESTAMP NOT NULL,
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 메타데이터
    video_duration INTEGER,  -- seconds
    category_id VARCHAR(50),
    tags TEXT,  -- JSON array: ["tag1", "tag2"]

    -- 통계 (스냅샷)
    views INTEGER,
    likes INTEGER,
    comments_count INTEGER,

    -- 미디어
    thumbnail_url TEXT,

    FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE
);

-- 영상 통계 히스토리 (시계열 분석용) ⭐ 핵심!
CREATE TABLE video_stats_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id VARCHAR(255) NOT NULL,

    -- 통계 스냅샷
    views INTEGER,
    likes INTEGER,
    dislikes INTEGER,  -- API에서 제공 안 함 (deprecated)
    comments_count INTEGER,

    -- 계산된 메트릭
    view_growth_rate REAL,  -- 전일 대비 증가율
    engagement_rate REAL,   -- (likes + comments) / views

    -- 시간
    snapshot_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE
);

-- 키워드 추적 (트렌드 분석용) ⭐ 새로 추가
CREATE TABLE keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword VARCHAR(255) NOT NULL,
    category VARCHAR(100),

    -- 집계
    mention_count INTEGER DEFAULT 1,  -- 언급 횟수
    total_views INTEGER,  -- 해당 키워드 영상 총 조회수

    -- 기간
    date DATE NOT NULL,

    UNIQUE(keyword, date)
);

-- 영상-키워드 매핑
CREATE TABLE video_keywords (
    video_id VARCHAR(255),
    keyword_id INTEGER,

    PRIMARY KEY (video_id, keyword_id),
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE,
    FOREIGN KEY (keyword_id) REFERENCES keywords(id) ON DELETE CASCADE
);

-- 인덱스
CREATE INDEX idx_videos_published_at ON videos(published_at DESC);
CREATE INDEX idx_videos_channel_id ON videos(channel_id);
CREATE INDEX idx_videos_category ON videos(category_id);
CREATE INDEX idx_snapshots_video_time ON video_stats_snapshots(video_id, snapshot_at DESC);
CREATE INDEX idx_keywords_date ON keywords(date DESC);
```

---

### 5.4 프로젝트 구조 (재설계)

```
youtube-intelligence/
├── src/
│   ├── __init__.py
│   ├── collectors/            # 데이터 수집
│   │   ├── youtube_api.py     # YouTube API wrapper
│   │   ├── channel_collector.py
│   │   ├── video_collector.py
│   │   └── stats_collector.py  # 통계 스냅샷 수집
│   │
│   ├── analyzers/             # 데이터 분석
│   │   ├── performance_analyzer.py  # 우리 채널 분석
│   │   ├── trend_analyzer.py        # 트렌드 분석
│   │   ├── keyword_extractor.py     # 키워드 추출
│   │   └── insights_generator.py    # 인사이트 자동 생성
│   │
│   ├── database/              # 데이터베이스
│   │   ├── models.py          # ORM 모델 (SQLAlchemy)
│   │   ├── repository.py      # 데이터 접근 계층
│   │   └── migrations/        # 스키마 마이그레이션
│   │
│   └── utils/
│       ├── config.py
│       ├── logger.py
│       └── helpers.py
│
├── dashboards/                # Streamlit 대시보드
│   ├── components/            # 공통 컴포넌트
│   │   ├── kpi_card.py
│   │   ├── video_card.py
│   │   ├── charts.py
│   │   └── filters.py
│   │
│   ├── pages/                 # 대시보드 페이지
│   │   ├── 1_📊_Performance.py     # 성과 대시보드
│   │   ├── 2_🔍_Trends.py          # 트렌드 대시보드
│   │   └── 3_⚙️_Settings.py        # 설정
│   │
│   └── Home.py                # 메인 페이지 (라우팅)
│
├── scripts/
│   ├── collect_data.py        # 데이터 수집 스크립트 (cron)
│   ├── analyze_trends.py      # 트렌드 분석 스크립트
│   └── generate_insights.py   # 인사이트 생성 스크립트
│
├── config/
│   ├── channels_owned.yaml    # 우리 채널 목록
│   ├── channels_benchmark.yaml # 벤치마크 채널 목록
│   └── config.yaml            # 전역 설정
│
├── data/
│   ├── intelligence.db        # SQLite 데이터베이스
│   └── logs/                  # 로그 파일
│
├── tests/
│   ├── test_collectors.py
│   ├── test_analyzers.py
│   └── test_dashboards.py
│
├── requirements.txt
├── .env.example
└── README.md
```

---

### 5.5 실행 흐름

#### **자동 실행 (Cron)**
```bash
# 매일 새벽 6시: 데이터 수집
0 6 * * * /usr/bin/python3 /path/to/scripts/collect_data.py

# 매일 새벽 7시: 트렌드 분석
0 7 * * * /usr/bin/python3 /path/to/scripts/analyze_trends.py

# 매일 새벽 8시: 인사이트 생성
0 8 * * * /usr/bin/python3 /path/to/scripts/generate_insights.py
```

#### **수동 실행 (오전 9시 회의 전)**
```bash
# 대시보드 실행
streamlit run dashboards/Home.py
```

**브라우저 접속:**
```
http://localhost:8501
```

---

### 5.6 다음 단계 액션 플랜

**Phase 1: 데이터 수집 (1-2일)**
- [ ] YouTube API wrapper 구현
- [ ] SQLite 스키마 생성
- [ ] 기본 데이터 수집 스크립트 작성
- [ ] 테스트 (1-2개 채널로)

**Phase 2: 대시보드 A - 성과 모니터링 (2-3일)**
- [ ] Streamlit 기본 레이아웃
- [ ] KPI 카드 구현
- [ ] 시계열 차트
- [ ] 영상 리스트
- [ ] 테스트 및 피드백

**Phase 3: 대시보드 B - 트렌드 추적 (2-3일)**
- [ ] 키워드 추출 로직
- [ ] 카테고리별 분석
- [ ] 인사이트 자동 생성
- [ ] 트렌드 시각화

**Phase 4: 고도화 (1주)**
- [ ] 성능 최적화
- [ ] 에러 처리 강화
- [ ] 알림 기능 추가 (이메일, Discord)
- [ ] 문서화

---

## 6. 요약 및 권장사항

### ✅ 핵심 결정사항

1. **기술 스택: Streamlit**
   - 빠른 개발, Python 친화적
   - 나중에 Custom으로 전환 가능

2. **데이터베이스: SQLite + 시계열 스냅샷**
   - 간단하지만 강력
   - 히스토리 추적 가능

3. **이중 대시보드 설계**
   - 성과 모니터링 (우리 채널)
   - 트렌드 추적 (벤치마크 채널)

4. **자동화: Cron + 수동 대시보드**
   - 새벽에 데이터 수집/분석
   - 오전 회의 때 대시보드 확인

### 📚 참고 자료

**대시보드 디자인:**
- [Dashboard Design Best Practices - Toptal](https://www.toptal.com/designers/data-visualization/dashboard-design-best-practices)
- [Streamlit Gallery](https://streamlit.io/gallery)

**YouTube Analytics:**
- [YouTube Analytics Guide - Databox](https://databox.com/youtube-analytics-guide)
- JensBender 프로젝트 (우리가 분석한 것)

---

다음에 할 일:
1. 요구사항 최종 확인 (이 설계가 맞는지?)
2. 와이어프레임 상세화 (화면 스케치)
3. Phase 1 구현 시작
