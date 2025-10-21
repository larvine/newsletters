# Newsletter Dataset Generator

Newsletter 파일들을 파싱하여 JSON 형식의 데이터셋을 생성하는 Python 스크립트입니다.

## 기능

- `_newsletters` 디렉토리의 마크다운 파일을 자동으로 파싱
- HTML 콘텐츠에서 포스트 정보 추출 (제목, URL, 이미지, 날짜)
- JSON 형식으로 데이터셋 생성
- 포스트 개수 제한 옵션 제공

## 사용법

### 기본 사용

```bash
python3 create_dataset.py
```

기본적으로 `_newsletters` 디렉토리의 모든 파일을 파싱하여 `newsletter_dataset.json` 파일을 생성합니다.

### 옵션

```bash
python3 create_dataset.py -l 6  # 최신 6개 포스트만 추출
python3 create_dataset.py -d ./posts -o output.json  # 커스텀 디렉토리/출력 파일
python3 create_dataset.py --help  # 도움말 보기
```

#### 사용 가능한 옵션

- `-d, --dir DIR`: Newsletter 디렉토리 경로 (기본값: `_newsletters`)
- `-o, --output OUTPUT`: 출력 JSON 파일명 (기본값: `newsletter_dataset.json`)
- `-l, --limit LIMIT`: 포함할 최대 포스트 수

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

### 최근 6개 포스트 추출

```bash
python3 create_dataset.py -l 6
```

### 다른 디렉토리에서 데이터셋 생성

```bash
python3 create_dataset.py -d ./my_newsletters -o my_dataset.json
```

## 요구사항

- Python 3.6 이상
- 표준 라이브러리만 사용 (추가 설치 불필요)

## 라이센스

MIT
