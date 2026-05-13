/**
 * system-prompt-all-rules — Full Rules Injection Plugin
 *
 * Injects ALL agents-rules files into the system prompt via
 * `experimental.chat.system.transform`. This moves rule content from
 * conversation context (uncached, accumulates per turn) into the system
 * prompt (cached by provider, paid once).
 *
 * Trade-off: System prompt grows by ~13K tokens (back to v0.10.x size),
 * but enjoys prompt caching instead of per-turn re-transmission.
 *
 * Usage: Place in .opencode/plugin/ and it auto-loads.
 */

import type { Plugin } from "@opencode-ai/plugin"
import { readFile, readdir } from "node:fs/promises"
import { join } from "node:path"

const RULES_DIR = ".opencode/agents-rules"

async function loadAllRules(directory: string): Promise<string[]> {
  const rulesDir = join(directory, RULES_DIR)
  const rules: string[] = []

  try {
    const files = await readdir(rulesDir)
    const mdFiles = files.filter((f) => f.endsWith(".md")).sort()

    for (const file of mdFiles) {
      try {
        const content = await readFile(join(rulesDir, file), "utf-8")
        rules.push(
          `<!-- agents-rules/${file} -->\n${content.trim()}\n<!-- /agents-rules/${file} -->`,
        )
      } catch {
        // Skip unreadable files
      }
    }
  } catch {
    // agents-rules dir doesn't exist — no-op
  }

  return rules
}

const plugin: Plugin = async ({ directory }) => {
  // Pre-load all rules at plugin init (they don't change during session)
  const allRules = await loadAllRules(directory)

  if (allRules.length === 0) {
    return { name: "system-prompt-all-rules" }
  }

  const injectedContent = [
    "## Pack-Specific Rules (Injected by Plugin)",
    "",
    "The following rules are authoritative for their respective domains.",
    "",
    ...allRules,
  ].join("\n")

  return {
    name: "system-prompt-all-rules",

    "experimental.chat.system.transform": async (_input, output) => {
      output.system.push(injectedContent)
    },
  }
}

export default plugin
