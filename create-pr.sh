#!/bin/bash
# Script to create PR and cleanup branches for Arrakis

echo "============================================"
echo "🚀 Arrakis Repository Cleanup & PR Creation"
echo "============================================"
echo ""

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "⚠️  GitHub CLI (gh) not found. Using web URL instead."
    echo ""
    echo "📝 Create PR by visiting this URL:"
    echo "https://github.com/codeshark2/arrakis/compare/main...claude/review-repo-quality-01Y3FK62mq2Ha3MRaqJMit2q"
    echo ""
    echo "Title: feat: Production-ready repository with CI/CD, testing, and security enhancements"
    echo ""
    echo "Description: See PR_DESCRIPTION.md in the repository"
    echo ""
else
    echo "📝 Creating Pull Request..."
    gh pr create \
        --title "feat: Production-ready repository with CI/CD, testing, and security enhancements" \
        --body-file PR_DESCRIPTION.md \
        --base main \
        --head claude/review-repo-quality-01Y3FK62mq2Ha3MRaqJMit2q

    if [ $? -eq 0 ]; then
        echo "✅ Pull Request created successfully!"
    else
        echo "⚠️  PR creation failed. Please create manually:"
        echo "https://github.com/codeshark2/arrakis/compare/main...claude/review-repo-quality-01Y3FK62mq2Ha3MRaqJMit2q"
    fi
fi

echo ""
echo "============================================"
echo "⏳ After the PR is merged, run this cleanup:"
echo "============================================"
echo ""
echo "bash cleanup-branches.sh"
