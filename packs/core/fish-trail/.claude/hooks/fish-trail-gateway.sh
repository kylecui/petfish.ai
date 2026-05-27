#!/usr/bin/env bash
# PEtFiSh fish-trail — UserPromptSubmit hook for Claude Code
# Outputs context reminder for topic governance enforcement.
# stdout is injected as additionalContext by Claude Code.

# Quick check: is fish-trail state directory present?
FISH_TRAIL_DIR=".petfish/fish-trail"

if [ -d "$FISH_TRAIL_DIR" ]; then
    echo "🐟 fish-trail active. Call topic_detect MCP tool before processing this message."
fi

exit 0
