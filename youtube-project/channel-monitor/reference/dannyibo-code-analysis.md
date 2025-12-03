# youtube-data-analytics-tools (DannyIbo) 코드 분석 리포트

> **분석 방법론**: `code-analysis-methodology.md` 기준으로 작성
> **분석 일자**: 2025-10-20
> **프로젝트**: https://github.com/DannyIbo/youtube-data-analytics-tools

---

## 1. 프로젝트 개요

### 목적
- 여러 YouTube 채널 비교 (최대 3개)
- 영상 댓글 분석 (시계열, 감정 분석)
- 비디오 프로덕션 회사의 반복 업무 자동화

### 기술 스택
- **언어**: Python 3
- **웹 프레임워크**: Flask
- **데이터 처리**: Pandas, NumPy
- **시각화**: Matplotlib, Seaborn, WordCloud
- **API**: google-api-python-client (YouTube Data API v3)
- **감정 분석**: vaderSentiment

### 아키텍처
- 모놀리식 Flask 애플리케이션
- 메모리 기반 (데이터 영속성 없음)
- 정적 이미지 기반 시각화

---

## 2. 폴더 및 파일 구조

```
youtube-data-analytics-tools/
├── app.py                    # Flask 엔트리포인트 (130 라인)
├── requirements.txt          # 의존성 라이브러리
│
├── src/                      # 핵심 로직
│   ├── youtube_data_module.py  # YouTube API 래퍼 (671 라인) ★핵심★
│   ├── viz.py                  # 시각화 함수 (238 라인)
│   └── sql.py                  # 유틸리티 (11 라인)
│
├── templates/                # Jinja2 HTML 템플릿
│   ├── layout.html           # 베이스 레이아웃
│   ├── select_channels.html  # 채널 검색 결과
│   ├── select_video.html     # 영상 검색 결과
│   ├── channels.html         # 채널 비교 대시보드
│   └── video_comments.html   # 댓글 분석 결과
│
└── static/images/            # 생성된 플롯 이미지 저장
```

### 구조의 특징
- **평평한 계층**: 복잡한 디렉토리 중첩 없음 (간결함 우선)
- **MVC 패턴**: app.py (Controller), templates (View), src (Model)
- **기능별 모듈 분리**: API 호출, 시각화, 웹 라우팅
- **sql.py의 미스노머**: 실제로는 ID 생성 유틸리티 (DB 기능 없음)

---

## 3. 의존성 분석

| 라이브러리 | 버전 | 용도 | 선택 이유 추측 | 대안 |
|-----------|------|------|--------------|------|
| **pandas** | - | 데이터 처리 | API 응답을 DataFrame으로 변환, 분석 용이 | Polars, Dask |
| **flask** | - | 웹 프레임워크 | 가볍고 간단, 빠른 프로토타이핑 | Django, FastAPI |
| **matplotlib** | - | 기본 시각화 | Python 표준, 이미지 저장 간편 | Plotly, Bokeh |
| **seaborn** | - | 고급 시각화 | Matplotlib 래퍼, 예쁜 그래프 | Plotly Express |
| **numpy** | - | 수치 연산 | Pandas 의존성, 로그 변환 등 | - |
| **vaderSentiment** | - | 감정 분석 | 사전 훈련 모델, 설정 불필요 | TextBlob, Transformer |
| **google-api-python-client** | - | YouTube API | Google 공식 클라이언트 | 직접 HTTP 요청 |
| **google-auth-*** | - | 인증 | OAuth 지원 (미사용 코드 존재) | - |
| **pytz** | - | 시간대 처리 | UTC 타임스탬프 변환 | datetime (Python 3.9+) |
| **wordcloud** | - | 워드클라우드 | 텍스트 시각화 | stylecloud |

### 핵심 의존성 조합
- **Flask + Pandas**: 웹 인터페이스 + 데이터 분석
- **Matplotlib + Seaborn**: 정적 그래프 생성
- **vaderSentiment**: 감정 분석 (머신러닝 없이 사전 기반)

---

## 4. 실행 흐름

