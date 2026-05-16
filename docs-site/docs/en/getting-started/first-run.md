# First Run

After [installing](installation.md) PEtFiSh and restarting your AI assistant, here's what to expect.

## 1. Initialize Your Project

Run the `/initproject` command in your AI assistant:

```
/initproject
```

The wizard will ask about your project type and install matching packs. For example, choosing `code` installs `deploy`, `petfish`, and `testdocs`.

## 2. The Companion Gateway Is Now Active

You don't need to do anything to enable it. The Companion Gateway runs automatically before every message. Behind the scenes, it:

1. **Reads your project mode** — checks `depth` (urgent/balanced/thorough) and `rigor` (on/off)
2. **Checks topic context** — detects if your message drifts from the current topic
3. **Scans for failures** — looks for errors from the previous turn
4. **Senses capability gaps** — recommends packs if your request needs skills you don't have
5. **Guards against sycophancy** — pauses before blindly agreeing with evaluative questions

You'll only see Gateway output when it has something useful to say (medium/high risk, or a recommendation). To see every decision, enable [debug mode](../guides/companion-gateway/index.md#debug-mode).

## 3. Try `/petfish`

The `/petfish` command is your main entry point. Try these:

| Command | What it does |
|---|---|
| `/petfish` | Show installed packs and skill status |
| `/petfish catalog` | Browse all available packs and skills |
| `/petfish suggest` | Get pack recommendations based on your project |
| `/petfish search <keyword>` | Search for skills across external marketplaces |

## 4. Start Working

Just work normally. PEtFiSh operates in the background:

- If you mention "deployment" but don't have the `deploy` pack → PEtFiSh recommends it
- If you ask "is this architecture good?" → the anti-sycophancy check kicks in before the agent agrees
- If the previous turn failed to read a PDF → PEtFiSh suggests the `ppt` pack
- If you switch topics mid-conversation → PEtFiSh flags the context drift

## 5. Optional: Configure Project Mode

Create `.opencode/project-mode.yaml` to tune PEtFiSh's behavior:

```yaml
depth: balanced       # urgent | balanced | thorough
rigor: false          # true | false
```

- **`depth: urgent`** — quick fixes, workarounds OK, minimal search
- **`depth: balanced`** — normal workflow (default)
- **`depth: thorough`** — root cause analysis, multi-source verification, forces `rigor: true`
- **`rigor: true`** — formal plans for complex tasks, reviewed before implementation

You can also switch modes mid-session by saying "urgent", "thorough", or "rigor" — no file changes needed.

## What's Next

- [Companion Gateway guide](../guides/companion-gateway/index.md) — deep dive into each Gateway step
- [/petfish commands](../guides/petfish-commands/index.md) — full command reference
- [Skill packs reference](../reference/packs/index.md) — browse all 12 packs and 96 skills
