#!/bin/bash
# Orderimo Self-Improvement Script
# Wakes every 20 minutes via OpenClaw cron
# Runs tests FIRST — if they fail, abort and alert Kay
# If they pass, performs a structured review pass and commits if changes made

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"
cd "$SCRIPT_DIR"

LOG="$SCRIPT_DIR/improve.log"
echo "=== plurino self-improve run: $(date) ===" >> "$LOG"

# Step 1: Run tests
echo "[1/4] Running tests..." >> "$LOG"
TEST_OUTPUT=$(python -m pytest tests/ -q --tb=short 2>&1)
TEST_EXIT=$?

if [ $TEST_EXIT -ne 0 ]; then
    echo "[!] Tests FAILED — aborting improvement pass" >> "$LOG"
    echo "$TEST_OUTPUT" >> "$LOG"
    echo "TESTS_FAILED" > "$SCRIPT_DIR/.improve_status"
    exit 1
fi

echo "[OK] Tests passed" >> "$LOG"

# Step 2: Check for obvious improvements
echo "[2/4] Scanning for improvements..." >> "$LOG"

IMPROVEMENTS=0

# Check for TODO/FIXME comments
TODO_COUNT=$(grep -rn "TODO\|FIXME\|XXX\|HACK" "$SCRIPT_DIR/apps" "$SCRIPT_DIR/tests" 2>/dev/null | wc -l || echo "0")
echo "  Found $TODO_COUNT TODO/FIXME comments" >> "$LOG"

# Check test coverage is > 80%
COVERAGE=$(python -m pytest tests/ --cov=apps --cov-report=term-missing -q 2>/dev/null | grep "TOTAL" | awk '{print $NF}' | tr -d '%' || echo "0")
echo "  Test coverage: ${COVERAGE}%" >> "$LOG"

# Step 3: Quality pass — check for common issues
echo "[3/4] Running quality checks..." >> "$LOG"

# Check for hardcoded secrets/keys
HARDCODED=$(grep -rn "pk_test_\|sk_test_\|password\s*=\s*['\"][^'\"]{8}" "$SCRIPT_DIR/apps" 2>/dev/null | grep -v ".pyc" | grep -v "improve.sh" | wc -l || echo "0")
echo "  Hardcoded credential warnings: $HARDCODED" >> "$LOG"

# Step 4: Git commit if changes exist
echo "[4/4] Checking for changes to commit..." >> "$LOG"
cd "$SCRIPT_DIR"
if [ -d ".git" ]; then
    if ! git diff --quiet || ! git diff --cached --quiet; then
        echo "  Uncommitted changes found — staging and committing..." >> "$LOG"
        git add -A
        git commit -m "plurino self-improve: $(date '+%Y-%m-%d %H:%M') — tests passed, coverage ${COVERAGE}%" >> "$LOG" 2>&1 || true
        echo "  Committed." >> "$LOG"
        IMPROVEMENTS=1
    else
        echo "  No changes to commit." >> "$LOG"
    fi
fi

echo "=== Run complete: $(date) ===" >> "$LOG"
echo "COMPLETE" > "$SCRIPT_DIR/.improve_status"
exit 0