### 4.1 엔트리포인트: app.py

#### 초기화 과정
```python
# app.py:1-16
from flask import Flask, render_template, request
from src import youtube_data_module as ydt
from src import viz
import pandas as pd
import os
import logging

# 로깅 설정
logger = logging.getLogger('app_logger')
logger.setLevel(logging.INFO)

# 환경 변수에서 API 키 로드
API_KEY = os.getenv('YOUTUBE_API_KEY')

# Flask 앱 생성
app = Flask(__name__)
```

**환경 변수 의존**:
- `YOUTUBE_API_KEY` 필수
- Windows: `setx YOUTUBE_API_KEY "your-key"`
- Linux/Mac: `.bashrc`에 export

#### 서버 시작
```python
# app.py:129-130
if __name__ == '__main__':
    app.run(port=3000, debug=True)
```
- **포트**: 3000 (README에는 명시 안 됨, 코드에만 존재)
- **디버그 모드**: True (프로덕션 부적합)

### 4.2 라우트 구조

| 경로 | 메서드 | 기능 | 템플릿 | 복잡도 |
|------|--------|------|--------|--------|
| `/` | GET | 홈페이지 | `layout.html` | 낮음 |
| `/select_video` | GET | 영상 검색 | `select_video.html` | 낮음 |
| `/video_comments` | GET | 댓글 분석 | `video_comments.html` | **높음** |
| `/select_channels` | GET/POST | 채널 검색 | `select_channels.html` | 중간 |
| `/channels` | GET/POST | 채널 비교 | `channels.html` | **매우 높음** |

---

## 5. 핵심 기능 분석

### 5.1 채널 비교 기능

#### 처리 흐름
```
사용자: 채널 이름 입력 (최대 3개)
  ↓
/select_channels: YouTube에서 채널 검색
  ↓
사용자: 채널 선택 (라디오 버튼)
  ↓
/channels: 채널 데이터 수집 및 분석
  ↓
플롯 생성 + 테이블 렌더링
```

#### 코드 흐름 (app.py:90-127)
```python
@app.route('/channels', methods=['GET', 'POST'])
def channels():
    # 1. 채널 ID 추출 (24자 길이 체크)
    channel_ids = []
    for c_id in request.args:
        if len(result_dictionary[c_id]) == 24:
            channel_ids.append(result_dictionary[c_id])

    # 2. YouTube API 인증
    youtube = ydt.youtubeAPIkey(API_KEY)

    # 3. 모든 채널의 영상 데이터 수집
    video_df = ydt.get_channel_video_df(youtube, channel_ids)

    # 4. 시각화 생성 (4+N개)
    image_names = []
    image_names.append(viz.barplot_channel_video_count(video_df, channel_ids))
    image_names.append(viz.barplot_links(video_df, channel_ids))

    # 채널별 루프 (N개 채널 → N*2개 이미지)
    for channel_id in channel_ids:
        channel_video_df = video_df[video_df['channel_id'] == channel_id]
        # 히스토그램 + 워드클라우드
        image_names.append(viz.histogram_video_duration_count_single(...))
        image_names.append(viz.create_wordcloud(...))

    # 5. Top 5 영상 테이블
    df_table = viz.top_videos(video_df, metric='view', n=5)

    # 6. 템플릿 렌더링
    return render_template('channels.html', ...)
```

**주의할 점**:
- **파일명 길이 문제**: `'_'.join(channel_ids)` → 3개 이상 시 파일명 과도하게 길어짐
- **동기 처리**: 채널 수만큼 순차 API 호출 (병렬 처리 없음)

### 5.2 댓글 분석 기능

#### 처리 흐름
```
사용자: 영상 검색 (키워드)
  ↓
/select_video: 검색 결과 표시
  ↓
사용자: 영상 선택
  ↓
/video_comments: 댓글 수집 및 분석
  ↓
감정 분석 + 시각화 (워드클라우드, 시계열, 산점도)
```

