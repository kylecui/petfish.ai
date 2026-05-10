/**
 * fish-trail-compaction — Phase 1 (Topic-Aware Context Injection)
 *
 * Injects the active topic's Context Package into OpenCode's compaction flow
 * via `output.context[]`. This gives the LLM summarizer topic awareness so it
 * can prioritize the current topic and compress unrelated topics more aggressively.
 *
 * Strategy: Pure augmentation — we append to context[], never replace the
 * default compaction prompt. Low risk, ~15% token savings expected.
 *
 * Data flow:
 *   .petfish/fish-trail/topic-registry.json → active_topic
 *   .petfish/fish-trail/topics/<id>.json    → title, scope, summary, tags
 */

import type { Plugin } from "@opencode-ai/plugin"
import { readFile } from "node:fs/promises"
import { join } from "node:path"

interface TopicRegistry {
  version: number
  active_topic: string | null
  topics: Record<string, { title: string; status: string }>
  links: unknown[]
}

interface TopicData {
  id: string
  title: string
  scope?: string
  summary?: string
  tags?: string[]
  status?: string
  parent?: string | null
  metadata?: Record<string, unknown>
}

const FISH_TRAIL_DIR = ".petfish/fish-trail"

async function readJSON<T>(path: string): Promise<T | null> {
  try {
    const raw = await readFile(path, "utf-8")
    return JSON.parse(raw) as T
  } catch {
    return null
  }
}

function buildContextPackage(topic: TopicData): string {
  const lines: string[] = [
    `## Active Topic: ${topic.title}`,
  ]

  if (topic.scope) {
    lines.push(`**Scope**: ${topic.scope}`)
  }
  if (topic.summary) {
    lines.push(`**Summary**: ${topic.summary}`)
  }
  if (topic.tags?.length) {
    lines.push(`**Tags**: ${topic.tags.join(", ")}`)
  }

  lines.push(
    "",
    "When summarizing conversation history, prioritize content related to this topic.",
    "Other topics may be compressed more aggressively.",
  )

  return lines.join("\n")
}

const plugin: Plugin = async ({ directory }) => ({
  name: "fish-trail-compaction",

  "experimental.session.compacting": async (_input, output) => {
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

    const contextPkg = buildContextPackage(topic)
    output.context.push(contextPkg)
  },
})

export default plugin
