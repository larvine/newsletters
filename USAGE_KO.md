# Jekyll Newsletter 사용 가이드 (한국어)

## 개요

이 프로젝트는 GitHub 저장소의 최신 포스트(Issues/PRs)를 자동으로 가져와서 Jekyll 뉴스레터 MD 파일을 생성합니다.

## 주요 기능

### 1. 두 가지 템플릿 타입

#### 블로그용 (`--type blog`)
- Matomo 추적 링크 없음
- Internal/External repo 링크 모두 지원
- `--internal` 플래그로 내부 저장소 링크 사용 가능

#### 모자이크 게시판용 (`--type mosaic`)
- Matomo 추적 링크 자동 추가 (`?mtm_campaign=newsletter&mtm_source=mosaic`)
- Public repo 링크만 사용
- 게시판 스타일 디자인

### 2. 레이아웃 구조

#### Wide Section
- **헤더**: 뉴스레터 제목과 날짜
- **Featured Post**: 첫 번째 포스트를 큰 형태로 표시
  - 큰 이미지 (400px 높이)
  - 제목, 날짜, 설명

#### Grid Section (2x2 그리드)
- 최신 포스트 중 8개를 선택
- 4개씩 2개의 그리드 섹션으로 배치
- 각 아이템: 이미지 (250px 높이) + 제목 + 날짜

#### 추가 Wide Section
- 나머지 포스트들은 Wide section 형태로 추가

## 사용 예제

### 1. 기본 사용법

```bash
# 블로그용 뉴스레터 생성
python3 generate_newsletter.py \
  --repo jekyll/jekyll \
  --type blog \
  --title "Jekyll 주간 뉴스레터" \
  --output _newsletters/2025-10-21-weekly.md

# 모자이크용 뉴스레터 생성
python3 generate_newsletter.py \
  --repo github/docs \
  --type mosaic \
  --title "GitHub 업데이트" \
  --output _newsletters/2025-10-21-updates.md
```

### 2. Internal Repo 사용 (블로그용만)

```bash
python3 generate_newsletter.py \
  --repo myorg/private-blog \
  --type blog \
  --internal \
  --token YOUR_GITHUB_TOKEN \
  --title "내부 블로그 뉴스레터" \
  --output _newsletters/2025-10-21-internal.md
```

### 3. 포스트 개수 조절

```bash
python3 generate_newsletter.py \
  --repo owner/repo \
  --type blog \
  --count 15 \
  --title "확장 뉴스레터" \
  --output _newsletters/2025-10-21-extended.md
```

## 파라미터 설명

| 파라미터 | 필수 | 설명 | 기본값 |
|---------|------|------|--------|
| `--repo` | ✓ | GitHub 저장소 (owner/name 형식) | - |
| `--type` | | 뉴스레터 타입 (blog 또는 mosaic) | blog |
| `--token` | | GitHub API 토큰 (private repo 접근 시) | - |
| `--output` | | 출력 MD 파일 경로 | 표준 출력 |
| `--title` | | 뉴스레터 제목 | Newsletter |
| `--count` | | 가져올 포스트 수 | 12 |
| `--internal` | | Internal repo 링크 사용 (블로그 타입만) | false |

## 포스트 분배 로직

1. **첫 번째 포스트**: Featured post (Wide section)
2. **2-5번째 포스트**: 첫 번째 Grid section (2x2)
3. **6-9번째 포스트**: 두 번째 Grid section (2x2)
4. **10번째 이후**: 추가 Wide section

총 12개 포스트를 가져오면:
- 1개 Featured
- 8개 Grid (4+4)
- 3개 추가 Wide

## 템플릿 차이점

### 블로그용
```html
<!-- 링크 예시 -->
<a href="https://github.com/owner/repo/issues/123">
```

### 모자이크용
```html
<!-- Matomo 파라미터 추가 -->
<a href="https://github.com/owner/repo/issues/123?mtm_campaign=newsletter&mtm_source=mosaic">
```

## Jekyll 설정

### 1. 로컬 미리보기

```bash
# Jekyll 서버 실행
jekyll serve

# 브라우저에서 확인
# http://localhost:4000/newsletters/2025-10-21-blog-sample.html
```

### 2. 빌드

```bash
# 정적 사이트 빌드
jekyll build

# 결과물은 _site/ 디렉토리에 생성
```

## 커스터마이징

### CSS 수정
`assets/css/newsletter.css` 파일을 수정하여 스타일 변경

주요 클래스:
- `.newsletter-header`: 헤더 섹션
- `.wide-section`: Wide 섹션
- `.featured-post`: Featured 포스트
- `.grid-section`: Grid 섹션
- `.grid-item`: Grid 아이템

### 레이아웃 수정
`_layouts/newsletter.html` 파일을 수정하여 레이아웃 변경

### Matomo 설정
`_layouts/newsletter.html`에서 다음 부분 수정:
```javascript
var u="//your-matomo-instance/";  // Matomo 서버 URL
_paq.push(['setSiteId', 'YOUR_SITE_ID']);  // Site ID
```

## 이미지 처리

- GitHub Issues/PRs 본문에서 첫 번째 이미지 자동 추출
- 이미지가 없는 경우 `/assets/images/default-newsletter.png` 사용
- 지원 형식:
  - Markdown: `![alt](url)`
  - HTML: `<img src="url">`

## 문제 해결

### Python 모듈이 없다는 오류
```bash
pip3 install -r requirements.txt
```

### GitHub API Rate Limit
- 토큰 없이 사용: 시간당 60 요청
- 토큰 사용: 시간당 5000 요청
```bash
python3 generate_newsletter.py --token YOUR_TOKEN ...
```

### Jekyll 서버 시작 안됨
```bash
# Jekyll 설치
gem install jekyll bundler

# Gemfile이 있는 경우
bundle install
bundle exec jekyll serve
```

## 자동화

### Cron Job 예시
```bash
# 매주 월요일 오전 9시에 뉴스레터 생성
0 9 * * 1 cd /path/to/workspace && python3 generate_newsletter.py --repo owner/repo --type blog --title "주간 뉴스레터" --output _newsletters/$(date +\%Y-\%m-\%d)-weekly.md
```

### GitHub Actions 예시
`.github/workflows/newsletter.yml`:
```yaml
name: Generate Newsletter
on:
  schedule:
    - cron: '0 9 * * 1'  # 매주 월요일 오전 9시
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - run: pip install -r requirements.txt
      - run: |
          python3 generate_newsletter.py \
            --repo ${{ github.repository }} \
            --type blog \
            --title "주간 뉴스레터" \
            --output _newsletters/$(date +%Y-%m-%d)-weekly.md
      - run: git add _newsletters/
      - run: git commit -m "Add weekly newsletter"
      - run: git push
```

## 라이선스

MIT License
