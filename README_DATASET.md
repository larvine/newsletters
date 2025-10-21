# Newsletter Dataset Generator

Newsletter 파일들을 파싱하여 JSON 형식의 데이터셋을 생성하는 Python 스크립트입니다.

## 기능

- **git log 기반 파일 검색**: 최근에 merge된 newsletter 파일을 자동으로 찾기
- `_newsletters` 디렉토리의 마크다운 파일을 자동으로 파싱
- HTML 콘텐츠에서 포스트 정보 추출 (제목, URL, 이미지, 날짜)
- JSON 형식으로 데이터셋 생성
- 포스트 개수 제한 옵션 제공

## 사용법

### 기본 사용 (git log 기반)

```bash
python3 create_dataset.py
```

기본적으로 `git log`를 사용하여 최근에 추가된 newsletter 파일들을 찾아서 파싱하고 `newsletter_dataset.json` 파일을 생성합니다.

### 옵션

```bash
# 최신 6개 포스트만 추출
python3 create_dataset.py -l 6

# 2024-10-01 이후 추가된 파일만
python3 create_dataset.py -s 2024-10-01

# git 사용하지 않고 디렉토리 전체 파일 사용
python3 create_dataset.py --no-git

# 커스텀 디렉토리/출력 파일
python3 create_dataset.py -d ./posts -o output.json

# 도움말 보기
python3 create_dataset.py --help
```

#### 사용 가능한 옵션

- `-d, --dir DIR`: Newsletter 디렉토리 경로 (기본값: `_newsletters`)
- `-o, --output OUTPUT`: 출력 JSON 파일명 (기본값: `newsletter_dataset.json`)
- `-l, --limit LIMIT`: 포함할 최대 포스트 수
- `-s, --since DATE`: git log 사용시 이 날짜 이후의 파일만 (기본값: `2024-01-01`)
- `--no-git`: git log 사용하지 않고 디렉토리의 모든 파일 처리

## 출력 형식

```json
[
  {
    "file": "_newsletters/2025-10-21-blog-sample.md",
    "image": "/assets/images/default-newsletter.png",
    "title": "Update resources.md",
    "date": "2025-10-06T09:08:54Z",
    "url": "https://github.com/jekyll/jekyll/pull/9880",
    "newsletter_type": "blog"
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

## 예제

### 최근 6개 포스트 추출 (git log 사용)

```bash
python3 create_dataset.py -l 6
```

출력:
```
📂 git log에서 최근 추가된 newsletter 파일 검색 중... (since: 2024-01-01)
   발견된 파일: 2개

파싱 중: 2025-10-21-blog-sample.md (추가일: 2025-10-21)
  → 8개 포스트 발견
파싱 중: 2025-10-21-mosaic-sample.md (추가일: 2025-10-21)
  → 8개 포스트 발견

✅ 총 6개의 포스트를 newsletter_dataset.json에 저장했습니다.
```

### 특정 날짜 이후 파일만

```bash
python3 create_dataset.py -s 2024-10-01 -l 6
```

### 다른 디렉토리에서 데이터셋 생성

```bash
python3 create_dataset.py -d ./my_newsletters -o my_dataset.json --no-git
```

## 요구사항

- Python 3.6 이상
- 표준 라이브러리만 사용 (추가 설치 불필요)

## 라이센스

MIT
