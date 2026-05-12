#!/bin/bash
# 3-Way A/B Test: v0.10.x vs v0.11.0+all-rules-plugin vs v0.11.0+smart-rules-plugin
#
# Tests whether injecting agents-rules into system prompt (cached) vs
# conversation context (uncached Read tool) reduces total token consumption.
#
# Setup:
#   tmux new-session -d -s test-servers
#   tmux send-keys "cd $(pwd)/test-v010x && OPENCODE_SERVER_PASSWORD=test opencode serve --port 3100" Enter
#   tmux new-window -t test-servers
#   tmux send-keys "cd $(pwd)/test-v011-allrules && OPENCODE_SERVER_PASSWORD=test opencode serve --port 3200" Enter
#   tmux new-window -t test-servers
#   tmux send-keys "cd $(pwd)/test-v011-smartrules && OPENCODE_SERVER_PASSWORD=test opencode serve --port 3300" Enter
#
#   Then: ./run_sysprompt_3way_test.sh [model]
#
set -euo pipefail

MODEL="${1:-github-copilot/claude-sonnet-4}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="sysprompt_3way_test_${TIMESTAMP}.log"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "============================================"
echo "  System Prompt Injection 3-Way Test"
echo "============================================"
echo "Model: $MODEL"
echo "Ports: v0.10.x=3100, v0.11.0+all-rules=3200, v0.11.0+smart-rules=3300"
echo ""

echo "Checking server health..."
for port in 3100 3200 3300; do
    if ! curl -sf -u opencode:test "http://localhost:$port/global/health" > /dev/null 2>&1; then
        echo "  ERROR: Server on port $port not responding"
        exit 1
    fi
    echo "  Port $port: OK"
done
echo ""

# Round 1: v0.10.x (baseline) vs v0.11.0+all-rules (plugin)
echo "========== ROUND 1: v0.10.x vs v0.11.0+all-rules =========="
AB_BASELINE_PORT=3100 AB_PLUGIN_PORT=3200 AB_PASSWORD=test AB_MODEL="$MODEL" \
    uv run ab_test_harness.py

cp ab_test_results.json "sysprompt_round1_${TIMESTAMP}.json"
echo "Round 1 results saved."

# Round 2: v0.10.x (baseline) vs v0.11.0+smart-rules (plugin)
echo ""
echo "========== ROUND 2: v0.10.x vs v0.11.0+smart-rules =========="
AB_BASELINE_PORT=3100 AB_PLUGIN_PORT=3300 AB_PASSWORD=test AB_MODEL="$MODEL" \
    uv run ab_test_harness.py

cp ab_test_results.json "sysprompt_round2_${TIMESTAMP}.json"
echo "Round 2 results saved."

echo ""
echo "============================================"
echo "  3-Way Test Complete"
echo "============================================"
echo "Round 1 (v0.10.x vs all-rules): sysprompt_round1_${TIMESTAMP}.json"
echo "Round 2 (v0.10.x vs smart-rules): sysprompt_round2_${TIMESTAMP}.json"
echo "Log: $LOG_FILE"
