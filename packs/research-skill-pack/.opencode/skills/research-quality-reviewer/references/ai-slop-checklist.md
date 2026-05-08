# AI Slop Checklist

## What is AI Slop?

AI-generated text that sounds authoritative but contains no real substance. It fills space without adding information or evidence.

## Red Flag Phrases

### Hollow Authority Claims
- "It is widely recognized that..."
- "Experts agree that..."
- "Research has shown that..." (without citing which research)
- "It is well-established that..."

### Vague Importance Signals
- "increasingly important"
- "plays a crucial role"
- "has become essential"
- "cannot be overstated"
- "in today's rapidly evolving landscape"

### Filler Transitions
- "It is worth noting that..."
- "It should be mentioned that..."
- "Another important aspect is..."
- "Furthermore, it is important to consider..."

### Unsupported Superlatives
- "comprehensive and robust"
- "cutting-edge"
- "state-of-the-art" (without comparison)
- "best-in-class"
- "world-class"

### Circular Definitions
- "X is important because it plays an important role in Y"
- "The significance of X lies in its significant impact on..."

## Detection Rules

For each flagged phrase, check:
1. Is there a specific evidence_id supporting this claim?
2. Can the phrase be replaced with a concrete fact?
3. Would removing the phrase lose any information?
4. Is this just padding to reach a word count?

## Remediation

| Problem | Fix |
|---|---|
| "Increasingly important" | Replace with trend data + source |
| "Widely recognized" | Cite who recognizes it |
| "Comprehensive and robust" | State specific capabilities |
| "In today's rapidly evolving" | Delete entirely or cite specific change |
| "Research has shown" | Cite the specific research |

## Acceptable Uses

Some phrases are acceptable when:
- They are genuine topic sentences followed by evidence
- They appear in a limitations section acknowledging uncertainty
- They are in informal notes, not final reports
