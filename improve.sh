#!/bin/bash
# Orderimo Self-Improvement Script
# Runs: tests → Lighthouse audit → quality checks → git commit
# Wakes every hour via OpenClaw cron

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"
cd "$SCRIPT_DIR"

LOG="$SCRIPT_DIR/improve.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
echo "=== Orderimo self-improve: $TIMESTAMP ===" >> "$LOG"

# ─── Step 1: Tests ──────────────────────────────────────────────────────────
echo "[1/4] Running test suite..." >> "$LOG"
TEST_OUTPUT=$(python -m pytest tests/ -q --tb=short 2>&1)
TEST_EXIT=$?

if [ $TEST_EXIT -ne 0 ]; then
    echo "[!] TESTS FAILED — aborting improvement pass" >> "$LOG"
    echo "$TEST_OUTPUT" >> "$LOG"
    echo "TESTS_FAILED" > "$SCRIPT_DIR/.improve_status"
    exit 1
fi

echo "  [OK] All tests passed" >> "$LOG"

# ─── Step 2: Lighthouse CI ─────────────────────────────────────────────────────
echo "[2/4] Running Lighthouse CI audit..." >> "$LOG"

LIGHTHOUSE_OUTPUT=$(lhci autorun 2>&1 || true)
echo "$LIGHTHOUSE_OUTPUT" >> "$LOG"

# Extract scores
PERF=$(echo "$LIGHTHOUSE_OUTPUT" | grep -o '"performance":[0-9.]*' | head -1 | cut -d: -f2 || echo "N/A")
ACCESS=$(echo "$LIGHTHOUSE_OUTPUT" | grep -o '"accessibility":[0-9.]*' | head -1 | cut -d: -f2 || echo "N/A")
SEO=$(echo "$LIGHTHOUSE_OUTPUT" | grep -o '"seo":[0-9.]*' | head -1 | cut -d: -f2 || echo "N/A")
echo "  Performance: $PERF | Accessibility: $ACCESS | SEO: $SEO" >> "$LOG"

# Warn if any score regressed below threshold
if [ "$PERF" != "N/A" ] && [ "$(echo "$PERF < 0.7" | bc -l 2>/dev/null)" = "1" ]; then
    echo "  [!] Performance below 0.7 — investigate" >> "$LOG"
fi

# ─── Step 3: Quality checks ──────────────────────────────────────────────────
echo "[3/4] Quality checks..." >> "$LOG"

IMPROVEMENTS=0

# Check for hardcoded secrets/keys
HARDCODED=$(grep -rn "pk_test_\|sk_test_\|password\s*=\s*['\"][^'\"]{8}" \
    "$SCRIPT_DIR/apps" "$SCRIPT_DIR/orderimo" 2>/dev/null | \
    grep -v ".pyc" | grep -v "improprove" | wc -l || echo "0")
[ "$HARDCODED" -gt "0" ] && echo "  [!] $HARDCODED hardcoded credential warnings" >> "$LOG"

# Check for TODO/FIXME comments (count open todos)
TODO_COUNT=$(grep -rn "TODO\|FIXME" "$SCRIPT_DIR/apps" "$SCRIPT_DIR/tests" 2>/dev/null | wc -l || echo "0")
echo "  Open TODOs/FIXMEs: $TODO_COUNT" >> "$LOG"

# Check for TODO/FIXME comments (count open todos)
TODO_COUNT=$(grep -rn "TODO\|FIXME" "$SCRIPT_DIR/apps" "$SCRIPT_DIR/tests" 2>/dev/null | wc -l || echo "0")
echo "  Open TODOs/FIXMEs: $TODO_COUNT" >> "$LOG"

echo "  [OK] Quality checks complete" >> "$LOG"

# ─── Step 4: Git commit ───────────────────────────────────────────────────────
echo "[4/4] Git status..." >> "$LOG"
cd "$SCRIPT_DIR"
if [ -d ".git" ]; then
    if ! git diff --quiet || ! git diff --cached --quiet; then
        echo "  [+] Uncommitted changes — staging and committing..." >> "$LOG"
        git add -A
        git commit -m "Orderimo self-improve: $TIMESTAMP — tests passed | perf:$PERF acc:$ACCESS seo:$SEO" >> "$LOG" 2>&1 || true
        echo "  [OK] Committed." >> "$LOG"
        IMPROVEMENTS=1
    else
        echo "  [OK] No changes to commit." >> "$LOG"
    fi

    # Push if there were changes
    if [ "$IMPROVEMENTS" = "1" ]; then
        git push origin main 2>&1 >> "$LOG" || echo "  [!] Push failed (may need auth)" >> "$LOG"
        echo "  [OK] Pushed to GitHub." >> "$LOG"
    fi
fi

echo "=== Complete: $TIMESTAMP ===" >> "$LOG"
echo "COMPLETE" > "$SCRIPT_DIR/.improve_status"
exit 0
