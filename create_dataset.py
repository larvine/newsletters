#!/usr/bin/env python3
"""
Newsletter Dataset Generator

이 스크립트는 git log를 사용하여 최근에 추가된 newsletter 파일들을 찾아서
JSON 데이터셋을 생성합니다.
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime


def get_recent_files_from_git(pattern: str = "*newsletters/*.md", 
                              since: str = "2024-01-01",
                              branch: str = "all") -> List[Tuple[str, str]]:
    """
    git log를 사용하여 최근에 추가된 파일 목록 가져오기
    
    Args:
        pattern: 파일 패턴 (예: "*newsletters/*.md")
        since: 이 날짜 이후의 파일들 (예: "2024-01-01")
        branch: 검색할 브랜치 ("all" 또는 브랜치명)
    
    Returns:
        (파일경로, 추가날짜) 튜플의 리스트
    """
    try:
        # git log로 추가된 파일들과 날짜 가져오기
        branch_arg = "--all" if branch == "all" else branch
        cmd = [
            "git", "log", branch_arg,
            "--diff-filter=A",  # 추가된 파일만
            "--name-only",
            "--pretty=format:%ai|%H",
            f"--since={since}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        files_with_dates = []
        current_date = None
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # 날짜 라인인지 확인
            if '|' in line:
                date_str = line.split('|')[0]
                current_date = date_str
            else:
                # 파일 라인
                # pattern에 맞는 파일만 선택
                pattern_parts = pattern.split('/')
                if all(part in line or part == '*' or part.startswith('*') for part in pattern_parts if part):
                    if line.endswith('.md') and ('newsletter' in line.lower() or 'post' in line.lower()):
                        if current_date and os.path.exists(line):
                            files_with_dates.append((line, current_date))
        
        # 날짜순으로 정렬 (최신순)
        files_with_dates.sort(key=lambda x: x[1], reverse=True)
        
        # 중복 제거 (같은 파일이 여러 번 나올 수 있음)
        seen = set()
        unique_files = []
        for filepath, date in files_with_dates:
            if filepath not in seen:
                seen.add(filepath)
                unique_files.append((filepath, date))
        
        return unique_files
    
    except subprocess.CalledProcessError as e:
        print(f"⚠️  git 명령 실행 실패: {e}")
        return []
    except Exception as e:
        print(f"⚠️  에러: {e}")
        return []


def parse_front_matter(content: str) -> Dict:
    """YAML front matter 파싱 (posts 배열 포함)"""
    front_matter = {}
    
    # --- 사이의 내용 추출
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return front_matter
    
    yaml_content = match.group(1)
    lines = yaml_content.split('\n')
    
    current_key = None
    current_list = []
    current_item = {}
    in_list = False
    
    for line in lines:
        line_stripped = line.strip()
        
        if not line_stripped:
            continue
        
        # 리스트 아이템 시작 (- 로 시작)
        if line_stripped.startswith('- '):
            if current_item:
                current_list.append(current_item)
            current_item = {}
            # - 다음에 key: value가 올 수 있음
            rest = line_stripped[2:].strip()
            if ':' in rest:
                k, v = rest.split(':', 1)
                current_item[k.strip()] = v.strip().strip('"').strip("'")
        # 들여쓰기된 키:값 (리스트 아이템의 속성)
        elif line.startswith('  ') and ':' in line_stripped:
            k, v = line_stripped.split(':', 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            
            # tags 같은 배열 처리
            if v.startswith('[') and v.endswith(']'):
                v = [item.strip().strip('"').strip("'") for item in v[1:-1].split(',') if item.strip()]
            
            current_item[k] = v
        # 일반 키:값
        elif ':' in line_stripped and not line.startswith('  '):
            # 이전 리스트 마무리
            if current_item:
                current_list.append(current_item)
                current_item = {}
            if current_list and current_key:
                front_matter[current_key] = current_list
                current_list = []
            
            k, v = line_stripped.split(':', 1)
            current_key = k.strip()
            v = v.strip().strip('"').strip("'")
            
            # 빈 값이면 리스트 시작일 수 있음
            if not v:
                in_list = True
            else:
                front_matter[current_key] = v
                current_key = None
    
    # 마지막 아이템 처리
    if current_item:
        current_list.append(current_item)
    if current_list and current_key:
        front_matter[current_key] = current_list
    
    return front_matter


def parse_newsletter_file(file_path: Path) -> List[Dict]:
    """Newsletter 파일을 파싱하여 포스트 목록 반환"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Front matter 파싱
    front_matter = parse_front_matter(content)
    
    # Front matter에 posts가 있으면 그걸 사용
    if 'posts' in front_matter and isinstance(front_matter['posts'], list):
        posts = []
        newsletter_type = front_matter.get('type', 'unknown')
        
        for post in front_matter['posts']:
            post_data = {
                'file': str(file_path),
                'title': post.get('title', ''),
                'url': post.get('url', ''),
                'image': post.get('image', ''),
                'date': post.get('date', ''),
                'newsletter_type': newsletter_type,
                'tags': post.get('tags', [])
            }
            posts.append(post_data)
        
        return posts
    
    # Front matter에 posts가 없으면 빈 리스트 반환
    return []


