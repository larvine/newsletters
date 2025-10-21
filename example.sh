#!/bin/bash
# 예제 뉴스레터 생성 스크립트

# 블로그용 뉴스레터 생성 예제
echo "Generating blog newsletter..."
python3 generate_newsletter.py \
  --repo jekyll/jekyll \
  --type blog \
  --title "Jekyll Weekly Newsletter" \
  --count 12 \
  --output _newsletters/2025-10-21-blog-example.md

# 모자이크용 뉴스레터 생성 예제
echo "Generating mosaic newsletter..."
python3 generate_newsletter.py \
  --repo github/docs \
  --type mosaic \
  --title "GitHub Updates" \
  --count 12 \
  --output _newsletters/2025-10-21-mosaic-example.md

echo "Done! Check _newsletters/ directory for generated files."
echo "Run 'jekyll serve' to preview the newsletters."
