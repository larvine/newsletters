#!/bin/bash
# Newsletter 생성 자동화 스크립트
# git log로 최근 파일을 찾아 데이터셋을 만들고 newsletter를 생성합니다.

set -e

# 기본값
LIMIT=6
GRID_SIZE=4
SINCE="2024-10-01"
TITLE=""
OUTPUT_DIR="_newsletters"
NEWSLETTER_TYPE="blog"

# 도움말
show_help() {
    cat << EOF
사용법: $0 [OPTIONS]

git log로 최근 추가된 newsletter 파일을 찾아 새로운 newsletter를 생성합니다.

OPTIONS:
    -l, --limit NUM         포함할 최대 포스트 수 (기본값: 6)
    -g, --grid-size NUM     Grid 영역에 배치할 포스트 개수 (기본값: 4)
    -s, --since DATE        이 날짜 이후의 파일만 (기본값: 2024-10-01)
    -t, --title TITLE       Newsletter 제목
    -o, --output-dir DIR    출력 디렉토리 (기본값: _newsletters)
    --type TYPE             Newsletter 타입: blog, mosaic (기본값: blog)
    -h, --help              이 도움말 표시

예제:
    # 기본 사용 (6개 포스트, 4개씩 grid)
    $0

    # 커스텀 설정
    $0 -l 8 -g 4 -t "Weekly Update" --type mosaic

    # 특정 날짜 이후
    $0 -s 2024-10-15 -l 10
EOF
}

# 인자 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--limit)
            LIMIT="$2"
            shift 2
            ;;
        -g|--grid-size)
            GRID_SIZE="$2"
            shift 2
            ;;
        -s|--since)
            SINCE="$2"
            shift 2
            ;;
        -t|--title)
            TITLE="$2"
            shift 2
            ;;
        -o|--output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --type)
            NEWSLETTER_TYPE="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "알 수 없는 옵션: $1"
            show_help
            exit 1
            ;;
    esac
done

echo "🚀 Newsletter 생성 시작..."
echo ""

# 1. 데이터셋 생성
echo "📊 Step 1: 데이터셋 생성"
python3 create_dataset.py -l "$LIMIT" -s "$SINCE" -o temp_dataset.json
echo ""

# 2. Newsletter 생성
echo "📝 Step 2: Newsletter 생성"
TODAY=$(date +%Y-%m-%d)
OUTPUT_FILE="${OUTPUT_DIR}/${TODAY}-newsletter.md"

if [ -n "$TITLE" ]; then
    python3 generate_newsletter.py temp_dataset.json \
        -o "$OUTPUT_FILE" \
        --type "$NEWSLETTER_TYPE" \
        -g "$GRID_SIZE" \
        -t "$TITLE"
else
    python3 generate_newsletter.py temp_dataset.json \
        -o "$OUTPUT_FILE" \
        --type "$NEWSLETTER_TYPE" \
        -g "$GRID_SIZE"
fi

echo ""

# 3. 임시 파일 삭제
rm -f temp_dataset.json

echo ""
echo "✅ 완료!"
echo "   생성된 파일: $OUTPUT_FILE"
echo ""
echo "💡 다음 단계:"
echo "   1. 파일 확인: cat $OUTPUT_FILE"
echo "   2. Jekyll 서버 실행: bundle exec jekyll serve"
echo "   3. Git 커밋: git add $OUTPUT_FILE && git commit -m 'Add newsletter'"