#### 코드 흐름 (app.py:36-66)
```python
@app.route('/video_comments')
def video_comments():
    video_id = request.args.get('video_id')
    youtube = ydt.youtubeAPIkey(API_KEY)

    # 1. 댓글 수집 (모든 댓글 + 대댓글)
    all_snippets = ydt.get_all_comments(youtube, video_id)

    # 2. 데이터 변환
    comment_dict = ydt.extract_comments(all_snippets)
    comment_df = ydt.comments_to_df(all_snippets)

    # 3. 감정 분석
    comment_sentiment = ydt.analyze_comment_sentiments(comment_df)
    comment_sentiment2, pos_sent, neg_sent = viz.split_sentiment_pos_neg(comment_sentiment)

    # 4. 시각화 생성 (4개)
    image_names = []
    image_names.append(viz.create_wordcloud(comment_string, ...))
    image_names.append(viz.lineplot_cumsum_video_comments(...))
    image_names.append(viz.lineplot_cumsum_video_comments_pos_neg(...))
    image_names.append(viz.scatterplot_sentiment_likecount(...))

    # 5. 상관관계 계산
    like_count_sentiment_corr = round(comment_sentiment2.corr().loc['like_count'][5],2)

    return render_template('video_comments.html', ...)
```

---

## 6. YouTube API 사용 패턴

### 6.1 API 인증 (youtube_data_module.py:39-47)

```python
def youtubeAPIkey(DEVELOPER_KEY):
    '''Get YouTube Data API credentials via API Key'''
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # 로컬 개발용
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=DEVELOPER_KEY
    )
    return youtube
```

**특징**:
- API 키 방식 (OAuth 아님)
- `OAUTHLIB_INSECURE_TRANSPORT="1"` → HTTPS 검증 우회 (프로덕션 위험)

### 6.2 주요 API 엔드포인트

| 함수명 | API 엔드포인트 | 용도 | 할당량 비용 |
|--------|---------------|------|-----------|
| `youtubeSearchList` | `search().list` | 채널/영상 검색 | 100 |
| `videoIdList` | `channels().list` + `playlistItems().list` | 채널의 모든 영상 ID | 3 + N*1 |
| `video_snippets` | `videos().list` | 영상 상세 정보 | 1 + (파트별) |
| `get_comment_threads` | `commentThreads().list` | 댓글 + 대댓글 | 4 * 페이지 수 |

### 6.3 할당량 관리

#### 현재 문제점
```python
# get_comment_threads() - 비용 계산은 하지만 제한 안 함
costs = 0
cost_per_query = 0
if 'replies' in part:
    cost_per_query += 2
if 'snippet' in part:
    cost_per_query += 2

while commentThreadsNextPageToken != None:
    costs += cost_per_query
    # ... API 호출 ...

logger.info(f'Comment thread query costs: {costs}')  # 로그만 출력
```

**문제**:
- 비용 계산 후 로깅만 할 뿐, 제한 없음
- 하루 10,000 할당량 초과 가능성
- README의 "To Dos"에 명시된 미해결 문제

#### 페이지네이션 처리
```python
# videoIdList() - 50개씩 페이지네이션
playlistNextPageToken = ''
while playlistNextPageToken != None:
    requestPlaylistItems = youtube.playlistItems().list(
        part="snippet",
        maxResults=50,
        pageToken=playlistNextPageToken,
        playlistId=channelUploadPlaylistID
    )
    response = requestPlaylistItems.execute()
    # ... 비디오 ID 수집 ...
    playlistNextPageToken = response.get('nextPageToken')
```

**좋은 점**:
- `nextPageToken` 활용으로 모든 데이터 수집
- `maxResults=50` → API 최대값 활용

### 6.4 복잡한 댓글 수집 로직

#### 문제: 대댓글 5개 이상 처리
YouTube API의 `commentThreads.list`는 대댓글을 최대 5개까지만 반환. 5개 초과 시 별도 호출 필요.

