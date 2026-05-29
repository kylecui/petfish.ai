# Rewrite Boundaries

## Safe changes

The agent may apply these changes when unambiguous:

- Normalize CJK-English spacing according to the profile.
- Replace a known alias with the preferred term.
- Normalize heading numbering style.
- Normalize Markdown blank lines.
- Normalize list markers.
- Fix repeated obvious layout inconsistencies.

## Review-needed changes

The agent must report these before applying them:

- Rewriting definitions.
- Moving paragraphs across sections.
- Shortening technical explanations.
- Replacing examples.
- Changing claim strength, such as `可能` → `必然`.
- Reframing conclusions or recommendations.
- Removing hedging language.

## Blocked changes

Do not perform these changes unless explicitly instructed:

- Add new facts.
- Invent citations.
- Remove citations.
- Change legal, medical, financial, or technical meaning.
- Rewrite the document to sound like generic marketing copy.
- Translate the whole document into another language.
- Convert Markdown into another file format.

## Rewrite report requirement

Every rewrite should produce a short report with:

- files changed
- safe fixes applied
- review-needed changes not applied
- blocked changes
- unresolved style decisions
