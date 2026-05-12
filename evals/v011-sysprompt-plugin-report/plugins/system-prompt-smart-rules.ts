/**
 * system-prompt-smart-rules — Topic-Aware Rules Injection Plugin
 *
 * Uses fish-trail's active_topic to inject ONLY matching agents-rules
 * into the system prompt. Maps topic tags/title to rule files.
 *
 * Falls back to no injection if no topic is active or no rules match.
 */

import type { Plugin } from "@opencode-ai/plugin"
import { readFile, readdir } from "node:fs/promises"
import { join } from "node:path"

const RULES_DIR = ".opencode/agents-rules"
const FISH_TRAIL_DIR = ".petfish/fish-trail"

interface TopicRegistry {
  active_topic: string | null
  topics: Record<string, { title: string; status: string }>
}

interface TopicData {
  title: string
  scope?: string
  tags?: string[]
}

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
  research: ["research.md"],
}

function matchRuleFiles(topic: TopicData): Set<string> {
  const matched = new Set<string>()
  const searchText = [
    topic.title,
    topic.scope ?? "",
    ...(topic.tags ?? []),
  ]
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

const plugin: Plugin = async ({ directory }) => {
  const rulesDir = join(directory, RULES_DIR)

  const rulesCache = new Map<string, string>()
  try {
    const files = await readdir(rulesDir)
    for (const file of files.filter((f) => f.endsWith(".md"))) {
      try {
        const content = await readFile(join(rulesDir, file), "utf-8")
        rulesCache.set(
          file,
          `<!-- agents-rules/${file} -->\n${content.trim()}\n<!-- /agents-rules/${file} -->`,
        )
      } catch {
        // skip
      }
    }
  } catch {
    // no rules dir
  }

  if (rulesCache.size === 0) {
    return { name: "system-prompt-smart-rules" }
  }

  return {
    name: "system-prompt-smart-rules",

    "experimental.chat.system.transform": async (_input, output) => {
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
    },
  }
}

export default plugin