#### 해결책 (get_all_comments 함수)
```python
# youtube_data_module.py:487-558
def get_all_comments(youtube, video_id):
    # 1. 모든 댓글 스레드 가져오기 (대댓글 5개까지 포함)
    thread_snippets = get_comment_threads(youtube, part="snippet,replies", video_id=video_id)

    # 2. 대댓글 5개 초과 스레드 찾기
    thread_ids_with_more_replies = {}
    already_downloaded_replies = {}

    for t_id in thread_snippets:
        if t_id['snippet']['totalReplyCount'] > 5:
            thread_ids_with_more_replies[t_id['id']] = True
            # 이미 받은 대댓글 기록
            for reply_id in t_id['replies']['comments']:
                already_downloaded_replies[reply_id['id']] = True

    # 3. 추가 대댓글 ID 가져오기
    reply_ids = {}
    for id_string in thread_ids_with_more_replies:
        replies = get_comments_list(youtube, part="id", parent_id=id_string)
        for r_id in replies['items']:
            if r_id['id'] not in already_downloaded_replies:
                reply_ids[r_id['id']] = True

    # 4. 추가 대댓글 상세 정보 가져오기
    reply_snippets = []
    for id_string in list_slice(list(reply_ids), n=50):
        r_snippets = get_comments_list(youtube, part="snippet", id=id_string)
        reply_snippets += r_snippets['items']

    # 5. 모두 합치기
    all_snippets = thread_snippets + reply_snippets + already_downloaded_replies
    return all_snippets
```

**복잡도 이유**:
1. API 제약 우회 (5개 대댓글 제한)
2. 중복 제거 (이미 받은 대댓글)
3. 배치 처리 (50개씩)

---

## 7. 데이터 구조

### 7.1 영상 데이터 (snippets_to_dict)

**DataFrame 스키마**:
```python
{
    'video_id': str,              # YouTube 영상 ID
    'published_at': datetime,     # 업로드 시간
    'channel_id': str,            # 채널 ID
    'title': str,                 # 영상 제목
    'description': str,           # 설명
    'channel_title': str,         # 채널 이름
    'tags': list,                 # 태그 리스트
    'category_id': str,           # 카테고리 ID
    'duration': str,              # "PT1H23M09S" 형식
    'duration_sec': int,          # 초 단위 변환
    'view_count': int,            # 조회수
    'like_count': int,            # 좋아요
    'dislike_count': int,         # 싫어요 (deprecated)
    'comment_count': int,         # 댓글 수
    'thumbnails_default': str,    # 썸네일 URL
    # ... 기타 메타데이터 ...
}
```

**duration 파싱**:
```python
# youtube_data_module.py:193-198
def get_duration_sec(pt):
    '''PT1H23M09S → 초 단위'''
    pattern = 'PT(\d*H)?(\d*M)?(\d*S)?'
    timestamp = [to_int(x) for x in re.findall(pattern, pt)[0]]
    duration_sec = timestamp[0] * 3600 + timestamp[1] * 60 + timestamp[2]
    return duration_sec
```

### 7.2 댓글 데이터 (comments_to_df)

**DataFrame 스키마**:
```python
{
    'id': str,                    # 댓글 ID (인덱스)
    'text_original': str,         # 댓글 원문
    'like_count': int,            # 댓글 좋아요
    'published_at': datetime,     # 댓글 작성 시간
    'total_reply_count': int      # 대댓글 수
}
```

### 7.3 감정 분석 결과

**vaderSentiment 출력**:
```python
{
    'neg': float,       # 부정 점수 (0-1)
    'neu': float,       # 중립 점수 (0-1)
    'pos': float,       # 긍정 점수 (0-1)
    'compound': float   # 복합 점수 (-1~1)
}
```

**compound 기준**:
- `< -0.5`: 부정
- `-0.5 ~ 0.5`: 중립
- `> 0.5`: 긍정

---

## 8. 시각화 로직

### 8.1 파일 저장 방식

**패턴**:
```python
# viz.py 전반
image_name = f'static/images/{식별자}_{플롯유형}.png'
plt.savefig(image_name, dpi=100)
return image_name  # 템플릿에서 <img src="{{image_name}}">
```

