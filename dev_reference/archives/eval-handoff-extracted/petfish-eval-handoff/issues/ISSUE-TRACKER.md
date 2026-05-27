# PEtFiSh Fish-Trail Issues Tracker

## Closed (Fixed)

| # | Title | Key Finding | Commit |
|---|-------|-------------|--------|
| 102 | Inline pack rules not stripped on upgrade | 26,850 tokens duplicated | Fixed in v0.11.1 |
| 145-163 | P1 evaluation series (17 issues) | Various MCP/quality bugs | Multiple |
| 164 | Cache-stable 3-block architecture | Topics/Related/Focus injection | e6614da |
| 165 | Mode-aware MCP suppression | [disk|rMCP:off] tag | e6614da |
| 166 | Reflective compression | Summary injection | e6614da |
| 167 | Tiered MCP access + compressionLevel | compact/full option | e6614da |
| 168 | compressionLevel dispatch dead code | formatActiveFocusFull never called | bdb388a |
| 169 | console.log TUI pollution | 19 stdout calls → stderr | 3e58529 |

## Open

| # | Title | Status | Impact |
|---|-------|--------|--------|
| 162 | topic_validate schema mismatch | Open | Validation fails |
| 163 | OpenCode hook API limitation | Open | Realtime mode blocked |
| 170 | v4 benchmark results report | Filed | Latest data |

## Discovered During Testing (Not Filed as Separate Issues)

- MCP server crash in opencode serve with minimal workspaces
- GPT-4o returns zero tokens via REST API
- DeepSeek Pro server failures during multi-model benchmark
- REST API does not expose internal tool call counts
- Claude input_tokens=1-3 is GitHub Copilot cache accounting artifact
