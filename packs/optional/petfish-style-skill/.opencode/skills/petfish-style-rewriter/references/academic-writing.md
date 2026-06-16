# Academic Writing — Humanization Framework

This reference extends the `academic` mode. It covers two concerns the main SKILL.md only sketches:

1. How to detect AI-flavored academic prose at the linguistic level (beyond the four categories in `ai-slop-detector.md`).
2. How to rewrite academic prose so it reads like a real researcher wrote it, without losing precision or over-correcting into casual writing.

Academic writing is a special case. The engineering-style rules in the main skill (split long sentences, one idea per sentence, no decoration) still apply to the *argument* sections. But academic writing also carries authorial voice, hedged claims, controlled asymmetry, and citations. Applying the strict engineering style verbatim produces text that is correct but reads as machine-generated. This reference explains when to diverge.

## When to use this reference

Load this file when the task involves:

- Paper drafts (introduction, related work, method, results, discussion)
- Thesis or dissertation chapters
- Survey or review articles
- Technical reports with academic register
- Grant or proposal sections written in academic register
- Rewriting AI-generated abstracts or paragraphs into defensible academic prose

Do not load it for slide bullet points, code comments, or support emails — those use the default engineering style.

## Part 1 — Linguistic Detection Framework

AI-generated academic prose leaves detectable traces beyond the four surface patterns (dash abuse, English AI words, triplets, empty not-X-but-Y). The features below are the ones detection systems weigh most heavily. Use them as a self-check, not as a way to evade detection — the goal is to write like a competent human, not to fool a classifier.

### 1. Perplexity (词汇困惑度)

- **AI signal**: every word is the most probable next token. The text is "clean" and predictable.
- **Human signal**: occasional lower-probability word choices, mild redundancy, or stylistic phrasing.
- **Rewrite move**: replace the single most obvious word with a slightly less common but accurate alternative. Example: "improve" → "stabilize"; "important" → "consequential" (when the stronger claim is justified).

### 2. Burstiness (句长波动)

- **AI signal**: sentence lengths cluster around a narrow band. Structure repeats.
- **Human signal**: high variance — one long sentence, then a very short one, then a medium one.
- **Rewrite move**: intentionally vary sentence length. A 3-word sentence after a 35-word sentence is not a flaw in academic writing; it is a recognizable human rhythm. Compute burstiness (see `style_check.py`) and if the coefficient of variation is below ~0.4, rewrite for variation.

### 3. Syntactic symmetry (句式对称性)

- **AI signal**: repeated sentence templates: "X does Y. This suggests Z. Therefore W." Every paragraph follows the same skeleton.
- **Human signal**: templates break. A paragraph may start with a contrast, insert a parenthetical, or open with the conclusion.
- **Rewrite move**: break the template deliberately in at least one paragraph per section. Move the conclusion forward, insert an example mid-paragraph, or open with a limitation.

### 4. Token likelihood density (词汇概率密度)

- **AI signal**: every phrase is the "safest" phrasing. No strange idioms, no field-specific verbal tics.
- **Human signal**: researchers reuse specific phrases ("we observe that", "this is consistent with", "somewhat to our surprise"), and these verbal tics are part of authorial voice.
- **Rewrite move**: introduce discipline-standard hedges and authorial phrases (see Part 3), not generic filler.

### 5. Semantic alignment (语义对齐度)

- **AI signal**: when paraphrasing, the meaning and information order stay 100% aligned with the source.
- **Human signal**: paraphrasing reorders information, drops some points, emphasizes others.
- **Rewrite move**: when summarizing prior work, intentionally reorder the information to serve your argument rather than mirroring the original order.

### 6. Logical over-coherence (逻辑过度完美)

- **AI signal**: every paragraph follows background → method → result → conclusion. Transitions are explicit and symmetric.
- **Human signal**: some transitions are implicit; an example may be dropped in without a signpost; a limitation may appear before the result it qualifies.
- **Rewrite move**: drop one explicit connector per page. Trust the reader to follow a two-step inference without "Therefore".

### 7. Technical density (术语堆叠密度)

- **AI signal**: dense chains of jargon with no surrounding explanation, used to sound authoritative.
- **Human signal**: jargon is introduced with a one-line gloss on first use, then used freely.
- **Rewrite move**: on first mention of any non-standard term, append a parenthetical definition or a short clause. After that, use the term without ceremony.

### 8. Paragraph templating (段落模板化)

- **AI signal**: every paragraph has the same internal shape and the same length.
- **Human signal**: paragraphs vary in length and shape — one may be a single observation, another a four-sentence argument.
- **Rewrite move**: deliberately write at least one short paragraph (2–3 sentences) and one longer paragraph (5–7 sentences) per page.

### 9. Missing human noise (缺乏人类噪声)

