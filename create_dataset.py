#!/usr/bin/env python3
"""
Newsletter Dataset Generator

이 스크립트는 _newsletters 디렉토리의 마크다운 파일들을 파싱하여
JSON 데이터셋을 생성합니다.
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict


def parse_front_matter(content: str) -> Dict:
    """YAML front matter 파싱"""
    front_matter = {}
    
    # --- 사이의 내용 추출
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        yaml_content = match.group(1)
        for line in yaml_content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                front_matter[key.strip()] = value.strip().strip('"')
    
    return front_matter


def parse_newsletter_file(file_path: Path) -> List[Dict]:
    """Newsletter 파일을 파싱하여 포스트 목록 반환"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Front matter 파싱
    front_matter = parse_front_matter(content)
    newsletter_type = front_matter.get('type', 'unknown')
    
    posts = []
    
    # 정규식으로 포스트 블록 추출
    # grid-item과 featured-post 모두 찾기
    
    # grid-item 패턴
    grid_pattern = r'<div class="grid-item">.*?<a href="([^"]+)">.*?<img src="([^"]+)" alt="([^"]+)">.*?</a>.*?<h3>.*?</h3>.*?<p class="post-date">([^<]+)</p>.*?</div>'
    grid_matches = re.findall(grid_pattern, content, re.DOTALL)
    
    for url, image, title, date in grid_matches:
        posts.append({
            'file': str(file_path),
            'image': image.strip(),
            'title': title.strip(),
            'date': date.strip(),
            'url': url.strip(),
            'newsletter_type': newsletter_type
        })
    
    # featured-post 패턴
    featured_pattern = r'<div class="featured-post">.*?<a href="([^"]+)">.*?<img src="([^"]+)" alt="([^"]+)">.*?</a>.*?<h2>.*?</h2>.*?<p class="post-date">([^<]+)</p>'
    featured_matches = re.findall(featured_pattern, content, re.DOTALL)
    
    for url, image, title, date in featured_matches:
        # featured post를 맨 앞에 추가
        posts.insert(0, {
            'file': str(file_path),
            'image': image.strip(),
            'title': title.strip(),
            'date': date.strip(),
            'url': url.strip(),
            'newsletter_type': newsletter_type
        })
    
    return posts


def create_dataset(newsletters_dir: str = '_newsletters', 
                   output_file: str = 'newsletter_dataset.json',
                   limit: int = None) -> List[Dict]:
    """
    Newsletter 디렉토리의 파일들을 파싱하여 JSON 데이터셋 생성
    
    Args:
        newsletters_dir: newsletter 파일들이 있는 디렉토리
        output_file: 출력할 JSON 파일명
        limit: 포함할 최대 포스트 수 (None이면 전체)
    
    Returns:
        생성된 데이터셋 (list of dict)
    """
    newsletters_path = Path(newsletters_dir)
    
    if not newsletters_path.exists():
        print(f"디렉토리를 찾을 수 없습니다: {newsletters_dir}")
        return []
    
    all_posts = []
    
    # 모든 .md 파일 처리 (최신 파일부터)
    md_files = sorted(newsletters_path.glob('*.md'), reverse=True)
    
    for md_file in md_files:
        print(f"파싱 중: {md_file.name}")
        posts = parse_newsletter_file(md_file)
        print(f"  → {len(posts)}개 포스트 발견")
        all_posts.extend(posts)
    
    # limit이 지정된 경우 제한
    if limit:
        all_posts = all_posts[:limit]
    
    # JSON 파일로 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 총 {len(all_posts)}개의 포스트를 {output_file}에 저장했습니다.")
    
    return all_posts


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Newsletter 파일들을 파싱하여 JSON 데이터셋을 생성합니다.'
    )
    parser.add_argument(
        '-d', '--dir',
        default='_newsletters',
        help='Newsletter 디렉토리 경로 (기본값: _newsletters)'
    )
    parser.add_argument(
        '-o', '--output',
        default='newsletter_dataset.json',
        help='출력 JSON 파일명 (기본값: newsletter_dataset.json)'
    )
    parser.add_argument(
        '-l', '--limit',
        type=int,
        help='포함할 최대 포스트 수'
    )
    
    args = parser.parse_args()
    
    create_dataset(
        newsletters_dir=args.dir,
        output_file=args.output,
        limit=args.limit
    )
