/**
 * topic-context-filter — Per-Request Context Filtering Plugin
 *
 * Filters non-active-topic messages from the LLM context window via
 * `experimental.chat.messages.transform`. Targets ≥30% input token reduction
 * for multi-topic sessions while guaranteeing zero modification for single-topic ones.
 *
 * Safety invariants:
 *   - Last N messages ALWAYS kept (safety window)
 *   - tool_use/tool_result pairs NEVER split
 *   - Single-topic sessions: no messages removed
 *   - Short conversations (<minMessages): skip entirely
 *   - Any failure: return unmodified (never throw)
 *
 * Config via opencode.json plugin tuple:
 *   "plugin": [[ ".opencode/plugin/topic-context-filter.ts", { "enabled": true, "safetyWindow": 3, "minMessages": 10 } ]]
 */

import type { Plugin } from "@opencode-ai/plugin"
import { readFile, stat } from "node:fs/promises"
import { join } from "node:path"

interface TopicRegistry {
  active_topic: string | null
  topics: Record<string, { title: string; status: string }>
}

interface TopicData {
  title: string
  scope?: string
  tags?: string[]
  summary?: string
}

interface PluginOptions {
  enabled?: boolean
  safetyWindow?: number
  minMessages?: number
}

interface MessagePart {
  type: string
  text?: string
  [key: string]: unknown
}

interface MessageInfo {
  role: string
  [key: string]: unknown
}

interface PluginMessage {
  info: MessageInfo
  parts: MessagePart[]
}

const FISH_TRAIL_DIR = ".petfish/fish-trail"

// Topic domain keywords — reuses same structure as system-prompt-rules.ts TOPIC_TO_RULES
const DOMAIN_KEYWORDS: Record<string, string[]> = {
  course: ["course", "课程", "教学", "大纲", "实验", "lesson", "curriculum", "syllabus", "lab", "learner", "instructor"],
  deploy: ["deploy", "部署", "docker", "container", "systemd", "nginx", "ci/cd", "rollback", "回滚", "运维", "ops"],
  writing: ["润色", "说人话", "去ai味", "rewrite", "polish", "style", "风格"],
  petfish: ["petfish", "skill", "companion", "pack", "install", "marketplace"],
  review: ["review", "评审", "critique", "calibration", "sycophancy", "评价"],
  topic: ["topic", "话题", "上下文", "context", "污染", "contamination", "fish-trail"],
  research: ["research", "研究", "调研", "文献", "evidence", "综述", "论文", "literature", "synthesis"],
  database: ["database", "数据库", "postgres", "mysql", "migration", "schema", "sql", "query", "table"],
  auth: ["auth", "认证", "login", "jwt", "token", "session", "oauth", "password", "credential"],
  frontend: ["frontend", "前端", "react", "vue", "css", "component", "ui", "ux", "layout", "style"],
  testing: ["test", "测试", "jest", "vitest", "pytest", "coverage", "mock", "fixture", "assertion"],
}

function buildKeywordSet(topic: TopicData): Set<string> {
  const keywords = new Set<string>()

  // Extract keywords from topic title, scope, tags, summary
  const text = [topic.title, topic.scope ?? "", topic.summary ?? "", ...(topic.tags ?? [])].join(" ").toLowerCase()

  // Add direct tags
  for (const tag of topic.tags ?? []) {
    keywords.add(tag.toLowerCase())
  }

  // Add words from title (split on spaces and common separators)
  for (const word of topic.title.toLowerCase().split(/[\s\-_/]+/)) {
    if (word.length > 2) keywords.add(word)
  }

  // Match against domain keywords to find relevant domain and add all its keywords
  for (const [_domain, domainWords] of Object.entries(DOMAIN_KEYWORDS)) {
    if (domainWords.some((w) => text.includes(w))) {
      for (const w of domainWords) keywords.add(w)
    }
  }

  return keywords
}

function getMessageText(msg: PluginMessage): string {
  return msg.parts
    .filter((p) => p.type === "text" && p.text)
    .map((p) => p.text ?? "")
    .join(" ")
    .toLowerCase()
}

function scoreMessage(text: string, keywords: Set<string>): number {
  let score = 0
  for (const kw of keywords) {
    if (text.includes(kw)) score++
  }
  return score
}

function getMatchedDomains(text: string): Set<string> {
  const domains = new Set<string>()
  for (const [domain, words] of Object.entries(DOMAIN_KEYWORDS)) {
    if (words.some((w) => text.includes(w))) {
      domains.add(domain)
    }
  }
  return domains
}

async function readJSON<T>(path: string): Promise<T | null> {
  try {
    return JSON.parse(await readFile(path, "utf-8")) as T
  } catch {
    return null
  }
}

