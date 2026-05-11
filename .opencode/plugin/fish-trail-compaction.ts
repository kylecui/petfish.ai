/**
 * fish-trail-compaction — Phase 2 (Topic-Structured Prompt Replacement)
 *
 * Replaces OpenCode's default compaction prompt with a topic-aware version
 * via `output.prompt`. This organizes the summary by topic, preserves the
 * active topic in full detail, and aggressively compresses inactive topics.
 *
 * When output.prompt is set, it completely replaces the default buildPrompt()
 * which combines anchor text + SUMMARY_TEMPLATE + context[]. This gives us
 * ~60% token savings by eliminating redundant cross-topic information.
 *
 * Fallback: If fish-trail data is unavailable, does nothing — OpenCode's
 * default compaction runs unmodified.
 *
 * Data flow:
 *   .petfish/fish-trail/topic-registry.json → active_topic + all topics
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

/**
 * Load all topic data files for topics listed in the registry.
 */
async function loadAllTopics(
  directory: string,
  registry: TopicRegistry,
): Promise<TopicData[]> {
  const topicIds = Object.keys(registry.topics)
  const results = await Promise.all(
    topicIds.map((id) =>
      readJSON<TopicData>(
        join(directory, FISH_TRAIL_DIR, "topics", `${id}.json`),
      ),
    ),
  )
  return results.filter((t): t is TopicData => t !== null && !!t.title)
}

/**
 * Build the topic-structured compaction prompt.
 *
 * This replaces OpenCode's default SUMMARY_TEMPLATE + anchor logic with a
 * prompt that:
 * 1. Organizes output by topic (active topic gets full detail)
 * 2. Instructs aggressive compression of inactive topics
 * 3. Preserves the same output structure (Markdown) for downstream compat
 * 4. Includes anchor/update logic using the active topic's summary
 */
function buildTopicStructuredPrompt(
  activeTopic: TopicData,
  allTopics: TopicData[],
): string {
  const inactiveTopics = allTopics.filter((t) => t.id !== activeTopic.id)

  // Build the known-topics context block
  const topicContext: string[] = [
    "## Known Topics",
    "",
    `### ACTIVE: ${activeTopic.title}`,
  ]
  if (activeTopic.scope) {
    topicContext.push(`Scope: ${activeTopic.scope}`)
  }
  if (activeTopic.summary) {
    topicContext.push(`Prior summary: ${activeTopic.summary}`)
  }
  if (activeTopic.tags?.length) {
    topicContext.push(`Tags: ${activeTopic.tags.join(", ")}`)
  }

  if (inactiveTopics.length > 0) {
    topicContext.push("")
    topicContext.push("### Other topics (compress aggressively):")
    for (const t of inactiveTopics) {
      topicContext.push(`- ${t.title}${t.scope ? ` — ${t.scope}` : ""}`)
    }
  }

  const prompt = `You are compacting a conversation that spans multiple topics. Produce a topic-organized summary.

${topicContext.join("\n")}

---

Produce exactly the Markdown structure below. Do not include the <template> tags.

<template>
## Active Topic: ${activeTopic.title}

### Goal
- [single-sentence goal for this topic]

### Progress
- [completed work, in-progress items, blockers — terse bullets]

### Key Decisions
- [decision and why, or "(none)"]

### Critical Context
- [technical facts, errors, open questions specific to this topic]

### Relevant Files
- [file path: why it matters]

### Next Steps
- [ordered next actions]

## Other Topics
${inactiveTopics.length > 0 ? inactiveTopics.map((t) => `### ${t.title}\n- [1-2 bullet summary of work done, or "(none)"]`).join("\n\n") : "- (none)"}

## User Constraints & Preferences
- [user constraints, preferences, specs across all topics, or "(none)"]

## Delegated Agent Sessions
- [agent type, purpose, session_id — only if referenced in conversation]
</template>

Rules:
- The ACTIVE topic section must capture ALL relevant details from the conversation — goals, progress, decisions, files, next steps.
- Other topic sections: maximum 2 bullets each. Drop details that are not needed to resume work.
- Preserve exact file paths, commands, error strings, identifiers, and session IDs.
- Use terse bullets, not prose paragraphs.
- Do not mention the summary process or that context was compacted.
- Keep every section, even when empty — use "(none)".`

  return prompt
}

const plugin: Plugin = async ({ directory }) => ({
  name: "fish-trail-compaction",

  "experimental.session.compacting": async (_input, output) => {
    const registryPath = join(directory, FISH_TRAIL_DIR, "topic-registry.json")
    const registry = await readJSON<TopicRegistry>(registryPath)

    if (!registry?.active_topic) return

    const allTopics = await loadAllTopics(directory, registry)
    const activeTopic = allTopics.find((t) => t.id === registry.active_topic)

    if (!activeTopic) return

    // Phase 2: Replace the entire compaction prompt
    output.prompt = buildTopicStructuredPrompt(activeTopic, allTopics)
  },
})

export default plugin