**문제점** (README To Dos에 명시):
1. **삭제 안 함**: 플롯 이미지가 계속 쌓임
2. **파일명 충돌**: 동일 채널 재분석 시 덮어쓰기
3. **파일명 길이**: 채널 ID 3개 조합 시 긴 파일명

### 8.2 주요 플롯 함수

#### 채널 비교 플롯

**1. 영상 개수 막대 그래프**
```python
# viz.py:15-29
def barplot_channel_video_count(df_all, channel_ids):
    channel_ids_string = '_'.join(channel_ids)  # 파일명 생성
    image_name = f'static/images/{channel_ids_string}_barplot_channel_video_count.png'

    plt.figure(figsize=(10, 5))
    df_all.groupby('channel_title').size().sort_values(ascending=False).plot.bar()
    plt.title('Video Counts per Channel')
    plt.savefig(image_name, dpi=100)
    return image_name
```

**2. 링크 분석 막대 그래프**
```python
# viz.py:91-116
def barplot_links(video_df, channel_ids):
    # 클릭 가능 링크 체크 ('http' 포함 여부)
    video_df['Links in decription'] = video_df['description'].str.contains('http').apply(
        lambda x: 'Clickable Link' if x else 'No clickable Link'
    )

    # Seaborn catplot
    g = sns.catplot(x="channel_title",
                    y="video_id",
                    hue="Links in decription",
                    data=video_df,
                    kind="bar")
    ...
```

**왜 링크 분석?**
- README에 명시 안 됨, 추측: SEO/마케팅 전략 분석용
- `https://` 형식만 클릭 가능 (YouTube 정책)

**3. 영상 길이 히스토그램**
```python
# viz.py:62-89
def histogram_video_duration_count_single(df_all, channel_id, channel_title):
    # 이상치 제거 (IQR 방식)
    outlier = (df_all['duration_sec'].describe()['75%'] -
               df_all['duration_sec'].describe()['25%']) * 1.5 +
               df_all['duration_sec'].describe()['75%']
    df_all = df_all[df_all['duration_sec'] <= outlier]

    df_all['duration_min'] = df_all['duration_sec'] / 60
    bin_size = df_all['duration_min'].max()

    plt.hist(df_all['duration_min'], bins=bin_size, alpha=0.5)
    ...
```

**이상치 처리**:
- IQR * 1.5 방식
- 예: 24시간 라이브 스트림 제외

#### 댓글 분석 플롯

**1. 시계열 라인 플롯**
```python
# viz.py:189-205
def lineplot_cumsum_video_comments_pos_neg(comment_sentiment, pos_sent, neg_sent, video_id):
    plt.plot('published_at', 'cumsum', data=pos_sent, color='green', label="Positive")
    plt.plot('published_at', 'cumsum', data=neg_sent, color='red', label="Negative")
    ...
```

**2. 감정-좋아요 산점도**
```python
# viz.py:207-224
def scatterplot_sentiment_likecount(comment_sentiment, pos_sent, neg_sent, video_id):
    # 로그 변환 (좋아요 0개 처리)
    plt.scatter(comment_sentiment['compound'],
                np.log1p(comment_sentiment['like_count']),
                label='Neutral')
    ...
```

**`np.log1p` 사용 이유**:
- 좋아요 0개 시 log(0) = -∞ 방지
- log1p(x) = log(1+x)

**3. 워드클라우드**
```python
# viz.py:118-154
def create_wordcloud(text, stopwords=STOPWORDS, ...):
    wordcloud = WordCloud(
        max_font_size=50,
        max_words=100,
        background_color="white",
        stopwords=stopwords,
        collocations=False  # 단어 쌍 비활성화
    ).generate(text)
    ...
```

**불용어 문제** (README To Dos):
- 영어만 제거 (`STOPWORDS`)
- 한국어, 일본어 등 미지원

---

## 9. 알고리즘 및 비즈니스 로직

### 9.1 채널 ID 검증

```python
# app.py:96-98
for c_id in result_dictionary:
    if len(result_dictionary[c_id]) == 24:
        channel_ids.append(result_dictionary[c_id])
```

