# MCP Tool Calling Investigation Report

**Date**: 2026-05-23
**Models tested**: DeepSeek-V4-Flash, DeepSeek-V4-Pro

## Summary

DeepSeek V4 models **can and do call MCP tools** when the user's message explicitly requests it. They do NOT call them proactively based on system prompt rules alone. This is a model behavior issue, not an infrastructure problem.

## Investigation Method

Used a local HTTP proxy (`/tmp/deepseek_proxy.py`) to intercept all requests from opencode to the DeepSeek API, logging the full request body including tools array and message history.

## Key Findings

### 1. MCP tools ARE sent to the API

Request 2 (first actual LLM call) contained **42 tools**:
- 11 builtin opencode tools (bash, read, grep, edit, write, glob, task, webfetch, skill, todowrite, question)
- **31 MCP tools** (context-state_*)
- `tool_choice: "auto"` (default)

MCP tool schemas totaled ~3,395 tokens; builtin tools ~19,010 tokens. All properly formatted as OpenAI function tools.

### 2. Model DOES call tools when appropriate

Test: "Read the file opencode.json" → Model called `read` tool → got file content → responded correctly.

Test: "Use context-state_topic_list and context-state_topic_detect" → Model called both MCP tools.

### 3. Model does NOT proactively call MCP tools

Despite fish-trail rules saying "call topic_detect on every message", the model:
- Ignores the instruction for routine messages ("Fix this TypeError", "Configure CI/CD")
- Only calls tools when the user's message explicitly mentions the tool or strongly implies it
- This applies to both Flash and Pro variants

### 4. Tool calling cost is real when it happens

When the model does call MCP tools, the cost profile is:
- 1 user message → 3 API round-trips (tool_call + result + final_response)
- Each round-trip includes the full tools array (42 tools × ~22K tokens total)
- The tool results enter the uncached conversation context

### 5. DeepSeek V4 behavior pattern

DeepSeek V4 models appear to follow a "minimum intervention" principle:
- If they can answer from context/reasoning, they won't call tools
- If tools are explicitly requested, they call them
- System prompt instructions about tool calling are treated as guidelines, not requirements
- This contrasts with Claude (which follows system prompt tool instructions more faithfully)

## Implications for Fish-Trail Architecture

### Current state (broken)
- Rules say "call topic_detect every turn" → Model ignores → No topic context injected → Quality no better than no-rules

### Plugin-inject (working)
- Topic context is pre-injected into system prompt → Model has context without calling tools → Quality is good

### Hybrid approach (viable but limited)
- Plugin-inject for routine turns (cached, cheap, always available)
- MCP tools for user-initiated actions (explicit topic management)
- The model WILL call MCP tools when the user says "show me topics" or "switch to X"
- The model will NOT call MCP tools proactively for topic detection

## Recommendations

1. **Plugin-inject is the right primary mechanism** — it provides topic context without depending on model's willingness to call tools
2. **MCP tools should be user-initiated only** — "show topics", "create topic", "switch topic" are fine; "detect topic automatically" is not reliable
3. **Update fish-trail rules** — remove "call topic_detect on every message"; replace with "topic context is provided in your system prompt"
4. **File issue to DeepSeek** — reasoning models should respect system prompt tool-calling instructions more consistently (though this is a model behavior, not a bug)

## Request Log Evidence

| Request | Tools Sent | Tool Choice | Notes |
|---------|-----------|-------------|-------|
| req 1 | 0 | not set | Title generation |
| req 2 | 42 | auto | First LLM call (no tool use) |
| req 3 | 0 | not set | Title generation (2nd session) |
| req 4 | 42 | auto | First LLM call (no tool use) |
| req 5 | 42 | auto | Follow-up after `read` tool call |
| req 6 | 0 | not set | Title generation (3rd session) |
| req 7 | 42 | auto | Called `topic_list` + `topic_detect` |
| req 8 | 42 | auto | Final response after tool results |

Raw request captures saved in `/tmp/deepseek_requests/`.
