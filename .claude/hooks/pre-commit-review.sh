#!/usr/bin/env bash
# EdgeVec Pre-Commit Review Hook
# Version: 2.0.0
# Purpose: Enforce quality gates at git commit level
#
# This hook prevents commits that bypass the HOSTILE_REVIEWER gate system.
# It complements the runtime enforcement in settings.json by blocking at VCS level.

set -e

# Color codes for terminal output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# EdgeVec gate file locations
GATE_1=".claude/GATE_1_COMPLETE.md"
GATE_2=".claude/GATE_2_COMPLETE.md"
GATE_3=".claude/GATE_3_COMPLETE.md"
GATE_4=".claude/GATE_4_COMPLETE.md"

# Get list of staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

# Exit early if no files staged
if [ -z "$STAGED_FILES" ]; then
  exit 0
fi

# Flag to track gate violations
GATE_VIOLATION=0
VIOLATION_MESSAGES=""

# Function to check gate and record violation
check_gate() {
  local gate_file=$1
  local gate_name=$2
  local paths=$3
  local remediation=$4

  if [ ! -f "$gate_file" ]; then
    GATE_VIOLATION=1
    VIOLATION_MESSAGES="${VIOLATION_MESSAGES}\n"
    VIOLATION_MESSAGES="${VIOLATION_MESSAGES}┌─────────────────────────────────────────────────────────────────────┐\n"
    VIOLATION_MESSAGES="${VIOLATION_MESSAGES}│ ${RED}GATE ${gate_name} NOT PASSED${NC}                                              │\n"
    VIOLATION_MESSAGES="${VIOLATION_MESSAGES}├─────────────────────────────────────────────────────────────────────┤\n"
    VIOLATION_MESSAGES="${VIOLATION_MESSAGES}│ ${YELLOW}Files being committed:${NC}                                             │\n"
    VIOLATION_MESSAGES="${VIOLATION_MESSAGES}│   ${paths}                                                          │\n"
    VIOLATION_MESSAGES="${VIOLATION_MESSAGES}│                                                                     │\n"
    VIOLATION_MESSAGES="${VIOLATION_MESSAGES}│ ${YELLOW}Required:${NC}                                                          │\n"
    VIOLATION_MESSAGES="${VIOLATION_MESSAGES}│   ${gate_file} must exist                                           │\n"
    VIOLATION_MESSAGES="${VIOLATION_MESSAGES}│                                                                     │\n"
    VIOLATION_MESSAGES="${VIOLATION_MESSAGES}│ ${YELLOW}Remediation:${NC}                                                       │\n"
    VIOLATION_MESSAGES="${VIOLATION_MESSAGES}│   ${remediation}                                                    │\n"
    VIOLATION_MESSAGES="${VIOLATION_MESSAGES}└─────────────────────────────────────────────────────────────────────┘\n"
  fi
}

# Check each category of files

# GATE 1: Architecture documents → Planning
echo -e "${BLUE}[EdgeVec Pre-Commit]${NC} Checking GATE 1 (Architecture)..."
ARCH_FILES=$(echo "$STAGED_FILES" | grep -E '^docs/architecture/' || true)
if [ -n "$ARCH_FILES" ]; then
  check_gate "$GATE_1" "1" "$ARCH_FILES" \
    "Run /architect-design and /review ARCHITECTURE.md to pass GATE 1"
fi

# GATE 2: Planning → Implementation
echo -e "${BLUE}[EdgeVec Pre-Commit]${NC} Checking GATE 2 (Planning → Code)..."
SRC_FILES=$(echo "$STAGED_FILES" | grep -E '^src/.*\.rs$' || true)
if [ -n "$SRC_FILES" ]; then
  check_gate "$GATE_2" "2" "$SRC_FILES" \
    "Run /planner-weekly [N] and /review WEEKLY_TASK_PLAN.md to pass GATE 2"
fi

# GATE 2 also applies to Cargo.toml changes
CARGO_FILES=$(echo "$STAGED_FILES" | grep -E '^Cargo\.toml$' || true)
if [ -n "$CARGO_FILES" ]; then
  check_gate "$GATE_2" "2" "$CARGO_FILES" \
    "Cargo.toml changes require approved plan. Run /planner-weekly [N] and /review"
fi

# GATE 3: Implementation → Merge
# (Tests, benchmarks, and finalized code require GATE 3)
echo -e "${BLUE}[EdgeVec Pre-Commit]${NC} Checking GATE 3 (Implementation → Merge)..."
TEST_FILES=$(echo "$STAGED_FILES" | grep -E '^(tests|benches|fuzz)/' || true)
if [ -n "$TEST_FILES" ]; then
  # Tests require at least GATE 2 (code can be written)
  if [ ! -f "$GATE_2" ]; then
    check_gate "$GATE_2" "2" "$TEST_FILES" \
      "Tests require approved plan. Run /planner-weekly [N] and /review"
  fi
fi

# GATE 4: Documentation → Release
# (Final README, CHANGELOG for release)
echo -e "${BLUE}[EdgeVec Pre-Commit]${NC} Checking GATE 4 (Documentation)..."
RELEASE_FILES=$(echo "$STAGED_FILES" | grep -E '^(README\.md|CHANGELOG\.md)$' || true)
if [ -n "$RELEASE_FILES" ]; then
  # README and CHANGELOG in root require GATE 3 (implementation complete)
  if [ ! -f "$GATE_3" ]; then
    check_gate "$GATE_3" "3" "$RELEASE_FILES" \
      "Release docs require implementation approval. Run /review [implementation]"
  fi
fi

# If any gate violations, block commit
if [ $GATE_VIOLATION -eq 1 ]; then
  echo -e "\n${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${RED}                    COMMIT BLOCKED BY HOSTILE GATE                   ${NC}"
  echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "$VIOLATION_MESSAGES"
  echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${YELLOW}The EdgeVec Military-Grade Development Protocol enforces strict gates.${NC}"
  echo -e "${YELLOW}Complete the required workflow steps above before committing.${NC}"
  echo -e ""
  echo -e "${BLUE}Override (NOT RECOMMENDED):${NC}"
  echo -e "  git commit --no-verify -m \"[HUMAN_OVERRIDE] reason\""
  echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  exit 1
fi

# All gates passed
echo -e "${GREEN}[EdgeVec Pre-Commit]${NC} ✅ All gates passed. Commit allowed."
exit 0
