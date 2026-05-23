/**
 * system-prompt-context-inject — Topic State Injection Plugin
 *
 * Reads topic state from `.petfish/fish-trail/` and injects it into the
 * cached system prompt prefix, eliminating the need for per-turn MCP tool
 * calls (topic_detect, get_memory_context) for routine topic awareness.
 *
 * Design rationale:
 *   - Reasoning models (DeepSeek V4, o1/o3, etc.) do not reliably call MCP
 *     tools proactively, even when instructed to do so per-turn.
 *   - Plugin injection into system prompt is cached (cheap); MCP tool call
 *     results enter uncached conversation context (expensive).
 *   - P1 evaluation: plugin-inject reduces tokens -8.1%, output -31.1%,
 *     contamination +11pp vs rules+MCP approach.
 *
 * One-turn delay:
 *   The plugin reads from disk (previous turn's state written by MCP server).
 *   Turn 1 (cold start): no injection. Turn 2+: previous state available.
 *   Quality evaluation (N=18) shows no degradation from this delay.
 *
 * Config via opencode.json plugin tuple:
 *   "plugin": [[ ".opencode/plugin/system-prompt-context-inject.ts", { "maxTopics": 5, "maxSummaryLen": 200 } ]]
 */

import type { Plugin } from "@opencode-ai/plugin"
import { readFile, readdir } from "node:fs/promises"
import { join } from "node:path"

const FISH_TRAIL_DIR = ".petfish/fish-trail"

interface PluginOptions {
  maxTopics?: number     // max related topics to inject (default: 5)
  maxSummaryLen?: number // truncate topic summaries (default: 200 chars)
}

interface TopicRegistry {
  active_topic: string | null
  topics: Record<string, { title: string; status: string }>
}

interface TopicData {
  title: string
  scope?: string
  tags?: string[]
  summary?: string
  status?: string
}

interface TopicGraph {
  topics: Record<string, {
    title: string
    status: string
    summary?: string
    scope?: string
  }>
  edges?: Array<{ source: string; target: string; relation: string }>
}

async function readJSON<T>(path: string): Promise<T | null> {
  try {
    return JSON.parse(await readFile(path, "utf-8")) as T
  } catch {
    return null
  }
}

function truncate(text: string, maxLen: number): string {
  if (!text || text.length <= maxLen) return text ?? ""
  return text.slice(0, maxLen - 3) + "..."
}

function formatTopicContext(
  registry: TopicRegistry,
  activeTopic: TopicData | null,
  graph: TopicGraph | null,
  opts: Required<PluginOptions>,
): string {
  const lines: string[] = [
    "## Active Topic Context (auto-injected by plugin)",
    "",
  ]

  // Active topic
  if (registry.active_topic && activeTopic) {
    const status = activeTopic.status ?? "active"
    lines.push(`- **Current topic**: ${registry.active_topic} — ${activeTopic.title} (${status})`)
    if (activeTopic.scope) {
      lines.push(`  - Scope: ${truncate(activeTopic.scope, opts.maxSummaryLen)}`)
    }
    if (activeTopic.summary) {
      lines.push(`  - Summary: ${truncate(activeTopic.summary, opts.maxSummaryLen)}`)
    }
  } else {
    lines.push("- No active topic detected")
  }

  // Related topics from registry
  const relatedTopics = Object.entries(registry.topics)
    .filter(([id]) => id !== registry.active_topic)
    .filter(([, data]) => data.status === "active" || data.status === "warm")
    .slice(0, opts.maxTopics)

  if (relatedTopics.length > 0) {
    lines.push("")
    lines.push("- **Related topics**:")
    for (const [id, data] of relatedTopics) {
      lines.push(`  - ${id} — ${data.title} (${data.status})`)
    }
  }

  // Topic graph edges for active topic (if available)
  if (graph?.edges && registry.active_topic) {
    const activeEdges = graph.edges
      .filter(e => e.source === registry.active_topic || e.target === registry.active_topic)
      .slice(0, 3)
    if (activeEdges.length > 0) {
      lines.push("")
      lines.push("- **Topic relations**:")
      for (const edge of activeEdges) {
        const other = edge.source === registry.active_topic ? edge.target : edge.source
        lines.push(`  - ${other} (${edge.relation})`)
      }
    }
  }

  // Critical instruction: do NOT call topic_detect/get_memory_context routinely
  lines.push("")
  lines.push("Topic context above is automatically injected by plugin. " +
    "Do NOT call `topic_detect` or `get_memory_context` for routine turns. " +
    "MCP tools (`topic_list`, `topic_create`, `session_bind`, etc.) are available " +
    "ONLY for user-initiated topic management actions.")

  return lines.join("\n")
}

const plugin: Plugin = async ({ directory }, options) => {
  const opts = (options as Record<string, unknown>) ?? {}
  const pluginOpts: Required<PluginOptions> = {
    maxTopics: (opts.maxTopics as number) ?? 5,
    maxSummaryLen: (opts.maxSummaryLen as number) ?? 200,
  }

  return {
    name: "system-prompt-context-inject",

    "experimental.chat.system.transform": async (_input, output) => {
      const fishTrailDir = join(directory, FISH_TRAIL_DIR)

      // Read topic registry
      const registry = await readJSON<TopicRegistry>(
        join(fishTrailDir, "topic-registry.json"),
      )
      if (!registry?.active_topic) {
        console.log(
          "[system-prompt-context-inject] No active topic found in registry " +
          "(cold start or no topics created yet). Skipping injection.",
        )
        return
      }

      // Read active topic data
      let activeTopic: TopicData | null = null
      try {
        const topicFiles = await readdir(join(fishTrailDir, "topics"))
        const matchFile = topicFiles.find(f =>
          f === `${registry.active_topic}.json` ||
          f.startsWith(registry.active_topic!.slice(0, 8)),
        )
        if (matchFile) {
          activeTopic = await readJSON<TopicData>(
            join(fishTrailDir, "topics", matchFile),
          )
        }
      } catch {
        // topics dir doesn't exist yet
        console.log(
          "[system-prompt-context-inject] topics/ directory not found. " +
          "Injection will contain topic ID only.",
        )
      }

      // Read topic graph (optional, for relations)
      const graph = await readJSON<TopicGraph>(
        join(fishTrailDir, "topic_graph.json"),
      )

      // Format and inject
      const contextBlock = formatTopicContext(registry, activeTopic, graph, pluginOpts)
      output.system.push(contextBlock)
      console.log(
        `[system-prompt-context-inject] Injected topic context: ` +
        `active=${registry.active_topic}, related=${Object.keys(registry.topics).length - 1}`,
      )
    },
  }
}

export default plugin
