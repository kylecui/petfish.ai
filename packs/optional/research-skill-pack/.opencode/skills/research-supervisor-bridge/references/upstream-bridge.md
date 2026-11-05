# Upstream Bridge Details — licenses, per-OS setup, and design rationale

Companion to SKILL.md. This file carries the details SKILL.md deliberately
omits: a license FAQ, per-OS fetch commands, and the rationale for building
`research-mentor-cards` instead of vendoring upstream content.

---

## License FAQ (CC BY-NC-SA 4.0, Supervisor-Skills handbook and skills)

| Use case | Allowed under NC? | Notes |
|---|---|---|
| Personal learning, reading the handbook | Yes | Attribution (BY) still required when sharing |
| Coursework / academic exercises | Generally yes | Non-commercial; share adaptations under the same license (SA) |
| University teaching materials | Generally yes | Same SA obligation |
| Company R&D evaluating research tooling | Gray zone | "Commercial" is judged by purpose and context, not by who pays; ask HKUSTDial when in doubt |
| A product or service that ships the content | **No** without separate permission | Upstream has existing licensing partnerships (Baidu, Doubao) - contact them for terms |
| Adapting content into an open-source pack | **No for NC purposes**, and SA applies | This is why PEtFiSh does not vendor upstream content |

Attribution format when sharing anything derived: cite
`HKUSTDial/Supervisor-Skills` (with link), state the license, link the license.

Snapshot note: licenses and partnerships described here reflect the repos as
of 2026-10; re-verify before relying on them.

---

## Per-OS fetch commands

All platforms use the same two steps: create the upstream directory via a
uv one-liner (cross-platform `Path.home()` expansion), then plain `git clone`
(git itself is cross-platform). **No platform-locked shell commands** - this
skill must stay runnable from any shell.

Step 1 - create the directory (identical syntax in every shell):

```bash
uv run python -c "from pathlib import Path; p = Path.home() / '.local' / 'share' / 'opencode' / 'upstream'; p.mkdir(parents=True, exist_ok=True); print(p)"
```

Step 2 - clone (paste the printed absolute path for `<upstream-dir>`):

```bash
git clone https://github.com/HKUSTDial/Supervisor-Skills.git <upstream-dir>/supervisor-skills
git clone https://github.com/yinwu01/Ducktor.git <upstream-dir>/ducktor
```

After cloning, follow each repo's own INSTALL.md / plugin manifests for
platform integration (Ducktor ships claude/codex/cursor plugin configs).
Re-check the repos periodically: upstream moves fast (new skills, license
clarifications, partnerships).

---

## Why PEtFiSh built its own cards instead of vendoring

Three reasons, in weight order:

1. **License**: Supervisor-Skills is CC BY-NC-SA. Vendoring its content into a
   freely redistributed pack would impose NC terms on downstream users and
   require adaptations to be shared under the same license - both incompatible
   with how PEtFiSh packs are licensed (research-skill-pack is Apache-2.0).
2. **Evidence discipline**: PEtFiSh's research pack is built around traceable
   evidence chains (JSONL ledgers, claim-to-evidence mapping). The mentor
   layer had to speak that language: every card carries an explicit endorsement
   level and real citations, and cards are explicitly barred from acting as
   evidence.
3. **Different card sources**: upstream cards encode a supervisor's practice
   experience; PEtFiSh cards encode published methodology literature (Toulmin,
   Swales CARS, Gopen & Swan, Sandve's reproducibility rules, Sandberg &
   Alvesson's problematization critique) plus marked internal practice. The
   two card sets are complementary - which is exactly why the comparison mode
   exists rather than a replacement claim.

---

## Tracking upstream changes

Watch both repos for: new skills (the 12-skill list grows), license
clarifications, and Ducktor card additions. When upstream adds a capability
that maps to a real PEtFiSh gap (e.g. the figure-designer slot), file an issue
in the PEtFiSh repo proposing an original implementation - do not submit
upstream content anywhere, and do not direct upstream work from PEtFiSh
issues.