**검증 로직**:
- YouTube 채널 ID = 항상 24자
- 예: `UCqC_GY2ZiENFz2pwL0cSfAw`

**문제**:
- 형식 검증 없음 (정규식 없음)
- 24자 아무 문자열도 통과

### 9.2 리스트 배치 처리

```python
# youtube_data_module.py:118-130
def list_slice(input_list, n=50):
    '''리스트를 n개씩 묶어서 쉼표로 연결'''
    s = 0
    e = n
    list_slices = []
    while s < len(input_list):
        list_slices.append(','.join(input_list[s:e]))
        s = e
        e += n
    return list_slices
```

**사용처**:
- API 호출 최적화
- `videos().list(id="id1,id2,...,id50")` → 한 번에 50개

**예시**:
```python
input_list = ['id1', 'id2', ..., 'id120']
list_slice(input_list, 50)
# 출력: ['id1,id2,...,id50', 'id51,...,id100', 'id101,...,id120']
```

### 9.3 임시 ID 생성

```python
# sql.py:4-10
def set_temp_id():
    '''Unix 타임스탬프 + 랜덤 4자리'''
    time_id = str(int(time.time()))       # 예: "1634567890"
    rand_id = str(random.randint(1000,9999))  # 예: "1234"
    temp_id = time_id + "_" + rand_id     # "1634567890_1234"
    return temp_id
```

**용도**:
- 워드클라우드 파일명 (video_id 없을 때)

**sql.py 네이밍 문제**:
- 실제 SQL/DB 기능 없음
- 유틸리티 함수 1개만 존재

---

## 10. 에러 처리 및 예외 상황

### 10.1 에러 처리 패턴

**현재 상태**: 에러 처리 거의 없음

**예시 - None 처리만 존재**:
```python
# youtube_data_module.py:268-272
df_data['view_count'].append(int(i['statistics'].get('viewCount') or 0))
df_data['like_count'].append(int(i['statistics'].get('likeCount') or 0))
# .get() 사용으로 KeyError 방지, or 0으로 None 처리
```

**문제점**:
1. **API 할당량 초과**: try-except 없음
2. **네트워크 오류**: 재시도 없음
3. **잘못된 입력**: 검증 부족

### 10.2 로그 주석으로 남은 디버깅 흔적

```python
# youtube_data_module.py:505-514
if t_id.get('replies') != None:
    for reply_id in t_id['replies']['comments']:
        already_downloaded_replies[reply_id['id']] = True
else:
    # 개발자의 디버깅 메시지
    logger.info(f"* * * * * {t_id['id']} would throw a key error for 'replies' * * * * * ")
```

**해석**:
- 개발 중 KeyError 발생 경험
- 근본 원인 미해결, 회피 코드로 처리

### 10.3 알려진 버그

**README To Dos에 명시**:
1. **플롯에 float 표시**: 정수여야 하는데 소수점 표시
2. **파일 정리 안 됨**: 디스크 공간 문제 가능성
3. **파일명 길이**: 채널 많으면 OS 제한 초과 가능
4. **API 할당량**: 사전 예측 없음
5. **불용어**: 영어만 지원

---

## 11. 주요 학습 포인트

### 11.1 좋은 패턴

#### 1. 모듈화
```python
# app.py는 라우팅만, 로직은 src/로 분리
from src import youtube_data_module as ydt
from src import viz

# app.py:101
video_df = ydt.get_channel_video_df(youtube, channel_ids)
image_names.append(viz.barplot_channel_video_count(video_df, channel_ids))
```

#### 2. 함수 docstring
```python
def get_comment_threads(...):
    '''Return a .json with top-level comments and meta data.
    Specify exactly one filter out of: channel_id, comment_thread_id, video_id.
    See detailed info in the documentation: https://...
    Quota costs: id: 0, replies: 2, snippet: 2'''
```

#### 3. 페이지네이션 처리
```python
while nextPageToken != None:
    response = api_call(pageToken=nextPageToken)
    # 데이터 수집
    nextPageToken = response.get('nextPageToken')
```

