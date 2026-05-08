# Evidence Taxonomy

## Evidence Types

| Type | Meaning | Can enter report? | Requirement |
|---|---|---|---|
| `EXTRACTED` | Directly from source | Yes | Must cite source and location |
| `INFERRED` | Derived from multiple facts | Yes | Must state reasoning chain |
| `AMBIGUOUS` | Conflicting or insufficient | Yes, as uncertainty | Must state conflict sources |
| `PROPOSED` | Our suggestion/hypothesis | Yes, as recommendation | Must label clearly |

## Confidence Levels

| Level | Meaning |
|---|---|
| `high` | Multiple independent sources agree; well-established fact |
| `medium` | Single reliable source; or multiple sources with minor conflicts |
| `low` | Limited evidence; single non-authoritative source; or inference with assumptions |

## Evidence Promotion Rules

From excerpt notes to evidence ledger:
1. Excerpt must have source_id and location
2. Claim must be articulable in one sentence
3. Type must be classified
4. Confidence must be assessed
5. Supporting/contradicting relationships must be noted

## Claim Map Conventions

- `CL-XXXXXX` — claim identifier
- Each claim references 1+ evidence entries
- Claims can be: Supported, Contested, Unsupported, Withdrawn
- Contested claims must list both supporting and contradicting evidence

## Contradiction Handling

When sources conflict:
1. Record both sides in evidence ledger
2. Note the contradiction in contradiction-log.md
3. Assess which source is more authoritative/recent
4. Mark claim as AMBIGUOUS if unresolvable
5. Report must disclose the contradiction
