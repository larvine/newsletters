#!/usr/bin/env python3
"""
Newsletter Generator

JSON 데이터셋을 기반으로 newsletter 마크다운 파일을 생성합니다.
기본적으로 4개씩 grid 영역에 배치하고, 나머지는 wide 영역에 배치합니다.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict


def create_newsletter_header(title: str, date: str, newsletter_type: str = "blog") -> str:
    """Newsletter 헤더 생성"""
    return f"""---
layout: newsletter
title: "{title}"
date: {date}
type: {newsletter_type}
---

<div class="newsletter-header">
    <h1>{title}</h1>
    <p class="newsletter-date">{date}</p>
</div>

"""


def create_wide_section(post: Dict) -> str:
    """Wide section (featured post) HTML 생성"""
    return f"""
<div class="wide-section">
    <div class="featured-post">
        <a href="{post['url']}">
            <img src="{post['image']}" alt="{post['title']}">
        </a>
        <div class="post-content">
            <h2><a href="{post['url']}">{post['title']}</a></h2>
            <p class="post-date">{post['date']}</p>
        </div>
    </div>
</div>
"""


def create_grid_section(posts: List[Dict]) -> str:
    """Grid section HTML 생성 (최대 4개)"""
    if not posts:
        return ""
    
    html = '\n<div class="grid-section">\n'
    
    for post in posts[:4]:  # 최대 4개만
        html += f"""    <div class="grid-item">
        <a href="{post['url']}">
            <img src="{post['image']}" alt="{post['title']}">
        </a>
        <h3><a href="{post['url']}">{post['title']}</a></h3>
        <p class="post-date">{post['date']}</p>
    </div>
"""
    
    html += '</div>\n'
    return html


def generate_newsletter(posts: List[Dict], 
                       output_file: str,
                       title: str = None,
                       newsletter_type: str = "blog",
                       grid_size: int = 4) -> str:
    """
    JSON 데이터셋에서 newsletter 파일 생성
    
    Args:
        posts: 포스트 리스트
        output_file: 출력 파일명
        title: Newsletter 제목 (None이면 자동 생성)
        newsletter_type: Newsletter 타입 (blog, mosaic 등)
        grid_size: Grid 영역에 배치할 포스트 개수 (기본: 4)
    
    Returns:
        생성된 파일 경로
    """
    if not posts:
        print("❌ 포스트가 없습니다.")
        return None
    
    # 제목 자동 생성
    if not title:
        today = datetime.now().strftime("%Y-%m-%d")
        title = f"Newsletter {today}"
    
    # 날짜 자동 생성
    date = datetime.now().strftime("%Y-%m-%d")
    
    # 헤더 생성
    content = create_newsletter_header(title, date, newsletter_type)
    
    # 포스트를 grid_size 단위로 분할
    remaining_posts = posts.copy()
    
    while remaining_posts:
        # 첫 번째 포스트를 wide section으로
        if len(remaining_posts) > grid_size:
            # 충분히 많은 경우, 하나를 wide로
            wide_post = remaining_posts.pop(0)
            content += create_wide_section(wide_post)
            
            # 다음 grid_size개를 grid section으로
            grid_posts = remaining_posts[:grid_size]
            remaining_posts = remaining_posts[grid_size:]
            content += create_grid_section(grid_posts)
        else:
            # 남은 포스트가 grid_size 이하인 경우
            # 첫 번째를 wide로 (최소 2개 이상인 경우)
            if len(remaining_posts) >= 2:
                wide_post = remaining_posts.pop(0)
                content += create_wide_section(wide_post)
            
            # 나머지를 grid로
            if remaining_posts:
                content += create_grid_section(remaining_posts)
            
            remaining_posts = []
    
    # 파일 저장
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Newsletter 파일 생성: {output_file}")
    print(f"   - 총 {len(posts)}개 포스트")
    print(f"   - 제목: {title}")
    print(f"   - 타입: {newsletter_type}")
    
    return str(output_path)


def load_dataset(json_file: str) -> List[Dict]:
    """JSON 데이터셋 로드"""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='JSON 데이터셋에서 newsletter 마크다운 파일을 생성합니다.',
        epilog="""
예제:
  # 기본 사용
  python3 generate_newsletter.py newsletter_dataset.json
  
  # 커스텀 출력 파일과 제목
  python3 generate_newsletter.py dataset.json -o _newsletters/2025-10-21-weekly.md -t "Weekly Update"
  
  # Grid 크기 변경 (기본 4개)
  python3 generate_newsletter.py dataset.json -g 6
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('input', help='입력 JSON 데이터셋 파일')
    parser.add_argument('-o', '--output', 
                       help='출력 파일명 (기본값: _newsletters/YYYY-MM-DD-newsletter.md)')
    parser.add_argument('-t', '--title',
                       help='Newsletter 제목 (기본값: 자동 생성)')
    parser.add_argument('--type', default='blog',
                       choices=['blog', 'mosaic'],
                       help='Newsletter 타입 (기본값: blog)')
    parser.add_argument('-g', '--grid-size', type=int, default=4,
                       help='Grid 영역에 배치할 포스트 개수 (기본값: 4)')
    parser.add_argument('-l', '--limit', type=int,
                       help='사용할 최대 포스트 수')
    
    args = parser.parse_args()
    
    # 데이터셋 로드
    posts = load_dataset(args.input)
    
    # limit 적용
    if args.limit:
        posts = posts[:args.limit]
    
    # 출력 파일명 자동 생성
    if not args.output:
        today = datetime.now().strftime("%Y-%m-%d")
        args.output = f"_newsletters/{today}-newsletter.md"
    
    # Newsletter 생성
    generate_newsletter(
        posts=posts,
        output_file=args.output,
        title=args.title,
        newsletter_type=args.type,
        grid_size=args.grid_size
    )
