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
    """YAML front matter 파싱"""
    front_matter = {}
    
    # --- 사이의 내용 추출
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return front_matter
    
    yaml_content = match.group(1)
    
    # 간단한 key: value 파싱
    for line in yaml_content.split('\n'):
        line = line.strip()
        if not line or not ':' in line:
            continue
        
        # 첫 번째 : 를 기준으로 분리
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        
        if value:  # 값이 있을 때만 저장
            front_matter[key] = value
    
    return front_matter


def parse_newsletter_file(file_path: Path) -> List[Dict]:
    """Newsletter 파일의 front matter를 파싱하여 데이터 반환"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Front matter 파싱
    front_matter = parse_front_matter(content)
    
    # Front matter 변수들을 그대로 JSON 데이터로 변환
    data = {
        'file': str(file_path),
    }
    
    # Front matter의 모든 변수를 데이터에 포함
    for key, value in front_matter.items():
        data[key] = value
    
    # 단일 항목을 리스트로 반환 (newsletter 파일 하나 = 하나의 데이터)
    return [data]


def create_dataset(newsletters_dir: str = '_newsletters', 
                   output_file: str = 'newsletter_dataset.json',
                   limit: int = None,
                   use_git: bool = True,
                   since: str = "2024-01-01") -> List[Dict]:
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
    
    # JSON 파일로 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 총 {len(all_posts)}개의 newsletter를 {output_file}에 저장했습니다.")
    
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
    
    args = parser.parse_args()
    
    create_dataset(
        newsletters_dir=args.dir,
        output_file=args.output,
        limit=args.limit,
        use_git=not args.no_git,
        since=args.since
    )
