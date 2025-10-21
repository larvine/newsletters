#!/bin/bash
# Newsletter 데이터셋 생성 자동화 스크립트
# git log로 최근 파일을 찾아 레이아웃이 할당된 데이터셋을 생성합니다.

set -e

# 기본값
LIMIT=6
GRID_SIZE=4
SINCE="2024-10-01"
OUTPUT_FILE="newsletter_dataset.json"

# 도움말
show_help() {
    cat << EOF
사용법: $0 [OPTIONS]

git log로 최근 추가된 newsletter 파일을 찾아 레이아웃이 할당된 데이터셋을 생성합니다.

OPTIONS:
    -l, --limit NUM         포함할 최대 포스트 수 (기본값: 6)
    -g, --grid-size NUM     Grid 영역에 배치할 포스트 개수 (기본값: 4)
    -s, --since DATE        이 날짜 이후의 파일만 (기본값: 2024-10-01)
    -o, --output FILE       출력 파일명 (기본값: newsletter_dataset.json)
    -h, --help              이 도움말 표시

예제:
    # 기본 사용 (6개 포스트, 4개씩 grid)
    $0

    # 커스텀 설정
    $0 -l 8 -g 6 -o weekly_dataset.json

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
        -o|--output)
            OUTPUT_FILE="$2"
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

echo "🚀 Newsletter 데이터셋 생성 시작..."
echo ""

# 데이터셋 생성 (레이아웃 타입 포함)
python3 create_dataset.py \
    -l "$LIMIT" \
    -s "$SINCE" \
    -g "$GRID_SIZE" \
    -o "$OUTPUT_FILE" \
    --assign-layout

echo ""
echo "✅ 완료!"
echo "   생성된 파일: $OUTPUT_FILE"
echo ""
echo "💡 데이터셋 구조:"
echo "   - 각 포스트에 'layout' 필드 추가 (wide 또는 grid)"
echo "   - Wide: Featured 영역에 표시"
echo "   - Grid: Grid 영역에 표시 (${GRID_SIZE}개씩)"
echo ""
echo "💡 다음 단계:"
echo "   1. 데이터셋 확인: cat $OUTPUT_FILE"
echo "   2. 템플릿에서 사용: {% for post in posts %} ... {% endfor %}"
