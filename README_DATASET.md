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

### 기본 사용

```bash
# 레이아웃이 할당된 데이터셋 생성
python3 create_dataset.py -d _newsletters --no-git --assign-layout

# 특정 개수만
python3 create_dataset.py -d _newsletters --no-git -l 6 --assign-layout

# Grid 크기 커스터마이징
python3 create_dataset.py -d _newsletters --no-git -l 10 --assign-layout -g 6
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
    "image": "/assets/images/default-newsletter.png",
    "title": "Update resources.md",
    "date": "2025-10-06T09:08:54Z",
    "url": "https://github.com/jekyll/jekyll/pull/9880",
    "newsletter_type": "blog",
    "tags": ["featured"],
    "layout": "wide"
  },
  {
    "file": "_newsletters/2025-10-21-blog-sample.md",
    "image": "/assets/images/default-newsletter.png",
    "title": "Bug fix",
    "date": "2025-10-02T17:25:05Z",
    "url": "https://github.com/jekyll/jekyll/issues/9879",
    "newsletter_type": "blog",
    "tags": [],
    "layout": "grid"
  }
]
```

각 포스트는 다음 필드를 포함합니다:

- `file`: 소스 newsletter 파일 경로
- `image`: 포스트 이미지 URL
- `title`: 포스트 제목
- `date`: 포스트 날짜 (ISO 8601 형식)
- `url`: 포스트 링크 URL
- `newsletter_type`: Newsletter 타입 (blog, mosaic 등)
- `tags`: 태그 배열 (wide-section에 있으면 `["featured"]` 자동 추가)
- `layout`: 레이아웃 타입 (`wide` 또는 `grid`) - `--assign-layout` 사용시

## 예제

## 예제

### 예제 1: 기본 사용

```bash
python3 create_dataset.py -d _newsletters --no-git -l 6 --assign-layout
```

출력:
```
📂 _newsletters 디렉토리의 모든 파일 처리 중...

파싱 중: 2025-10-21-test.md
  → 6개 포스트 발견

📐 레이아웃 할당: Wide 2개, Grid 4개

✅ 총 6개의 포스트를 newsletter_dataset.json에 저장했습니다.
```

**레이아웃 로직:**
1. `featured` tag가 있는 포스트 → `wide` (1개)
2. 일반 포스트 중 첫 번째 → `wide` (1개)
3. 나머지 → `grid` (4개)

### 예제 2: 템플릿에서 사용

생성된 데이터셋을 템플릿에서 사용:

```liquid
{% for post in posts %}
  {% if post.layout == "wide" %}
    <div class="wide-section">
      <div class="featured-post">
        <a href="{{ post.url }}">
          <img src="{{ post.image }}" alt="{{ post.title }}">
        </a>
        <h2>{{ post.title }}</h2>
      </div>
    </div>
  {% elsif post.layout == "grid" %}
    <div class="grid-item">
      <a href="{{ post.url }}">
        <img src="{{ post.image }}" alt="{{ post.title }}">
      </a>
      <h3>{{ post.title }}</h3>
    </div>
  {% endif %}
{% endfor %}
```

### 예제 3: Grid 크기 변경

```bash
# 6개씩 grid에 배치
python3 create_dataset.py -l 10 --assign-layout -g 6
```

**레이아웃 구조 (10개 포스트, grid-size=6, featured 1개):**
- Featured 포스트 1개 → `wide`
- 일반 포스트 1개 → `wide`
- 일반 포스트 6개 → `grid`
- 일반 포스트 1개 → `wide`
- 일반 포스트 1개 → `grid`

## 레이아웃 할당 규칙

1. **Featured 우선**: `tags`에 `"featured"`가 있으면 무조건 `layout: "wide"`
2. **일반 포스트**: grid_size개씩 묶어서, 각 그룹 앞에 1개를 `wide`로 배치
3. **Front matter 기반**: Newsletter 파일의 front matter에서 posts 배열을 파싱

## 요구사항

- Python 3.6 이상
- 표준 라이브러리만 사용 (추가 설치 불필요)

## 라이센스

MIT
