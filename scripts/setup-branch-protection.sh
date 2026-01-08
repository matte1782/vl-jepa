#!/bin/bash
# Setup GitHub Branch Protection Rules
# Run this once after repository creation
#
# Prerequisites:
#   - GitHub CLI installed: https://cli.github.com/
#   - Authenticated: gh auth login
#
# Usage: ./scripts/setup-branch-protection.sh

set -e

REPO="matte1782/lecture-mind"
BRANCH="master"

echo "🔒 Setting up branch protection for $REPO ($BRANCH branch)..."

# Create branch protection ruleset via GitHub API
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/$REPO/branches/$BRANCH/protection \
  -f required_status_checks='{"strict":true,"contexts":["Lint & Format","Type Check","Test (Python 3.10)","Test (Python 3.11)","Test (Python 3.12)","Smoke Test","Build Package"]}' \
  -F enforce_admins=true \
  -f required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":false,"required_approving_review_count":1}' \
  -f restrictions=null \
  -F allow_force_pushes=false \
  -F allow_deletions=false \
  -F block_creations=false \
  -F required_conversation_resolution=true

echo "✅ Branch protection enabled!"
echo ""
echo "Protected settings:"
echo "  - Force pushes: BLOCKED"
echo "  - Branch deletion: BLOCKED"
echo "  - Direct pushes: BLOCKED (PR required)"
echo "  - Required approvals: 1"
echo "  - Stale approval dismissal: ENABLED"
echo "  - Status checks required: ALL CI jobs"
echo "  - Up-to-date branch required: YES"
echo ""
echo "🎉 Repository is now secure!"