- **AI signal**: no hesitation, no qualifications, no "we initially expected X but found Y".
- **Human signal**: controlled imperfection — a qualification, a surprise, a scope limit.
- **Rewrite move**: add one candid observation per section ("This effect was smaller than we expected" or "We cannot rule out confound C, but…").

### 10. Missing authorial fingerprint (缺乏作者印记)

- **AI signal**: no consistent voice. Every section could have been written by a different model.
- **Human signal**: recurring phrases, a consistent stance toward certainty, a characteristic way of introducing examples.
- **Rewrite move**: choose 2–3 authorial phrases and use them consistently (see Part 3).

## Part 2 — Humanization Techniques

These techniques make academic prose read as human-written while remaining defensible. Apply them selectively, not exhaustively — over-applying all seven produces a different kind of artificiality.

### 2.1 Add controlled imperfection

Insert a short clause that breaks the rhythm or qualifies a claim.

- **AI-like**: "Relying on the model's implicit behavior, we obtain competitive results."
- **Human**: "Relying on the model's implicit behavior, we found it necessary — almost unexpectedly — to specify what must be preserved."

The dash here is earned because it carries real semantic weight (a genuine surprise), not rhythm for its own sake. This is consistent with the dash-abuse rule in `ai-slop-detector.md`: dashes survive only when they add information.

### 2.2 Reorder information

AI paraphrases preserve source order. Human paraphrases serve the argument's order.

- **Source order**: "Background → Gap → Method → Result"
- **Human variant**: lead with the result, then qualify with method and limitation, then situate against background.

In abstracts and introductions, moving the contribution forward is often the most effective single rewrite.

### 2.3 Choose non-obvious vocabulary

Replace the single most probable word with a slightly less common synonym, but only when the synonym is at least as accurate.

| AI-default | Human variant | When the variant is justified |
|---|---|---|
| improve | stabilize, bring down | when the change is a reduction, not a generic gain |
| important | consequential, material | when importance is load-bearing for the argument |
| show | indicate, suggest | when the evidence is indirect |
| use | rely on, draw on | when there is a dependency relationship |

Do not replace for the sake of replacing. A word that is less accurate but less probable is worse than the default.

### 2.4 Vary sentence length on purpose (burstiness)

After a long compound sentence, write a short one. A 4-word sentence in an academic paper is a recognizable human move:

> These effects were small. They were also inconsistent across seeds.

The second sentence could have been a subordinate clause ("..., although they were inconsistent across seeds"). Keeping it as a standalone short sentence is a deliberate human rhythm choice.

### 2.5 Use authorial voice

Academic writing permits a small set of authorial phrases that signal stance. These are not filler; they carry epistemic information.

- "We found that…" (claim of direct observation)
- "In our experience…" (claim of practice-based judgment)
- "Somewhat surprisingly…" (flags a result that resists the obvious interpretation)
- "We cannot rule out…" (explicit hedge)
- "This is consistent with…" (links to prior work without overclaiming)
- "To our knowledge…" (scopes a novelty claim)

Use 2–3 of these consistently across a paper. They become the authorial fingerprint that Part 1, feature 10 asks for.

### 2.6 Break over-symmetry

AI over-uses parallel constructions: "A does X, and B does Y", "A, B, and C".

- **AI-like**: "A does X, and B does Y."
- **Human**: "A does X. B, however, behaves differently under this condition."

The second version breaks the symmetry and adds a qualification. Use this move once or twice per section, not in every sentence — over-using "however" is itself an AI tell.

### 2.7 Add controlled semantic drift

When paraphrasing or summarizing, let the meaning shift slightly to reflect your interpretation.

- **Source**: "Explicit obligations improve contract adherence."
- **Human paraphrase**: "Spelling out these obligations tends to stabilize behavior, at least in the settings we examined."

The paraphrase adds a scope limit ("at least in the settings we examined") and shifts "improve" to "stabilize" — a narrower, more defensible claim. This is not misrepresentation; it is responsible hedging.

## Part 3 — Human Academic Writing Template

This template operationalizes the techniques above into a section-by-section shape. It is not the only valid shape. Deviate when the argument demands it.

### Abstract (150–250 words)

1. **Opening sentence**: state the problem or gap. Avoid "In recent years…" openings.
2. **Second sentence**: state the approach in one clause. Add a natural adverb ("empirically", "in a controlled setting") if accurate.
3. **Third sentence**: state the main result with a number or a bounded claim.
4. **Fourth sentence**: add one qualification or scope limit.
5. **Closing sentence**: state the implication, hedged.

Avoid the symmetric "Background / Method / Result / Conclusion" template that reads as machine-generated. Reorder when the result is the most interesting part.

### Introduction

