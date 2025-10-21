# Newsletter Dataset Generator

Newsletter 파일들을 파싱하여 JSON 형식의 데이터셋을 생성하고, 데이터셋으로부터 새로운 newsletter를 생성하는 도구 모음입니다.

## 도구 목록

### 1. `create_dataset.py` - 데이터셋 생성
- **git log 기반 파일 검색**: 최근에 merge된 newsletter 파일을 자동으로 찾기
- `_newsletters` 디렉토리의 마크다운 파일을 자동으로 파싱
- HTML 콘텐츠에서 포스트 정보 추출 (제목, URL, 이미지, 날짜)
- JSON 형식으로 데이터셋 생성

### 2. `generate_newsletter.py` - Newsletter 생성
- JSON 데이터셋에서 newsletter 마크다운 파일 생성
- **4개씩 grid 영역에 배치**, 나머지는 wide 영역에 배치
- 자동 레이아웃 구성 (wide + grid sections)

### 3. `create_newsletter_from_git.sh` - 원클릭 자동화
- git log → 데이터셋 → newsletter 생성까지 한번에
- 간편한 쉘 스크립트 인터페이스

## 사용법

### 🚀 빠른 시작 (권장)

한 번에 모든 작업을 수행하는 쉘 스크립트:

```bash
./create_newsletter_from_git.sh
```

### 📝 수동 사용

#### 1. 데이터셋 생성

```bash
# 기본 사용 (git log로 최근 파일 찾기)
python3 create_dataset.py -l 6

# 2024-10-01 이후 추가된 파일만
python3 create_dataset.py -s 2024-10-01

# git 사용하지 않고 디렉토리 전체
python3 create_dataset.py --no-git
```

**옵션:**
- `-l, --limit`: 포함할 최대 포스트 수
- `-s, --since`: git log 사용시 이 날짜 이후의 파일만 (기본: 2024-01-01)
- `-d, --dir`: Newsletter 디렉토리 경로 (기본: _newsletters)
- `-o, --output`: 출력 JSON 파일명 (기본: newsletter_dataset.json)
- `--no-git`: git 사용 안 함

#### 2. Newsletter 생성

```bash
# 데이터셋으로부터 newsletter 생성
python3 generate_newsletter.py newsletter_dataset.json

# 커스텀 옵션
python3 generate_newsletter.py dataset.json \
    -o _newsletters/2025-10-21-weekly.md \
    -t "Weekly Update" \
    --type mosaic \
    -g 4
```

**옵션:**
- `-o, --output`: 출력 파일명
- `-t, --title`: Newsletter 제목
- `--type`: Newsletter 타입 (blog, mosaic)
- `-g, --grid-size`: Grid 영역에 배치할 포스트 개수 (기본: 4)
- `-l, --limit`: 사용할 최대 포스트 수

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

### 예제 1: 기본 워크플로우 (자동화)

```bash
# 원클릭으로 newsletter 생성
./create_newsletter_from_git.sh -l 6 -t "Weekly Update"
```

출력:
```
🚀 Newsletter 생성 시작...

📊 Step 1: 데이터셋 생성
📂 git log에서 최근 추가된 newsletter 파일 검색 중... (since: 2024-10-01)
   발견된 파일: 2개

파싱 중: 2025-10-21-blog-sample.md (추가일: 2025-10-21)
  → 8개 포스트 발견

✅ 총 6개의 포스트를 temp_dataset.json에 저장했습니다.

📝 Step 2: Newsletter 생성
✅ Newsletter 파일 생성: _newsletters/2025-10-21-newsletter.md
   - 총 6개 포스트
   - 제목: Weekly Update
   - 타입: blog

✅ 완료!
   생성된 파일: _newsletters/2025-10-21-newsletter.md
```

**레이아웃 구조 (6개 포스트, grid-size=4):**
- 1번 포스트 → Wide section (featured)
- 2~5번 포스트 → Grid section (4개)
- 6번 포스트 → Grid section (1개)

### 예제 2: 수동 워크플로우

```bash
# 1. 데이터셋 생성
python3 create_dataset.py -l 8 -s 2024-10-01

# 2. Newsletter 생성
python3 generate_newsletter.py newsletter_dataset.json \
    -o _newsletters/2025-10-21-custom.md \
    -t "Custom Newsletter" \
    -g 4
```

### 예제 3: Grid 크기 변경

```bash
# 6개씩 grid에 배치
./create_newsletter_from_git.sh -l 10 -g 6
```

**레이아웃 구조 (10개 포스트, grid-size=6):**
- 1번 포스트 → Wide section
- 2~7번 포스트 → Grid section (6개)
- 8번 포스트 → Wide section
- 9~10번 포스트 → Grid section (2개)

## 요구사항

- Python 3.6 이상
- 표준 라이브러리만 사용 (추가 설치 불필요)

## 라이센스

MIT
