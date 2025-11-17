#!/bin/bash
# Cleanup script - Run AFTER PR is merged to main

echo "============================================"
echo "🧹 Cleaning up Arrakis branches"
echo "============================================"
echo ""

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"
echo ""

# Switch to main
echo "1️⃣  Switching to main branch..."
git checkout main
if [ $? -ne 0 ]; then
    echo "❌ Failed to switch to main. Aborting."
    exit 1
fi
echo "✅ Switched to main"
echo ""

# Pull latest changes
echo "2️⃣  Pulling latest changes from main..."
git pull origin main
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Failed to pull from main"
fi
echo "✅ Main branch updated"
echo ""

# Show current status
echo "3️⃣  Current branches:"
git branch -a
echo ""

# Delete local Claude branches
echo "4️⃣  Deleting local Claude branches..."
for branch in $(git branch | grep "claude/"); do
    echo "   Deleting local: $branch"
    git branch -D "$branch" 2>/dev/null && echo "   ✅ Deleted" || echo "   ℹ️  Already gone"
done
echo ""

# Delete remote Claude branches
echo "5️⃣  Deleting remote Claude branches..."
for branch in $(git branch -r | grep "origin/claude/" | sed 's|origin/||'); do
    echo "   Deleting remote: $branch"
    git push origin --delete "$branch" 2>/dev/null && echo "   ✅ Deleted" || echo "   ℹ️  Already gone"
done
echo ""

# Final verification
echo "6️⃣  Final branch status:"
git branch -a
echo ""

# Count remaining branches
BRANCH_COUNT=$(git branch -r | grep -v "HEAD" | wc -l)
if [ $BRANCH_COUNT -eq 0 ]; then
    echo "✅ Perfect! Only main branch remains."
else
    echo "ℹ️  Remaining remote branches: $BRANCH_COUNT"
    echo "   (This is normal if main exists on remote)"
fi

echo ""
echo "============================================"
echo "✅ Cleanup complete!"
echo "============================================"