- Paragraph 1: the problem, stated concretely. Do not over-expand background.
- Paragraph 2: why existing approaches fall short. Name them.
- Paragraph 3: what this work does, in one or two sentences, then the contribution list.
- Paragraph 4 (optional): a roadmap, only if the paper is long or non-standard.

Insert at least one authorial-voice phrase ("we observe", "to our knowledge") and at least one candid qualification.

### Related Work

- Group prior work by approach, not by author or year.
- For each group: one sentence on the approach, one on the limitation relevant to this paper.
- End with a sentence that positions this work relative to the closest prior approach.

Do not list papers as a flattened enumeration. The grouping itself is an authorial choice.

### Method

- Lead with the formal setup or the data, whichever is more concrete.
- Introduce each non-standard term with a one-line gloss on first use.
- Use numbered definitions or algorithms when the logic is intricate.
- End the section with a scope statement: what this method does and does not claim to do.

### Results

- State the main result first, then the secondary results.
- Report numbers with intervals or dispersion measures, not point estimates alone.
- Use "we observe" or "we find" for direct observations; reserve "this suggests" or "this indicates" for interpreted claims.
- Note at least one negative, null, or surprising result.

### Discussion

- Open with the result that was most surprising or most consequential.
- Contrast with the closest prior result.
- List limitations explicitly, grouped by source (data, method, scope).
- Close with a bounded forward statement, not a slogan.

### Conclusion

- One paragraph. Restate the contribution in different words (not a copy of the abstract).
- Add one scope limit that was not in the abstract.
- Close with a specific next step, not "future work is promising".

## Part 4 — Tension Resolution

The engineering-style rules in the main SKILL.md sometimes conflict with academic humanization. Resolve as follows.

| Engineering rule | Academic exception | Resolution |
|---|---|---|
| Break long sentences into medium ones | Burstiness is a human signal | Allow one long sentence (35–50 words) per page, then a short one. Do not let long sentences accumulate. |
| Remove all decoration | Authorial phrases carry epistemic weight | Keep "we found", "to our knowledge", "somewhat surprisingly" — they are not decoration, they are stance markers. |
| One idea per sentence | Academic sentences sometimes carry a claim plus a qualification | A claim plus a one-clause qualification is one idea. A claim plus three subordinated clauses is not. |
| Avoid hedges | Hedging is responsible in academic writing | Hedge when the evidence is indirect. Remove hedges when the evidence is direct and the claim is load-bearing. |
| Compact Chinese-English spacing | Academic Chinese still follows the compact rule | No exception. Use `Webhook挂载`, not `Webhook 挂载`, even in formal Chinese academic writing. |

The default is still the engineering style. Diverge only with a reason, and only in the direction the academic register requires.

## Part 5 — Academic Anti-patterns

These extend the general anti-patterns in `ai-slop-detector.md` with academic-specific failure modes.

### 5.1 The symmetric paragraph pile

Every paragraph in a section has the same shape and length. Rewrite: vary paragraph length by ≥2 sentences across adjacent paragraphs.

### 5.2 The connector stack

Transitions are explicit in every sentence: "First… Second… Third… Therefore…". Rewrite: drop at least one connector per page and let the logic carry.

### 5.3 The jargon pile-up

Three or more non-standard terms in one sentence with no gloss. Rewrite: gloss the first term, drop or defer the others.

### 5.4 The hedge pile-up

Every claim has two or more hedges ("may potentially suggest", "could possibly indicate"). Rewrite: one hedge per claim, chosen for the strongest epistemic meaning ("suggests" > "may suggest" > "could possibly suggest").

### 5.5 The empty roadmap

"We organize the paper as follows. Section 2 reviews… Section 3 presents… Section 4 discusses…". Rewrite: keep only if the paper structure is non-standard. For standard IMRaD, drop the roadmap.

### 5.6 The over-claimed contribution

"We are the first to…" without a bounded scope. Rewrite: "To our knowledge, this is the first work to [specific action] in [specific setting]." If you cannot bound the claim, drop the novelty claim and state the contribution empirically.

## Part 6 — Self-check

Before finalizing an academic rewrite, run this checklist.

1. **Burstiness**: is there at least one short sentence (≤8 words) and one long sentence (≥30 words) per page?
2. **Authorial voice**: are there 2–3 consistent authorial phrases across the text?
3. **Tempting symmetry**: does at least one paragraph per section break the dominant template?
4. **Hedges**: is each hedge load-bearing (not stacked)?
5. **Jargon**: is every non-standard term glossed on first use?
6. **Candor**: is there at least one candid qualification or surprise per section?
7. **Connectors**: is at least one connector per page dropped in favor of implicit logic?
8. **Contributions**: are novelty claims bounded by scope?

If any answer is "no", revise before finalizing. Run `scripts/style_check.py` for the burstiness and connector metrics; the rest are judgment calls.
