# Jekyll Newsletter Generator

GitHub 저장소의 최신 포스트를 자동으로 가져와 Jekyll 뉴스레터 MD 파일을 생성하는 도구입니다.

## 기능

- GitHub Issues/Posts를 자동으로 가져와 뉴스레터 생성
- 블로그용과 모자이크 게시판용 두 가지 템플릿 제공
- 모자이크용은 Matomo 추적 링크 자동 추가
- Wide section과 Grid section을 활용한 레이아웃
- 반응형 디자인

## 설치

```bash
# Python 의존성 설치
pip install -r requirements.txt

# Jekyll 설치 (Ruby 필요)
gem install jekyll bundler
```

## 사용법

### 1. 뉴스레터 생성

```bash
# 블로그용 뉴스레터 생성
python generate_newsletter.py \
  --repo owner/repo-name \
  --type blog \
  --title "Weekly Newsletter" \
  --output _newsletters/2025-10-21-weekly.md

# 모자이크용 뉴스레터 생성 (Matomo 포함)
python generate_newsletter.py \
  --repo owner/repo-name \
  --type mosaic \
  --title "Monthly Update" \
  --output _newsletters/2025-10-monthly.md

# Internal repo 링크 사용 (블로그용)
python generate_newsletter.py \
  --repo owner/private-repo \
  --type blog \
  --internal \
  --token YOUR_GITHUB_TOKEN \
  --output _newsletters/2025-10-internal.md
```

### 2. Jekyll 서버 실행

```bash
# 로컬 서버 실행
jekyll serve

# 브라우저에서 확인
# http://localhost:4000/newsletters/
```

### 3. 빌드

```bash
# 정적 사이트 빌드
jekyll build

# 결과물은 _site/ 디렉토리에 생성됩니다
```

## 파라미터 설명

- `--repo`: GitHub 저장소 (owner/name 형식, 필수)
- `--type`: 뉴스레터 타입 (blog 또는 mosaic, 기본값: blog)
- `--token`: GitHub API 토큰 (private repo 접근 시 필요)
- `--output`: 출력 MD 파일 경로
- `--title`: 뉴스레터 제목
- `--count`: 가져올 포스트 수 (기본값: 12)
- `--internal`: Internal repo 링크 사용 (블로그 타입에만 적용)

## 뉴스레터 레이아웃

### Wide Section
- 헤더와 가장 중요한 Featured 포스트 표시
- 큰 이미지와 설명 포함

### Grid Section
- 2x2 그리드 레이아웃
- 최신 포스트 중 8개를 4개씩 배치
- 나머지 포스트는 추가 Wide section으로 표시

## 템플릿 차이

### 블로그용 (Blog)
- Matomo 추적 없음
- Internal/External repo 링크 모두 지원
- 깔끔한 블로그 스타일

### 모자이크용 (Mosaic)
- Matomo 추적 링크 자동 추가 (`?mtm_campaign=newsletter&mtm_source=mosaic`)
- Public repo 링크만 사용
- 게시판 스타일 디자인

## 디렉토리 구조

```
.
├── _config.yml              # Jekyll 설정
├── _layouts/
│   └── newsletter.html      # 뉴스레터 레이아웃
├── _newsletters/            # 생성된 뉴스레터 MD 파일들
├── assets/
│   ├── css/
│   │   └── newsletter.css   # 스타일시트
│   └── images/              # 이미지 파일들
├── generate_newsletter.py   # 뉴스레터 생성 스크립트
└── requirements.txt         # Python 의존성
```

## 예제

```bash
# 예제 1: 공개 저장소의 블로그 뉴스레터
python generate_newsletter.py \
  --repo jekyll/jekyll \
  --type blog \
  --title "Jekyll Weekly Updates" \
  --count 10 \
  --output _newsletters/2025-10-21-jekyll-weekly.md

# 예제 2: 모자이크 게시판용 뉴스레터
python generate_newsletter.py \
  --repo github/opensource \
  --type mosaic \
  --title "Open Source Highlights" \
  --output _newsletters/2025-10-21-opensource.md
```

## 커스터마이징

### CSS 수정
`assets/css/newsletter.css` 파일을 수정하여 디자인 변경

### 레이아웃 수정
`_layouts/newsletter.html` 파일을 수정하여 레이아웃 변경

### Matomo 설정
`_layouts/newsletter.html`의 Matomo 섹션에서 tracker URL과 site ID 수정

## 라이선스

MIT License
