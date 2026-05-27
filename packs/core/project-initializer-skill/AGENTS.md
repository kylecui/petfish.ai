<!-- BEGIN pack: project-initializer-skill -->
# Project Initializer Skill Pack Rules

This pack provides workspace scaffolding and initialization capabilities for AI-agent projects.

## Skill Routing (强制)

### Rules

1. When the user asks to initialize, scaffold, bootstrap, or set up a new AI-agent workspace, **MUST** route to `project-initializer`.
2. When the user asks to generate `AGENTS.md`, `README`, `.opencode/` templates, `docs/`, `tasks/`, `qa/`, or `mcp` config files, **MUST** route to `project-initializer`.
3. When the user selects or asks about a profile (minimal / course / code / ops / security / research / writing / skills-package / comprehensive), **MUST** route to `project-initializer`.
4. When the user asks to configure a `uv` dev environment for a new project, **MUST** route to `project-initializer`.
5. **Safe no-overwrite rule**: `project-initializer` must check for existing files before writing. For any file that already exists, it must ask for explicit confirmation before overwriting. Never silently overwrite.

### Conflict Resolution

- If the user asks to "update" or "modify" an existing `AGENTS.md` rather than initialize from scratch, do NOT route to `project-initializer` — handle as a direct edit task.
- If the user asks to initialize AND install packs, route initialization to `project-initializer` first, then route pack installation to `petfish-companion`.

## Profiles

| Profile | Included Templates |
|---|---|
| minimal | AGENTS.md, README |
| course | + docs/, course structure, QA/QC templates |
| code | + tasks/, .opencode/agents/, dev env |
| ops | + deploy config, runbook templates |
| security | + security policy, threat model stubs |
| research | + research/, evidence/, sources/ stubs |
| writing | + docs/, style guide stub |
| skills-package | + packs/, skill scaffold, lint config |
| comprehensive | all of the above |

## Behavioral Rules

- Always confirm the target directory and profile before writing any files.
- List all files that will be created before creating them (dry-run summary).
- For risky operations (overwrite existing files, delete, restructure), require explicit user confirmation.
- After scaffolding, output a post-init summary: files created, next steps, recommended pack installs.
- Do not create `README.md` files unless the profile explicitly includes them or the user requests them.

## Output Format

Post-init output must include:

1. **Files Created** — list of paths written
2. **Skipped / Conflicts** — files that already existed and were not overwritten
3. **Next Steps** — recommended commands (e.g., `/petfish install <pack>`, `uv sync`)
4. **Profile Summary** — what the selected profile provides
<!-- END pack: project-initializer-skill -->
