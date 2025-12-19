# 점성술 가이드 - Celestial Sanctuary

## 1. 기본 개념

### 출생 차트 (Natal Chart / Birth Chart)
출생 시점의 천체 배치를 지도처럼 나타낸 것. 필요한 정보:
- 출생 날짜
- 출생 시간 (정확할수록 좋음)
- 출생 장소 (위도/경도)

### 12 하우스 (Houses)
하늘을 12개 영역으로 나눈 것. 각 하우스는 삶의 특정 영역을 담당.

| 하우스 | 영역 | 주인 행성 | 대응 별자리 |
|--------|------|-----------|-------------|
| 1st | 자아, 외모, 첫인상 | Mars | Aries |
| 2nd | 재산, 가치관, 자존감 | Venus | Taurus |
| 3rd | 소통, 학습, 형제 | Mercury | Gemini |
| 4th | 가정, 뿌리, 감정적 기반 | Moon | Cancer |
| 5th | 창조성, 연애, 즐거움 | Sun | Leo |
| 6th | 건강, 일상, 봉사 | Mercury | Virgo |
| 7th | 파트너십, 결혼, 계약 | Venus | Libra |
| 8th | 변화, 죽음/재생, 공유자원 | Pluto | Scorpio |
| 9th | 철학, 고등교육, 해외여행 | Jupiter | Sagittarius |
| 10th | 커리어, 명성, 사회적 지위 | Saturn | Capricorn |
| 11th | 커뮤니티, 친구, 희망 | Uranus | Aquarius |
| 12th | 무의식, 영성, 카르마 | Neptune | Pisces |

### 10 행성 (Planets)
| 행성 | 상징 | 지배 별자리 |
|------|------|-------------|
| Sun ☉ | 자아, 의식, 생명력 | Leo |
| Moon ☽ | 감정, 무의식, 본능 | Cancer |
| Mercury ☿ | 소통, 지성, 학습 | Gemini, Virgo |
| Venus ♀ | 사랑, 미, 가치 | Taurus, Libra |
| Mars ♂ | 행동, 욕망, 에너지 | Aries |
| Jupiter ♃ | 확장, 행운, 지혜 | Sagittarius |
| Saturn ♄ | 제한, 책임, 구조 | Capricorn |
| Uranus ♅ | 혁신, 자유, 변화 | Aquarius |
| Neptune ♆ | 꿈, 환상, 영성 | Pisces |
| Pluto ♇ | 변혁, 힘, 재생 | Scorpio |

---

## 2. 하우스 시스템 종류

### Whole Sign House (전체 별자리 하우스)
- **가장 간단한 시스템**
- Ascendant가 있는 별자리 = 1st House
- 그 다음 별자리 = 2nd House, ...
- 각 하우스가 정확히 30도

### Equal House (균등 하우스)
- Ascendant 도수에서 시작
- 각 하우스 정확히 30도
- Ascendant 도수가 각 하우스 시작점

### Placidus (플라시더스)
- **가장 널리 사용됨**
- 시간 기반 계산
- 하우스 크기가 불균등
- 극지방에서 계산 문제 발생

---

## 3. 앱 구현 전략

### Phase 1: 간단한 버전 (현재)
- Whole Sign House 시스템 사용
- 출생 날짜로 태양 별자리 계산
- 출생 시간으로 Ascendant 추정
- 행성 위치는 날짜 기반 테이블 사용

### Phase 2: 정확한 버전 (추후)
- Swiss Ephemeris 라이브러리 통합
- 또는 외부 API 사용 (AstroAPI 등)
- Placidus 하우스 시스템 지원
- 정확한 천문학적 계산

---

## 4. 수정구슬 3단계 로직

```
하우스 상태 결정:
1. 해당 하우스에 행성이 있는가?
   - 없음 → EMPTY (빈 방)
   - 있음 → 2번으로

2. 그 행성이 하우스의 주인인가?
   - 아님 → TENANT (손님)
   - 맞음 → OWNER_HOME (집주인 귀환)
```

### 예시
- 1st House에 Mars가 있음 → OWNER_HOME (Mars는 1st House 주인)
- 1st House에 Jupiter가 있음 → TENANT (Jupiter는 손님)
- 1st House에 행성 없음 → EMPTY

---

## 5. 별자리별 날짜 범위

| 별자리 | 시작일 | 종료일 |
|--------|--------|--------|
| Aries | 3/21 | 4/19 |
| Taurus | 4/20 | 5/20 |
| Gemini | 5/21 | 6/20 |
| Cancer | 6/21 | 7/22 |
| Leo | 7/23 | 8/22 |
| Virgo | 8/23 | 9/22 |
| Libra | 9/23 | 10/22 |
| Scorpio | 10/23 | 11/21 |
| Sagittarius | 11/22 | 12/21 |
| Capricorn | 12/22 | 1/19 |
| Aquarius | 1/20 | 2/18 |
| Pisces | 2/19 | 3/20 |

---

## 6. Ascendant (상승궁) 계산

Ascendant는 출생 시간에 동쪽 지평선에 떠오르는 별자리.

### 간단한 추정 방법
- 일출 시간 = 해당 날짜의 태양 별자리
- 2시간마다 다음 별자리로 이동
- 12별자리 × 2시간 = 24시간

```
Ascendant 추정:
1. 태양 별자리 확인 (출생 날짜)
2. 일출 시간 기준 = 태양 별자리가 Ascendant
3. 2시간마다 다음 별자리
4. (출생시간 - 일출시간) / 2 = 별자리 이동 수
```

---

## 참고 자료

- [House System Calculator](https://horoscopes.astro-seek.com/astrology-house-systems-calculator)
- [Compare House Systems](https://astrolibrary.org/compare-house-systems/)
- [House Systems Explained](https://www.bigskyastrology.com/house-systems-dividing-the-sky/)
- [Cafe Astrology](https://cafeastrology.com/free-natal-chart-report-whole-sign-houses.html)
