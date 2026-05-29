# Series Style Rules

## Style consistency is multi-layered

Assess consistency in the following order:

1. Conceptual consistency: the same concept should not drift into incompatible meanings.
2. Structural consistency: chapters should use compatible section architecture.
3. Terminology consistency: preferred terms should dominate aliases.
4. Naming consistency: modules, chapters, figures, and tables should follow one convention.
5. Typographic consistency: Markdown, punctuation, and spacing should be predictable.
6. Voice consistency: tone and sentence rhythm should feel like the same series.

## Baseline is a contract, not a cage

Use the baseline to infer default rules. However:

- Do not force a weak baseline pattern onto stronger later chapters.
- Do not preserve obvious baseline mistakes.
- Report internal baseline inconsistency before applying it to target files.
- Ask the user to confirm a new convention when several valid conventions coexist.

## Common drift patterns

- Same concept appears under several names.
- Section titles gradually shift from analytical to marketing style.
- Early chapters use numbered headings, later chapters use free-form headings.
- Some files use `AI Agent`, others use `智能体`, `Agent`, or `智能代理`.
- Markdown tables have inconsistent alignment and caption placement.
- CJK-English spacing changes within or across files.
- Later chapters omit summary sections that are standard in the baseline.

## Severity levels

- `Pass`: conforms to the profile or variation is intentional and harmless.
- `Warning`: inconsistency exists but does not harm comprehension.
- `Fail`: inconsistency affects series identity, terminology precision, or reader navigation.
- `Blocked`: a safe automatic fix is not possible without user or author judgment.
