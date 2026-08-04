# PPT Skills Pack Rules

This pack provides PPTX reading and writing capabilities for course slides, proposals, reports, and technical decks.

## Skill Routing (强制)

### Rules

1. When the user wants to **read, inspect, summarize, audit, or compare** a PPT/PPTX file, **MUST** route to `ppt-reader`. Do NOT route to `ppt-writer`.
2. When the user wants to **create, rewrite, restructure, update, or export** a PPT/PPTX deck, **MUST** route to `ppt-writer`. Do NOT route to `ppt-reader`.
3. When the user provides a Markdown outline, document, meeting notes, or old PPT and asks to generate a new deck, **MUST** route to `ppt-writer`.
4. When the user asks for a "rewrite brief" or "per-slide action plan" as input for a future writing task, **MUST** route to `ppt-reader` (produces the brief), then `ppt-writer` (executes it).
5. When the user asks for visual QA of a generated deck, **MUST** use `ppt-writer`'s `qa_deck.py` step — do NOT treat this as a `ppt-reader` task.

### Conflict Resolution

- "Read and then rewrite" requests: route `ppt-reader` first, then `ppt-writer` to execute. Do not merge.
- "Summarize the slides" = `ppt-reader`. "Update the slides" = `ppt-writer`.
- When ambiguous, ask: is the primary output a **report about** the deck (`ppt-reader`) or **a new deck** (`ppt-writer`)?

## ppt-reader Workflow

1. Extract slide inventory → `pptx_inventory.json` (titles, layout, notes, comments, media, links)
2. Produce Markdown summary of structure and content
3. Flag: missing placeholders, sensitive info, broken links, layout inconsistencies
4. Optionally produce a rewrite brief / per-slide action plan for `ppt-writer`

## ppt-writer Workflow

1. Receive input: Markdown / doc / outline / old PPTX / rewrite brief
2. Build narrative structure and page plan
3. Run `build_deck.py` → `qa_deck.py` → fix issues → re-verify until QA passes
4. Deliver final PPTX

## Behavioral Rules

- Never skip the `qa_deck.py` step after `build_deck.py`. Generate → QA → fix → re-verify is mandatory.
- `ppt-reader` output must be saved before passing to `ppt-writer`.
- Do not mix reading and writing in a single tool invocation.