def assign_layout_types(posts: List[Dict], grid_size: int = 4) -> List[Dict]:
    """
    포스트에 레이아웃 타입 할당 (wide 또는 grid)
    
    로직:
    1. 'featured' tag가 있는 포스트는 무조건 'wide'
    2. 나머지는 4개씩 grid에 배치하고, 그 전에 하나씩 wide로 배치
    
    Args:
        posts: 포스트 리스트
        grid_size: Grid에 배치할 포스트 개수 (기본: 4)
    
    Returns:
        레이아웃 타입이 추가된 포스트 리스트
    """
    result = []
    
    # 1단계: featured tag가 있는 포스트를 먼저 처리
    featured_posts = []
    regular_posts = []
    
    for post in posts:
        tags = post.get('tags', [])
        if 'featured' in tags:
            post['layout'] = 'wide'
            featured_posts.append(post)
        else:
            regular_posts.append(post)
    
    # 2단계: featured 포스트를 결과에 추가
    result.extend(featured_posts)
    
    # 3단계: 일반 포스트를 레이아웃에 따라 배치
    remaining = regular_posts.copy()
    
    while remaining:
        # Wide 영역에 1개 배치 (포스트가 grid_size보다 많을 때만)
        if len(remaining) > grid_size:
            post = remaining.pop(0)
            post['layout'] = 'wide'
            result.append(post)
            
            # Grid 영역에 grid_size개 배치
            for _ in range(min(grid_size, len(remaining))):
                post = remaining.pop(0)
                post['layout'] = 'grid'
                result.append(post)
        else:
            # 남은 포스트가 적으면
            if len(remaining) >= 2:
                # 2개 이상이면 첫 번째를 wide로
                post = remaining.pop(0)
                post['layout'] = 'wide'
                result.append(post)
            
            # 나머지는 grid로
            for post in remaining:
                post['layout'] = 'grid'
                result.append(post)
            remaining = []
    
    return result


def create_dataset(newsletters_dir: str = '_newsletters', 
                   output_file: str = 'newsletter_dataset.json',
                   limit: int = None,
                   use_git: bool = True,
                   since: str = "2024-01-01",
                   grid_size: int = 4,
                   assign_layout: bool = False) -> List[Dict]:
    """
    Newsletter 파일들을 파싱하여 JSON 데이터셋 생성
    
    Args:
        newsletters_dir: newsletter 파일들이 있는 디렉토리
        output_file: 출력할 JSON 파일명
        limit: 포함할 최대 포스트 수 (None이면 전체)
        use_git: git log를 사용하여 최근 파일만 가져올지 여부
        since: git log 사용시 이 날짜 이후의 파일만 (예: "2024-01-01")
    
    Returns:
        생성된 데이터셋 (list of dict)
    """
    all_posts = []
    
    if use_git:
        # git log를 사용하여 최근 추가된 파일 찾기
        print(f"📂 git log에서 최근 추가된 newsletter 파일 검색 중... (since: {since})")
        pattern = f"*{newsletters_dir}/*.md"
        files_with_dates = get_recent_files_from_git(pattern, since)
        
        if not files_with_dates:
            print(f"⚠️  최근 추가된 파일을 찾을 수 없습니다. 디렉토리 모드로 전환합니다.")
            use_git = False
        else:
            print(f"   발견된 파일: {len(files_with_dates)}개\n")
            
            for filepath, date in files_with_dates:
                md_file = Path(filepath)
                print(f"파싱 중: {md_file.name} (추가일: {date[:10]})")
                posts = parse_newsletter_file(md_file)
                print(f"  → {len(posts)}개 포스트 발견")
                all_posts.extend(posts)
    
    if not use_git:
        # 디렉토리의 모든 파일 처리
        newsletters_path = Path(newsletters_dir)
        
        if not newsletters_path.exists():
            print(f"디렉토리를 찾을 수 없습니다: {newsletters_dir}")
            return []
        
        print(f"📂 {newsletters_dir} 디렉토리의 모든 파일 처리 중...\n")
        
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
    
    # 레이아웃 타입 할당
    if assign_layout:
        all_posts = assign_layout_types(all_posts, grid_size)
        wide_count = sum(1 for p in all_posts if p.get('layout') == 'wide')
        grid_count = sum(1 for p in all_posts if p.get('layout') == 'grid')
        print(f"\n📐 레이아웃 할당: Wide {wide_count}개, Grid {grid_count}개")
    
    # JSON 파일로 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 총 {len(all_posts)}개의 포스트를 {output_file}에 저장했습니다.")
    
    return all_posts


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Newsletter 파일들을 파싱하여 JSON 데이터셋을 생성합니다.',
        epilog="""
예제:
  # git log로 최근 추가된 파일에서 6개 포스트 생성
  python3 create_dataset.py -l 6
  
  # 2024-10-01 이후 추가된 파일만
  python3 create_dataset.py -s 2024-10-01
  
  # git 사용하지 않고 디렉토리 전체 파일 사용
  python3 create_dataset.py --no-git
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
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
    parser.add_argument(
        '--no-git',
        action='store_true',
        help='git log 사용하지 않고 디렉토리의 모든 파일 처리'
    )
    parser.add_argument(
        '-s', '--since',
        default='2024-01-01',
        help='git log 사용시 이 날짜 이후의 파일만 (기본값: 2024-01-01)'
    )
    parser.add_argument(
        '--assign-layout',
        action='store_true',
        help='각 포스트에 레이아웃 타입(wide/grid) 할당'
    )
    parser.add_argument(
        '-g', '--grid-size',
        type=int,
        default=4,
        help='Grid 영역에 배치할 포스트 개수 (기본값: 4)'
    )
    
    args = parser.parse_args()
    
    create_dataset(
        newsletters_dir=args.dir,
        output_file=args.output,
        limit=args.limit,
        use_git=not args.no_git,
        since=args.since,
        grid_size=args.grid_size,
        assign_layout=args.assign_layout
    )