const plugin: Plugin = async ({ directory }, options) => {
  const opts = (options ?? {}) as PluginOptions
  const enabled = opts.enabled !== false
  const safetyWindow = opts.safetyWindow ?? 3
  const minMessages = opts.minMessages ?? 10

  if (!enabled) {
    return { name: "topic-context-filter" }
  }

  // Cache topic registry path
  const registryPath = join(directory, FISH_TRAIL_DIR, "topic-registry.json")
  let cachedRegistry: TopicRegistry | null = null
  let cachedRegistryMtime = 0

  async function getRegistry(): Promise<TopicRegistry | null> {
    try {
      const s = await stat(registryPath)
      const mtime = s.mtimeMs
      if (mtime === cachedRegistryMtime && cachedRegistry) {
        return cachedRegistry
      }
      cachedRegistry = await readJSON<TopicRegistry>(registryPath)
      cachedRegistryMtime = mtime
      return cachedRegistry
    } catch {
      return null
    }
  }

  return {
    name: "topic-context-filter",

    "experimental.chat.messages.transform": async (_input, output) => {
      try {
        const messages = output.messages as PluginMessage[]

        // Short conversation guard
        if (messages.length < minMessages) return

        // Read active topic
        const registry = await getRegistry()
        if (!registry?.active_topic) return

        // Read topic data
        const topicPath = join(directory, FISH_TRAIL_DIR, "topics", `${registry.active_topic}.json`)
        const topic = await readJSON<TopicData>(topicPath)
        if (!topic?.title) return

        // Build keyword set for active topic
        const keywords = buildKeywordSet(topic)
        if (keywords.size === 0) return

        // Score all messages (except safety window)
        const safetyStart = Math.max(0, messages.length - safetyWindow)
        const scores: number[] = new Array(messages.length).fill(0)
        const allMatchedDomains = new Set<string>()

        for (let i = 0; i < safetyStart; i++) {
          const text = getMessageText(messages[i])
          scores[i] = scoreMessage(text, keywords)

          // Track domains for single-topic guard
          if (scores[i] > 0) {
            // This message hits our active topic keywords — not "off-topic"
          } else {
            // Check if it hits OTHER topic domains
            const domains = getMatchedDomains(text)
            for (const d of domains) allMatchedDomains.add(d)
          }
        }

        // Single-topic guard: if no OTHER topic domains detected, return early
        if (allMatchedDomains.size <= 1) return

        // Count how many messages would be removed
        let removeCount = 0
        for (let i = 0; i < safetyStart; i++) {
          if (scores[i] === 0) removeCount++
        }

        // Low-yield guard: if <20% would be removed, skip
        if (removeCount / messages.length < 0.2) return

        // Build keep/remove map, respecting tool_use/tool_result pairs
        const keep = new Array<boolean>(messages.length).fill(false)

        // Safety window always kept
        for (let i = safetyStart; i < messages.length; i++) {
          keep[i] = true
        }

        // Mark scored messages
        for (let i = 0; i < safetyStart; i++) {
          if (scores[i] > 0) keep[i] = true
        }

        // Ensure tool_use/tool_result pairs stay together
        for (let i = 0; i < messages.length; i++) {
          if (!keep[i]) continue
          const msg = messages[i]
          // If this is a tool_use, keep next message (tool_result)
          if (msg.parts.some((p) => p.type === "tool_use" || p.type === "tool-use")) {
            if (i + 1 < messages.length) keep[i + 1] = true
          }
          // If this is a tool_result, keep previous message (tool_use)
          if (msg.parts.some((p) => p.type === "tool_result" || p.type === "tool-result")) {
            if (i - 1 >= 0) keep[i - 1] = true
          }
        }

        // Also: if a tool_result is kept, its preceding tool_use must be kept
        for (let i = 1; i < messages.length; i++) {
          if (keep[i] && messages[i].info.role === "tool") {
            keep[i - 1] = true
          }
        }

        // Build filtered array: collapse consecutive removed messages into placeholder
        const filtered: PluginMessage[] = []
        let removedRun = 0

        for (let i = 0; i < messages.length; i++) {
          if (keep[i]) {
            // Flush any pending removed run
            if (removedRun > 0) {
              filtered.push({
                info: { role: "assistant" },
                parts: [{ type: "text", text: `[${removedRun} messages from other topics omitted]` }],
              })
              removedRun = 0
            }
            filtered.push(messages[i])
          } else {
            removedRun++
          }
        }

        // Flush trailing removed run (shouldn't happen due to safety window, but just in case)
        if (removedRun > 0) {
          filtered.push({
            info: { role: "assistant" },
            parts: [{ type: "text", text: `[${removedRun} messages from other topics omitted]` }],
          })
        }

        // Only splice if we actually reduced messages
        if (filtered.length < messages.length) {
          output.messages.splice(0, output.messages.length, ...filtered)
        }
      } catch (e) {
        // Graceful degradation: never throw, never break the session
        console.warn("[topic-context-filter] Error during filtering, returning unmodified:", e)
      }
    },
  }
}

export default plugin
