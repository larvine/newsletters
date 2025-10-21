# Newsletter Dataset Generator

Newsletter 파일들을 파싱하여 JSON 형식의 데이터셋을 생성하고, 데이터셋으로부터 새로운 newsletter를 생성하는 도구 모음입니다.

## 도구 목록

### 1. `create_dataset.py` - 데이터셋 생성
- **git log 기반 파일 검색**: 최근에 merge된 newsletter 파일을 자동으로 찾기
- `_newsletters` 디렉토리의 마크다운 파일을 자동으로 파싱
- HTML 콘텐츠에서 포스트 정보 추출 (제목, URL, 이미지, 날짜)
- JSON 형식으로 데이터셋 생성
- **레이아웃 타입 자동 할당**: 4개씩 grid, 나머지는 wide로 구분

### 2. `create_newsletter_from_git.sh` - 원클릭 자동화
- git log → 레이아웃 할당된 데이터셋 생성
- 간편한 쉘 스크립트 인터페이스

## 사용법

### 🚀 빠른 시작 (권장)

```bash
# 레이아웃이 할당된 데이터셋 생성
./create_newsletter_from_git.sh -l 6 -g 4
```

### 📝 수동 사용

```bash
# 레이아웃 타입 포함하여 데이터셋 생성
python3 create_dataset.py -l 6 --assign-layout -g 4

# 2024-10-01 이후 추가된 파일만
python3 create_dataset.py -s 2024-10-01 --assign-layout

# git 사용하지 않고 디렉토리 전체
python3 create_dataset.py --no-git --assign-layout
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
    "layout": "wide"
  },
  {
    "file": "_newsletters/2025-10-21-blog-sample.md",
    "image": "/assets/images/default-newsletter.png",
    "title": "Bug fix",
    "date": "2025-10-02T17:25:05Z",
    "url": "https://github.com/jekyll/jekyll/issues/9879",
    "newsletter_type": "blog",
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
- `layout`: 레이아웃 타입 (`wide` 또는 `grid`) - `--assign-layout` 사용시

## 예제

### 예제 1: 기본 워크플로우 (자동화)

```bash
# 레이아웃이 할당된 데이터셋 생성
./create_newsletter_from_git.sh -l 6 -g 4
```

출력:
```
🚀 Newsletter 데이터셋 생성 시작...

📂 git log에서 최근 추가된 newsletter 파일 검색 중... (since: 2024-10-01)
   발견된 파일: 2개

파싱 중: 2025-10-21-blog-sample.md (추가일: 2025-10-21)
  → 8개 포스트 발견

📐 레이아웃 할당: Wide 1개, Grid 5개

✅ 총 6개의 포스트를 newsletter_dataset.json에 저장했습니다.

✅ 완료!
   생성된 파일: newsletter_dataset.json
```

**레이아웃 구조 (6개 포스트, grid-size=4):**
- 1번 포스트 → `"layout": "wide"` (Featured 영역)
- 2~5번 포스트 → `"layout": "grid"` (Grid 영역 4개)
- 6번 포스트 → `"layout": "grid"` (Grid 영역 1개)

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
./create_newsletter_from_git.sh -l 10 -g 6
```

**레이아웃 구조 (10개 포스트, grid-size=6):**
- 1번 포스트 → `"layout": "wide"`
- 2~7번 포스트 → `"layout": "grid"` (6개)
- 8번 포스트 → `"layout": "wide"`
- 9~10번 포스트 → `"layout": "grid"` (2개)

## 요구사항

- Python 3.6 이상
- 표준 라이브러리만 사용 (추가 설치 불필요)

## 라이센스

MIT
