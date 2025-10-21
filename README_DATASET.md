# Newsletter Dataset Generator

Newsletter 파일들을 파싱하여 JSON 형식의 데이터셋을 생성하는 도구입니다.

## 주요 기능

### `create_dataset.py`

- **git log 기반 파일 검색**: 최근에 merge된 newsletter 파일을 자동으로 찾기
- `_newsletters` 디렉토리의 마크다운 파일을 자동으로 파싱
- HTML 콘텐츠에서 포스트 정보 추출 (제목, URL, 이미지, 날짜, tags)
- JSON 형식으로 데이터셋 생성
- **스마트 레이아웃 할당**:
  - `featured` tag가 있는 포스트 → 자동으로 `wide` 레이아웃
  - 나머지 포스트 → 4개씩 grid, 그 사이에 wide 배치

## 사용법

## Newsletter 파일 형식

Front matter에 posts 배열로 포스트 정보를 저장:

```yaml
---
layout: newsletter
title: "Weekly Newsletter"
date: 2025-10-21
type: blog
posts:
  - title: "Featured Post"
    url: "https://github.com/..."
    image: "/assets/images/..."
    date: "2025-10-21T10:00:00Z"
    tags: ["featured"]
  - title: "Regular Post"
    url: "https://github.com/..."
    image: "/assets/images/..."
    date: "2025-10-20T10:00:00Z"
    tags: []
---

Newsletter content...
```

## 사용법

```bash
# 기본 사용
python3 create_dataset.py -d _newsletters --no-git

# git log로 최근 추가된 파일만
python3 create_dataset.py -d _newsletters -s 2024-10-01

# 특정 개수로 제한
python3 create_dataset.py -d _newsletters --no-git -l 5
```

**주요 옵션:**
- `-l, --limit`: 포함할 최대 포스트 수
- `-g, --grid-size`: Grid 영역에 배치할 포스트 개수 (기본: 4)
- `--assign-layout`: 레이아웃 타입(wide/grid) 자동 할당
- `-s, --since`: git log 사용시 이 날짜 이후의 파일만 (기본: 2024-01-01)
- `-d, --dir`: Newsletter 디렉토리 경로 (기본: _newsletters)
- `-o, --output`: 출력 JSON 파일명 (기본: newsletter_dataset.json)
- `--no-git`: git 사용 안 함

## 출력 형식

```json
[
  {
    "file": "_newsletters/2025-10-21-blog-sample.md",
    "layout": "newsletter",
    "title": "Jekyll 뉴스레터 예제",
    "date": "2025-10-21",
    "type": "blog"
  },
  {
    "file": "_newsletters/2025-10-21-mosaic-sample.md",
    "layout": "newsletter",
    "title": "GitHub 업데이트",
    "date": "2025-10-21",
    "type": "mosaic"
  }
]
```

각 항목은 다음 필드를 포함합니다:

- `file`: Newsletter 파일 경로
- `layout`: 레이아웃 이름 (front matter의 layout)
- `title`: Newsletter 제목 (front matter의 title)
- `date`: 날짜 (front matter의 date)
- `type`: Newsletter 타입 (front matter의 type)
- 기타 front matter에 있는 모든 변수

## 예제

## 예제

### 예제 1: 기본 사용

```bash
python3 create_dataset.py -d _newsletters --no-git
```

출력:
```
📂 _newsletters 디렉토리의 모든 파일 처리 중...

파싱 중: 2025-10-21-mosaic-sample.md
  → 1개 포스트 발견
파싱 중: 2025-10-21-blog-sample.md
  → 1개 포스트 발견

✅ 총 2개의 newsletter를 newsletter_dataset.json에 저장했습니다.
```

### 예제 2: git log로 최근 파일만

```bash
python3 create_dataset.py -d _newsletters -s 2024-10-01
```

### 예제 3: 템플릿에서 사용

생성된 데이터셋을 템플릿에서 활용:

```liquid
{% for newsletter in newsletters %}
  <div class="newsletter-item">
    <h2>{{ newsletter.title }}</h2>
    <p>{{ newsletter.date }}</p>
    <a href="{{ newsletter.file }}">보기</a>
  </div>
{% endfor %}
```

## 요구사항

- Python 3.6 이상
- 표준 라이브러리만 사용 (추가 설치 불필요)

## 라이센스

MIT
