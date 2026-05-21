/**
 * system-prompt-rules — Unified Rules Injection Plugin
 *
 * Injects agents-rules files into the system prompt via
 * `experimental.chat.system.transform`. This moves rule content from
 * conversation context (uncached, accumulates per turn) into the system
 * prompt (cached by provider, paid once).
 *
 * Modes:
 *   "all"   — Inject ALL agents-rules files. Simple, best at current scale (~9K tokens).
 *   "smart" — Topic-aware: inject only rules matching the active fish-trail topic.
 *   "auto"  — Use "all", but advise switching to "smart" when rules exceed 30K tokens.
 *
 * Config via opencode.json plugin tuple:
 *   "plugin": [[ ".opencode/plugin/system-prompt-rules.ts", { "mode": "all" } ]]
 *
 * Default mode: "all"
 */

import type { Plugin } from "@opencode-ai/plugin"
import { readFile, readdir } from "node:fs/promises"
import { join } from "node:path"

type Mode = "all" | "smart" | "auto"

const RULES_DIR = ".opencode/agents-rules"
const FISH_TRAIL_DIR = ".petfish/fish-trail"
const AUTO_THRESHOLD_TOKENS = 30_000

// CJK regex: CJK Unified Ideographs, Extension A, Hangul, Hiragana/Katakana
const CJK_RE = /[\u4e00-\u9fff\u3400-\u4dbf\uac00-\ud7af\u3040-\u30ff]/g

/**
 * Estimate chars-per-token based on CJK content ratio.
 * Pure English ≈ 4 chars/token; pure CJK ≈ 1 char/token.
 */
function estimateCharsPerToken(text: string): number {
  if (text.length === 0) return 4
  const cjkCount = (text.match(CJK_RE) ?? []).length
  const ratio = cjkCount / text.length
  return Math.max(1, Math.min(4, 4 - 3 * ratio))
}

interface TopicRegistry {
  active_topic: string | null
  topics: Record<string, { title: string; status: string }>
}

interface TopicData {
  title: string
  scope?: string
  tags?: string[]
}

// Maps topic keywords → rule file names for smart mode
const TOPIC_TO_RULES: Record<string, string[]> = {
  course: ["course-skills.md"],
  deploy: ["deploy-ops.md"],
  ops: ["deploy-ops.md"],
  writing: ["petfish-style.md"],
  style: ["petfish-style.md"],
  petfish: ["petfish-companion.md"],
  skill: ["petfish-companion.md"],
  review: ["anti-sycophancy.md"],
  calibration: ["anti-sycophancy.md"],
  topic: ["fish-trail.md"],
  context: ["fish-trail.md"],
  safety: ["safety-guard.md"],
  guard: ["safety-guard.md"],
  security: ["safety-guard.md"],
  research: ["research.md"],
}

function matchRuleFiles(topic: TopicData): Set<string> {
  const matched = new Set<string>()
  const searchText = [topic.title, topic.scope ?? "", ...(topic.tags ?? [])]
    .join(" ")
    .toLowerCase()

  for (const [keyword, files] of Object.entries(TOPIC_TO_RULES)) {
    if (searchText.includes(keyword)) {
      for (const f of files) matched.add(f)
    }
  }

  return matched
}

async function readJSON<T>(path: string): Promise<T | null> {
  try {
    return JSON.parse(await readFile(path, "utf-8")) as T
  } catch {
    return null
  }
}

async function injectSmartRules(
  directory: string,
  rulesCache: Map<string, string>,
  output: { system: string[] },
): Promise<void> {
  const registryPath = join(directory, FISH_TRAIL_DIR, "topic-registry.json")
  const registry = await readJSON<TopicRegistry>(registryPath)
  if (!registry?.active_topic) return

  const topicPath = join(
    directory,
    FISH_TRAIL_DIR,
    "topics",
    `${registry.active_topic}.json`,
  )
  const topic = await readJSON<TopicData>(topicPath)
  if (!topic?.title) return

  const matched = matchRuleFiles(topic)
  if (matched.size === 0) return

  const sections: string[] = [
    `## Pack-Specific Rules (Smart-injected for topic: ${topic.title})`,
    "",
  ]

  for (const file of matched) {
    const content = rulesCache.get(file)
    if (content) sections.push(content)
  }

  output.system.push(sections.join("\n"))
}

const plugin: Plugin = async ({ directory }, options) => {
  const opts = (options as Record<string, unknown>) ?? {}
  const mode: Mode = (opts.mode as Mode) ?? "all"
  const autoFallback: boolean = (opts.autoFallback as boolean) ?? false

  // Pre-load and cache all rule files at init (they don't change during session)
  const rulesCache = new Map<string, string>()
  const rulesDir = join(directory, RULES_DIR)

  try {
    const files = await readdir(rulesDir)
    for (const file of files.filter((f) => f.endsWith(".md")).sort()) {
      try {
        const content = await readFile(join(rulesDir, file), "utf-8")
        rulesCache.set(
          file,
          `<!-- agents-rules/${file} -->\n${content.trim()}\n<!-- /agents-rules/${file} -->`,
        )
      } catch {
        // Skip unreadable files
      }
    }
  } catch {
    // agents-rules dir doesn't exist — no-op
  }

  if (rulesCache.size === 0) {
    return { name: "system-prompt-rules" }
  }

  // Pre-compute the "all rules" injection block
  const allRulesContent = [
    "## Pack-Specific Rules (Injected by Plugin)",
    "",
    "The following rules are authoritative for their respective domains.",
    "",
    ...[...rulesCache.values()],
  ].join("\n")

  // Estimate total token count (CJK-aware) for auto mode advisory
  const totalChars = allRulesContent.length
  const charsPerToken = estimateCharsPerToken(allRulesContent)
  const estimatedTokens = Math.ceil(totalChars / charsPerToken)
  let autoAdvisoryLogged = false

  return {
    name: "system-prompt-rules",

    "experimental.chat.system.transform": async (_input, output) => {
      if (mode === "smart") {
        // Smart mode: inject only rules matching active topic
        await injectSmartRules(directory, rulesCache, output)
        return
      }

      // Auto mode with fallback: switch to smart when threshold exceeded
      if (mode === "auto" && autoFallback && estimatedTokens > AUTO_THRESHOLD_TOKENS) {
        if (!autoAdvisoryLogged) {
          autoAdvisoryLogged = true
          console.warn(
            `[system-prompt-rules] Auto fallback: rules total ~${estimatedTokens} tokens ` +
            `(threshold: ${AUTO_THRESHOLD_TOKENS}). Switching to smart mode.`,
          )
        }
        await injectSmartRules(directory, rulesCache, output)
        return
      }

      // "all" and "auto" (no fallback) modes: inject everything
      output.system.push(allRulesContent)

      // Auto mode advisory: warn once when rules exceed threshold
      if (mode === "auto" && !autoAdvisoryLogged && estimatedTokens > AUTO_THRESHOLD_TOKENS) {
        autoAdvisoryLogged = true
        console.warn(
          `[system-prompt-rules] Auto advisory: rules total ~${estimatedTokens} tokens ` +
          `(threshold: ${AUTO_THRESHOLD_TOKENS}). Consider switching to "smart" mode ` +
          `in opencode.json: [".opencode/plugin/system-prompt-rules.ts", {"mode":"smart"}]`,
        )
      }
    },
  }
}

export default plugin
