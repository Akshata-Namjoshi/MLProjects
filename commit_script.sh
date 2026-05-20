#!/bin/bash
cd "d:\ML_Projects.worktrees\agents-streamlit-output-issue-debugging"
echo "=== 1. Check git status ==="
git status --short
echo ""
echo "=== 2. Stage all changes ==="
git add -A
echo "Staged."
echo ""
echo "=== 3. Check recent commits ==="
git log --oneline -5
echo ""
echo "=== 4. Commit with message ==="
git commit -m "Phase 2: Add Docker containerization and fix imports" -m "- Add Dockerfile for Python 3.11 container with Streamlit
- Add docker-compose.yml for local development and testing
- Add .dockerignore to exclude unnecessary files
- Fix app.py to use absolute imports (from app.ui) instead of relative imports
- Remove obsolete version field from docker-compose.yml"
echo ""
echo "=== 5. Confirm commit ==="
echo "Latest commit:"
git log --oneline -1
echo ""
echo "Final status:"
git status --short
