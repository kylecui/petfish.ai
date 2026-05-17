# URL Scheme

## Base URL

- Custom domain: `https://docs.petfish.ai/`
- Legacy URL: `https://kylecui.github.io/petfish.ai/` (auto-redirects to custom domain)

## Language Routing

| Locale | URL prefix | Notes |
|--------|-----------|-------|
| English (default) | `/` | Served from `docs/en/` |
| Chinese | `/zh/` | Served from `docs/zh/` |

The `mkdocs-static-i18n` plugin with `fallback_to_default: true` means any missing
`zh/` page falls back to the English version automatically.

## URL Structure

```
/                                  → Home (en)
/zh/                               → Home (zh)

/getting-started/                  → Getting Started (en)
/zh/getting-started/               → Getting Started (zh)

/guides/                           → Guides index (en)
/zh/guides/                        → Guides index (zh)
/guides/companion-gateway/         → Companion Gateway guide (en)
/zh/guides/companion-gateway/      → Companion Gateway guide (zh)

/reference/                        → Reference index (en)
/zh/reference/                     → Reference index (zh)
/reference/packs/                  → Pack catalog (en)
/zh/reference/packs/               → Pack catalog (zh)
/reference/packs/companion/        → companion pack page (en)
/zh/reference/packs/companion/     → companion pack page (zh)
/reference/skills/                 → Skill catalog (en)
/zh/reference/skills/              → Skill catalog (zh)
/reference/skills/petfish-companion/ → skill page (en)
/zh/reference/skills/petfish-companion/ → skill page (zh)

/developer/                        → Developer docs (en)
/zh/developer/                     → Developer docs (zh)

/technical/                        → Technical papers (en)
/zh/technical/                     → Technical papers (zh)

/changelog/                        → Changelog (en)
/zh/changelog/                     → Changelog (zh)
```

## Auto-Generated Pages

The `generate_skill_reference.py` script produces:

- `reference/packs/index.md` — pack catalog table
- `reference/packs/<alias>.md` — one page per pack (12 packs)
- `reference/skills/index.md` — skill catalog table
- `reference/skills/<name>.md` — one page per skill (96 skills)

All generated in both `en/` and `zh/` directories.

## Nav Integration

Auto-generated pack and skill pages need to be added to `mkdocs.yml` nav.
The current nav uses index pages only; individual pack/skill pages are
discovered by MkDocs navigation auto-discovery within the directory.