### 11.2 피해야 할 안티패턴

#### 1. 하드코딩
```python
# app.py:130
app.run(port=3000, debug=True)  # 환경 변수로 관리해야 함
```

#### 2. 매직 넘버
```python
# app.py:97
if len(result_dictionary[c_id]) == 24:  # 24가 무엇인지 상수로 정의
```

#### 3. 파일명에 ID 직접 사용
```python
# viz.py:18
channel_ids_string = '_'.join(channel_ids)  # 해시나 인덱스 사용 권장
```

#### 4. 동기 처리
```python
# app.py:108-115 - 채널마다 순차 처리
for channel_id in channel_ids:
    # API 호출 (병렬 가능)
```

---

## 12. 개선 가능 영역

### 12.1 성능 최적화

**현재 문제**:
- 채널 3개 분석 시 모든 영상 순차 다운로드
- 예: 각 채널 1000개 영상 = 3000개 API 호출

**개선안**:
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def fetch_channel_data(youtube, channel_id):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        video_df = await loop.run_in_executor(
            executor, ydt.get_channel_video_df, youtube, [channel_id]
        )
    return video_df

# 병렬 처리
video_dfs = await asyncio.gather(*[
    fetch_channel_data(youtube, cid) for cid in channel_ids
])
```

### 12.2 API 할당량 관리

**추가할 기능**:
```python
class QuotaManager:
    def __init__(self, daily_limit=10000):
        self.daily_limit = daily_limit
        self.used = self.load_from_cache()  # Redis or file

    def estimate_cost(self, channel_ids, include_comments=False):
        cost = 0
        for cid in channel_ids:
            video_count = self.estimate_video_count(cid)
            cost += 3  # channels.list
            cost += (video_count // 50 + 1) * 1  # playlistItems.list
            cost += (video_count // 50 + 1) * 8  # videos.list with all parts
            if include_comments:
                cost += video_count * 4  # rough estimate
        return cost

    def check_and_reserve(self, cost):
        if self.used + cost > self.daily_limit:
            raise QuotaExceededError(f"Need {cost}, have {self.daily_limit - self.used}")
        self.used += cost
        self.save_to_cache()
```

### 12.3 데이터 영속성

**현재**: 메모리만, 재분석 시 API 재호출

**개선안**:
```python
# SQLite 추가
import sqlite3

def save_video_data(video_df, db_path='data.db'):
    conn = sqlite3.connect(db_path)
    video_df.to_sql('videos', conn, if_exists='append', index=False)
    conn.close()

def load_cached_data(channel_id, max_age_hours=24):
    conn = sqlite3.connect('data.db')
    query = f"""
    SELECT * FROM videos
    WHERE channel_id = '{channel_id}'
    AND date_data_created > datetime('now', '-{max_age_hours} hours')
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df if not df.empty else None
```

### 12.4 파일 정리 자동화

**방법 1: 세션 종료 시 삭제**
```python
import atexit
import glob

def cleanup_images():
    for img in glob.glob('static/images/*.png'):
        os.remove(img)

atexit.register(cleanup_images)
```

**방법 2: TTL 기반 정리**
```python
import time
from pathlib import Path

def clean_old_images(max_age_seconds=3600):
    now = time.time()
    for img_path in Path('static/images').glob('*.png'):
        if now - img_path.stat().st_mtime > max_age_seconds:
            img_path.unlink()

# 주기적 실행 (APScheduler 사용)
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(clean_old_images, 'interval', hours=1)
scheduler.start()
```

### 12.5 10개+ 채널 지원

**파일명 문제 해결**:
```python
import hashlib

def generate_safe_filename(channel_ids):
    # MD5 해시 사용
    ids_string = '_'.join(sorted(channel_ids))  # 정렬로 일관성
    hash_digest = hashlib.md5(ids_string.encode()).hexdigest()[:8]
    return f'compare_{hash_digest}'

# 사용
image_name = f'static/images/{generate_safe_filename(channel_ids)}_barplot.png'
```

**동적 UI**:
```html
<!-- 채널 추가 버튼 -->
<button onclick="addChannelInput()">+ Add Channel</button>
<div id="channel-inputs">
    <input name="channel_1" placeholder="Channel 1">
</div>

<script>
let channelCount = 1;
function addChannelInput() {
    channelCount++;
    const div = document.getElementById('channel-inputs');
    const input = document.createElement('input');
    input.name = `channel_${channelCount}`;
    input.placeholder = `Channel ${channelCount}`;
    div.appendChild(input);
}
</script>
```

---

## 13. 우리 프로젝트에 적용할 교훈

### 13.1 재사용 가능한 코드

**가져올 것**:
1. `list_slice()` - 배치 처리 유틸
2. `get_duration_sec()` - PT 형식 파싱
3. `get_all_comments()` - 대댓글 5개 이상 처리 로직
4. `snippets_to_dict()` - API 응답 → DataFrame 변환 패턴

### 13.2 피할 것

1. **파일명에 ID 직접 사용** → 해시 사용
2. **데이터 영속성 없음** → 초기부터 DB 설계
3. **에러 처리 부재** → try-except + 재시도
4. **동기 처리** → asyncio 고려

### 13.3 개선하여 적용

**구조**:
```
our-project/
├── api/
│   ├── youtube_client.py      # DannyIbo의 youtube_data_module 개선판
│   └── quota_manager.py       # 할당량 관리 (신규)
├── storage/
│   ├── database.py            # SQLite/MySQL (신규)
│   └── cache.py               # Redis (선택)
├── visualization/
│   ├── plots.py               # DannyIbo의 viz.py 개선판
│   └── dashboard.py           # 인터랙티브 대시보드 (Plotly)
└── web/
    ├── app.py                 # Flask
    └── background_tasks.py    # APScheduler (신규)
```

### 13.4 기술 스택 선택 기준

| 요구사항 | DannyIbo 선택 | 우리 선택 (제안) | 이유 |
|---------|--------------|----------------|------|
| 데이터 저장 | 없음 | SQLite | 시계열 분석 필수 |
| 스케줄링 | 수동 | APScheduler | 자동 모니터링 |
| 시각화 | Matplotlib | Plotly | 인터랙티브 |
| 비동기 | 없음 | asyncio | 10개+ 채널 |
| 테스트 | 없음 | pytest | 신뢰성 |

---

## 14. 결론

### 프로젝트 평가

**강점**:
- 간결한 코드 (총 1050줄)
- 빠른 프로토타이핑
- 실무 문제 해결에 집중

**약점**:
- 프로덕션 레벨 아님
- 확장성 제한 (3채널)
- 데이터 영속성 부재

**적합한 사용 사례**:
- 개인 프로젝트
- 일회성 분석
- 학습용 참고 코드

**부적합한 사용 사례**:
- 프로덕션 서비스
- 대규모 채널 분석 (10개 이상)
- 장기 트렌드 추적

### 핵심 인사이트

1. **YouTube API는 복잡하다**: 대댓글, 페이지네이션, 할당량 등
2. **파일 관리가 중요하다**: 임시 파일 정리 필수
3. **3개 제한의 이유**: 기술적 제약 (파일명) + 실용성
4. **감정 분석은 간단할 수 있다**: vaderSentiment로 충분

### 다음 단계

1. JensBender 프로젝트 분석 (프로덕션급 비교)
2. YouTube Data API v3 공식 문서 정리
3. `google-api-python-client` 라이브러리 심층 분석
4. 우리 프로젝트 아키텍처 설계

---

**분석 방법론 준수 체크리스트**:
- [x] Phase 1: 프로젝트 구조 파악
- [x] Phase 2: 의존성 분석
- [x] Phase 3: 엔트리포인트 분석
- [x] Phase 4-6: 핵심 로직, API, 데이터 구조
- [x] Phase 7: 알고리즘 분석
- [x] Phase 8: 에러 처리
- [x] Phase 9: 배포 (Flask 로컬 서버)
- [x] Phase 10: 문서화 및 종합
