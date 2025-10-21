#!/usr/bin/env python3
"""
GitHub Posts Fetcher

GitHub API를 사용하여 저장소의 최근 이슈와 PR을 가져와서 JSON 데이터셋을 생성합니다.
"""

import json
import urllib.request
import urllib.error
from typing import List, Dict, Optional
from datetime import datetime


def fetch_github_data(owner: str, repo: str, endpoint: str, 
                     since: Optional[str] = None, 
                     limit: int = 10,
                     token: Optional[str] = None) -> List[Dict]:
    """
    GitHub API를 사용하여 데이터 가져오기
    
    Args:
        owner: 저장소 소유자
        repo: 저장소 이름
        endpoint: API 엔드포인트 (issues, pulls 등)
        since: 이 날짜 이후의 항목만 가져오기 (ISO 8601 형식)
        limit: 가져올 최대 항목 수
        token: GitHub Personal Access Token (선택사항, rate limit 증가)
    
    Returns:
        GitHub API 응답 데이터
    """
    # API URL 구성
    url = f"https://api.github.com/repos/{owner}/{repo}/{endpoint}"
    params = []
    
    if since:
        params.append(f"since={since}")
    
    params.append(f"per_page={min(limit, 100)}")
    params.append("state=all")
    params.append("sort=updated")
    params.append("direction=desc")
    
    if params:
        url += "?" + "&".join(params)
    
    # 요청 헤더 설정
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Newsletter-Dataset-Generator'
    }
    
    if token:
        headers['Authorization'] = f'token {token}'
    
    # API 요청
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data[:limit]
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP 에러: {e.code} - {e.reason}")
        if e.code == 403:
            print("   Rate limit에 도달했을 수 있습니다. GitHub token을 사용해보세요.")
        return []
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return []


def extract_image_from_body(body: str) -> Optional[str]:
    """본문에서 첫 번째 이미지 URL 추출"""
    if not body:
        return None
    
    # Markdown 이미지 형식: ![alt](url)
    import re
    md_pattern = r'!\[.*?\]\((https?://[^\)]+)\)'
    match = re.search(md_pattern, body)
    if match:
        return match.group(1)
    
    # HTML 이미지 형식: <img src="url">
    html_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
    match = re.search(html_pattern, body)
    if match:
        return match.group(1)
    
    return None


def create_dataset_from_github(owner: str, repo: str, 
                               limit: int = 6,
                               include_issues: bool = True,
                               include_pulls: bool = True,
                               since: Optional[str] = None,
                               token: Optional[str] = None,
                               output_file: str = 'github_dataset.json') -> List[Dict]:
    """
    GitHub 저장소에서 최근 이슈/PR을 가져와 데이터셋 생성
    
    Args:
        owner: 저장소 소유자
        repo: 저장소 이름
        limit: 가져올 최대 포스트 수
        include_issues: 이슈 포함 여부
        include_pulls: PR 포함 여부
        since: 이 날짜 이후의 항목만 (예: "2024-10-01T00:00:00Z")
        token: GitHub Personal Access Token
        output_file: 출력 JSON 파일명
    
    Returns:
        생성된 데이터셋
    """
    all_posts = []
    
    print(f"📥 GitHub에서 데이터 가져오는 중: {owner}/{repo}")
    
    # 이슈와 PR을 모두 가져오기 위해 issues 엔드포인트 사용
    # (GitHub API에서 PR도 이슈의 일종으로 취급됨)
    if include_issues or include_pulls:
        items = fetch_github_data(owner, repo, "issues", since, limit * 2, token)
        
        for item in items:
            # PR 필터링
            is_pull_request = 'pull_request' in item
            
            if is_pull_request and not include_pulls:
                continue
            if not is_pull_request and not include_issues:
                continue
            
            # 이미지 추출
            image = extract_image_from_body(item.get('body', ''))
            if not image:
                image = "/assets/images/default-newsletter.png"
            
            post = {
                'title': item['title'],
                'url': item['html_url'],
                'image': image,
                'date': item['created_at'],
                'type': 'pull_request' if is_pull_request else 'issue',
                'state': item['state'],
                'author': item['user']['login'],
                'repository': f"{owner}/{repo}"
            }
            
            all_posts.append(post)
            
            if len(all_posts) >= limit:
                break
    
    # 데이터셋을 날짜순으로 정렬 (최신순)
    all_posts.sort(key=lambda x: x['date'], reverse=True)
    all_posts = all_posts[:limit]
    
    # JSON 파일로 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 총 {len(all_posts)}개의 포스트를 {output_file}에 저장했습니다.")
    print(f"\n📊 통계:")
    issues_count = sum(1 for p in all_posts if p['type'] == 'issue')
    pulls_count = sum(1 for p in all_posts if p['type'] == 'pull_request')
    print(f"   - 이슈: {issues_count}개")
    print(f"   - PR: {pulls_count}개")
    
    return all_posts


if __name__ == '__main__':
    import argparse
    import os
    
    parser = argparse.ArgumentParser(
        description='GitHub API를 사용하여 저장소의 최근 이슈/PR을 가져와 JSON 데이터셋을 생성합니다.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  # Jekyll 저장소에서 최근 6개 포스트 가져오기
  python3 fetch_github_posts.py jekyll jekyll -l 6
  
  # GitHub docs 저장소에서 PR만 가져오기
  python3 fetch_github_posts.py github docs -l 10 --no-issues
  
  # Token 사용 (rate limit 증가)
  python3 fetch_github_posts.py jekyll jekyll -l 6 -t YOUR_TOKEN
  
  # 환경변수로 token 설정
  export GITHUB_TOKEN=your_token_here
  python3 fetch_github_posts.py jekyll jekyll -l 6
        """
    )
    
    parser.add_argument('owner', help='저장소 소유자 (예: jekyll, github)')
    parser.add_argument('repo', help='저장소 이름 (예: jekyll, docs)')
    parser.add_argument('-l', '--limit', type=int, default=6,
                       help='가져올 최대 포스트 수 (기본값: 6)')
    parser.add_argument('-o', '--output', default='github_dataset.json',
                       help='출력 JSON 파일명 (기본값: github_dataset.json)')
    parser.add_argument('--no-issues', action='store_true',
                       help='이슈 제외')
    parser.add_argument('--no-pulls', action='store_true',
                       help='PR 제외')
    parser.add_argument('-s', '--since',
                       help='이 날짜 이후의 항목만 가져오기 (예: 2024-10-01T00:00:00Z)')
    parser.add_argument('-t', '--token',
                       help='GitHub Personal Access Token')
    
    args = parser.parse_args()
    
    # 환경변수에서 token 가져오기
    token = args.token or os.environ.get('GITHUB_TOKEN')
    
    if not token:
        print("⚠️  GitHub token이 없습니다. Rate limit이 제한될 수 있습니다.")
        print("   Token 생성: https://github.com/settings/tokens")
        print("   사용법: -t YOUR_TOKEN 또는 export GITHUB_TOKEN=YOUR_TOKEN\n")
    
    create_dataset_from_github(
        owner=args.owner,
        repo=args.repo,
        limit=args.limit,
        include_issues=not args.no_issues,
        include_pulls=not args.no_pulls,
        since=args.since,
        token=token,
        output_file=args.output
    )
