#!/usr/bin/env python3
"""
Jekyll Newsletter Generator
GitHub 저장소의 최신 포스트를 가져와 뉴스레터 MD 파일을 생성합니다.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import requests


class Post:
    """블로그 포스트를 나타내는 클래스"""
    
    def __init__(self, title: str, link: str, image: str, date: str, 
                 is_internal: bool = False, description: str = ""):
        self.title = title
        self.link = link
        self.image = image
        self.date = date
        self.is_internal = is_internal
        self.description = description
    
    @classmethod
    def from_github_issue(cls, issue: Dict, repo_url: str, is_internal: bool = False):
        """GitHub Issue로부터 Post 객체 생성"""
        title = issue.get('title', 'No Title')
        issue_number = issue.get('number')
        link = f"{repo_url}/issues/{issue_number}" if is_internal else issue.get('html_url')
        
        # 이미지 추출 (본문에서 첫 번째 이미지 찾기)
        body = issue.get('body', '')
        image = extract_first_image(body)
        
        date = issue.get('created_at', '')
        description = body[:200] if body else ""
        
        return cls(title, link, image, date, is_internal, description)


def extract_first_image(markdown_text: str) -> str:
    """마크다운 텍스트에서 첫 번째 이미지 URL 추출"""
    import re
    # ![alt](url) 형식
    match = re.search(r'!\[.*?\]\((.*?)\)', markdown_text)
    if match:
        return match.group(1)
    
    # <img src="url"> 형식
    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', markdown_text)
    if match:
        return match.group(1)
    
    return "/assets/images/default-newsletter.png"


def fetch_github_posts(repo_owner: str, repo_name: str, token: Optional[str] = None,
                       count: int = 12, is_internal: bool = False) -> List[Post]:
    """GitHub 저장소에서 최신 포스트(Issues) 가져오기"""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
    headers = {}
    
    if token:
        headers['Authorization'] = f'token {token}'
    
    params = {
        'state': 'open',
        'sort': 'created',
        'direction': 'desc',
        'per_page': count
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        issues = response.json()
        
        repo_url = f"https://github.com/{repo_owner}/{repo_name}"
        posts = [Post.from_github_issue(issue, repo_url, is_internal) for issue in issues]
        return posts
    except Exception as e:
        print(f"Error fetching posts: {e}", file=sys.stderr)
        return []


def generate_wide_section(post: Post, include_matomo: bool = False) -> str:
    """Wide 섹션 HTML 생성"""
    matomo_params = ""
    if include_matomo:
        matomo_params = '?mtm_campaign=newsletter&mtm_source=mosaic'
    
    html = f'''
<div class="wide-section">
    <div class="featured-post">
        <a href="{post.link}{matomo_params}">
            <img src="{post.image}" alt="{post.title}">
        </a>
        <div class="post-content">
            <h2><a href="{post.link}{matomo_params}">{post.title}</a></h2>
            <p class="post-date">{post.date}</p>
            {f'<p class="post-description">{post.description}</p>' if post.description else ''}
        </div>
    </div>
</div>
'''
    return html


def generate_grid_section(posts: List[Post], include_matomo: bool = False) -> str:
    """Grid 섹션 HTML 생성 (2x2 그리드)"""
    matomo_params = ""
    if include_matomo:
        matomo_params = '?mtm_campaign=newsletter&mtm_source=mosaic'
    
    html = '<div class="grid-section">\n'
    
    for post in posts:
        html += f'''    <div class="grid-item">
        <a href="{post.link}{matomo_params}">
            <img src="{post.image}" alt="{post.title}">
        </a>
        <h3><a href="{post.link}{matomo_params}">{post.title}</a></h3>
        <p class="post-date">{post.date}</p>
    </div>
'''
    
    html += '</div>\n'
    return html


def generate_newsletter_md(posts: List[Post], newsletter_type: str = 'blog',
                          title: str = "Newsletter", date: str = None) -> str:
    """뉴스레터 MD 파일 생성"""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    include_matomo = (newsletter_type == 'mosaic')
    
    # Front matter
    md_content = f'''---
layout: newsletter
title: "{title}"
date: {date}
type: {newsletter_type}
---

'''
    
    # 포스트 분배
    # - 첫 번째 포스트: featured (wide section)
    # - 다음 8개: 4개씩 2개의 grid section
    # - 나머지: 추가 wide section
    
    if not posts:
        return md_content + "<p>No posts available.</p>"
    
    # Header와 첫 번째 featured post
    md_content += '<div class="newsletter-header">\n'
    md_content += f'    <h1>{title}</h1>\n'
    md_content += f'    <p class="newsletter-date">{date}</p>\n'
    md_content += '</div>\n\n'
    
    # Featured post (첫 번째)
    if posts:
        md_content += generate_wide_section(posts[0], include_matomo)
        md_content += '\n'
    
    # Grid sections (다음 8개를 4개씩)
    grid_posts = posts[1:9]
    if len(grid_posts) > 0:
        # 첫 번째 그리드 (4개)
        first_grid = grid_posts[:4]
        if first_grid:
            md_content += generate_grid_section(first_grid, include_matomo)
            md_content += '\n'
        
        # 두 번째 그리드 (4개)
        second_grid = grid_posts[4:8]
        if second_grid:
            md_content += generate_grid_section(second_grid, include_matomo)
            md_content += '\n'
    
    # 나머지 포스트는 wide section으로
    remaining_posts = posts[9:]
    for post in remaining_posts:
        md_content += generate_wide_section(post, include_matomo)
        md_content += '\n'
    
    return md_content


def main():
    parser = argparse.ArgumentParser(description='Generate Jekyll newsletter from GitHub posts')
    parser.add_argument('--repo', required=True, help='GitHub repository (owner/name)')
    parser.add_argument('--type', choices=['blog', 'mosaic'], default='blog',
                       help='Newsletter type (blog or mosaic)')
    parser.add_argument('--token', help='GitHub API token')
    parser.add_argument('--output', help='Output MD file path')
    parser.add_argument('--title', default='Newsletter', help='Newsletter title')
    parser.add_argument('--count', type=int, default=12, help='Number of posts to fetch')
    parser.add_argument('--internal', action='store_true', 
                       help='Use internal repository links (for blog type)')
    
    args = parser.parse_args()
    
    # Parse repo
    repo_parts = args.repo.split('/')
    if len(repo_parts) != 2:
        print("Error: --repo must be in format 'owner/name'", file=sys.stderr)
        sys.exit(1)
    
    repo_owner, repo_name = repo_parts
    
    # Fetch posts
    print(f"Fetching posts from {args.repo}...")
    is_internal = args.internal and args.type == 'blog'
    posts = fetch_github_posts(repo_owner, repo_name, args.token, args.count, is_internal)
    
    if not posts:
        print("No posts found!", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(posts)} posts")
    
    # Generate newsletter
    newsletter_content = generate_newsletter_md(posts, args.type, args.title)
    
    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(newsletter_content, encoding='utf-8')
        print(f"Newsletter saved to: {output_path}")
    else:
        print(newsletter_content)


if __name__ == '__main__':
    main()
