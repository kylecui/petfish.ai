# Citation Policy

## 1) Purpose and enforceable scope

This policy defines how citation integrity is audited in research outputs that are expected to influence decisions. It applies to scientific drafts, architecture analysis, product research reports, policy briefs, and planning documents. The policy is not about style compliance. It is about claim accountability. A compliant document allows another reviewer to reconstruct why each critical statement exists and to verify that statement against a traceable source path.

The minimum required traceability chain is:

`claim -> evidence_id -> source_id -> accessible location`

Definitions:

- **claim**: a statement that describes fact, trend, comparison, risk, conclusion, or recommendation basis.
- **evidence_id**: a ledger entry that captures what was observed or inferred, how confident we are, and where it came from.
- **source_id**: a source index record containing title, origin, date metadata, and access path.
- **accessible location**: a concrete URL or file path with fine grained locator (page, section, paragraph, timestamp, commit, issue, or anchor).

If any link in this chain is missing or invalid, the claim is unsupported. Unsupported claims must be repaired, downgraded, or removed before release.

## 2) Claim classes and priority levels

Citation audit starts by classifying claims. This reduces noise and ensures high impact statements receive strict verification.

### Class A: Critical claims

Claims that influence architecture choice, compliance posture, budget, launch decision, risk rating, or executive recommendation.

### Class B: Supporting claims

Claims that provide comparison context, rationale detail, or secondary interpretation.

### Class C: Descriptive claims

Low impact context statements that do not materially change the conclusion.

Policy:

- Class A must have complete and semantically aligned citation chains.
- Class B must have complete chains; limited remediation backlog is allowed only if explicitly recorded.
- Class C may use lighter treatment if it cannot be misread as decision evidence.

Any language such as “最新”, “领先”, “主流”, “best”, “leading”, “widely adopted”, “industry standard”, “state of the art” automatically escalates the statement to Class A.

## 3) Chain validation rules

### 3.1 Claim -> evidence_id

- Every Class A claim maps to at least one directly relevant evidence entry.
- Multi part claims should map to multiple evidence entries.
- INFERRED evidence is allowed, but inference steps must be inspectable.
- Evidence text must support the claim semantics, not merely share keywords.

### 3.2 evidence_id -> source_id

- Each evidence entry must resolve to an existing source record.
- source_id must not be orphaned, placeholder, or stale without annotation.
- evidence location must be precise. “paper said” is invalid.

### 3.3 source_id -> accessible location

- URL must load or be archived with verifiable mirror.
- Local path must be accessible in workspace history.
- For mutable sources, access timestamp is required.
- For versioned docs, version identifier is required.

## 4) Rules for statistical claims

Numeric statements are often misused. The following checks are mandatory:

1. **Date**: when data was collected, when published, and which period it represents.
2. **Sample**: sample size, sampling frame, inclusion criteria, and representativeness limits.
3. **Scope**: geography, segment, metric definition, denominator, and calculation method.

Additional checks:

- Unit consistency (absolute count, rate, percentage).
- Denominator consistency across compared numbers.
- Distinguish correlation from causation.
- Include uncertainty indicators where available.

Failure patterns:

- old baseline presented as current market state,
- selective quotation that removes caveats,
- percentage comparison across incompatible populations,
- reporting gain without tradeoff cost.

## 5) Rules for regulation and compliance claims

Regulatory claims must be time aware and jurisdiction aware.

Mandatory checks:

1. Effective status: draft, effective, amended, repealed, transitional.
2. Applicability boundary: subject type, geography, industry, and processing context.
3. Source hierarchy: primary legal text first, commentary second.

If secondary interpretation is cited, the primary source must also be cited. Absolute compliance wording (“fully compliant”, “always required”, “completely prohibited”) requires blocking review and explicit legal boundary notes.

## 6) Rules for product capability claims

Product features evolve quickly. Capability claims are valid only with version context.

Mandatory checks:

1. Verify current version or release channel.
2. Distinguish GA, Beta, Preview, and roadmap.
3. Verify plan/tier/region dependencies.
4. Verify claim date aligns with release notes.

Invalid pattern: roadmap promise written as current capability.
Insufficient pattern: marketing page only citation for technical behavior.

## 7) High risk wording and downgrade protocol

If evidence is insufficient for high confidence language, downgrade wording instead of overstating certainty.

Approved downgrade patterns:

- “within the reviewed sample as of DATE”
- “under tested conditions”
- “available sources suggest”
- “preliminary evidence indicates”

The downgrade protocol preserves decision quality by aligning language strength with evidence strength.

## 8) Audit outputs and required fields

### citation-audit.md

- scope and document version
- coverage metrics by claim class
- blocking issues and rationale
- non blocking risk items
- remediation actions and ownership hints

### unsupported-claims.md

- claim text
- missing chain segment
- risk rating
- remediation path

### source-coverage.md

- source usage concentration
- stale source list
- broken links or inaccessible paths
- single source dependency risk

## 9) Decision policy

- **PASS**: all critical claims have complete valid chains.
- **CONDITIONAL**: no critical breaks, but limited medium risk gaps remain.
- **FAIL**: any critical unsupported claim, invalid legal status usage, broken statistical context, or inaccessible core source.

A FAIL result blocks publication. Fix chain integrity first, rerun audit second.

## 10) Operational checklist

- [ ] enumerate critical claims
- [ ] resolve evidence links
- [ ] resolve source links
- [ ] verify location precision
- [ ] verify date/sample/scope for statistics
- [ ] verify effective status for regulation
- [ ] verify version state for product claims
- [ ] align wording intensity with confidence

Citation quality is not achieved by adding more links. Citation quality is achieved when each key statement can be independently reconstructed and challenged using the recorded evidence path.
