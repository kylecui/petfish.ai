/**
 * system-prompt-context-inject - Topic State Injection Plugin
 *
 * Reads topic state from .petfish/fish-trail/ and injects it into the
 * cached system prompt prefix, eliminating per-turn MCP tool calls.
 *
 * Active topic resolution (fallback order):
 *   1. topic-registry.json.active_topic  (v1 layout)
 *   2. topic_graph.json.active_topic     (v2 layout)
 *   3. Most recent active topic from topic_graph.json.topics
 *
 * Bun transpiler note:
 *   Do NOT use (x || "").method() - Bun/JSC miscompiles method calls on
 *   || fallback expressions. Always assign to variable first.
 *
 * Config via opencode.json plugin tuple:
 *   "plugin": [[ ".opencode/plugin/system-prompt-context-inject.ts", { "maxTopics": 5, "maxSummaryLen": 200 } ]]
 */

import type { Plugin } from "@opencode-ai/plugin"
import { readFile, readdir } from "node:fs/promises"
import { join } from "node:path"

const FISH_TRAIL_DIR = ".petfish/fish-trail"

interface PluginOptions {
  maxTopics?: number
  maxSummaryLen?: number
}

interface TopicRegistry {
  active_topic: string | null
  version?: string
  topics: Record<string, { title: string; status: string }>
}

interface TopicData {
  title: string
  scope?: string
  tags?: string[]
  summary?: string
  status?: string
}

interface TopicGraphNode {
  title: string
  status: string
  summary?: string
  scope?: string
  updated_at?: string
}

interface TopicGraph {
  active_topic?: string
  topics?: Record<string, TopicGraphNode>
  nodes?: Array<{ id: string; title: string; status: string; updated_at?: string }>
  edges?: Array<{ source: string; target: string; relation: string }>
}

async function readJSON<T>(path: string): Promise<T | null> {
  try {
    const raw = await readFile(path, "utf-8")
    return JSON.parse(raw) as T
  } catch {
    return null
  }
}

function truncate(text: string | undefined | null, maxLen: number): string {
  if (!text) return ""
  if (text.length <= maxLen) return text
  return text.slice(0, maxLen - 3) + "..."
}

async function resolveActiveTopic(fishTrailDir: string): Promise<string | null> {
  // 1. topic-registry.json.active_topic (v1 layout)
  const registry = await readJSON<TopicRegistry>(join(fishTrailDir, "topic-registry.json"))
  if (registry && registry.active_topic) {
    return registry.active_topic
  }

  // 2-3. topic_graph.json (v2 layout)
  const graph = await readJSON<TopicGraph>(join(fishTrailDir, "topic_graph.json"))
  if (!graph) return null

  // Check graph-level active_topic
  if (graph.active_topic) {
    return graph.active_topic
  }

  // Find most recent active topic from topics dict
  if (graph.topics) {
    const activeEntries = Object.entries(graph.topics)
      .filter(function(entry) { return entry[1].status === "active" })
      .sort(function(a, b) {
        const aTime = a[1].updated_at || ""
        const bTime = b[1].updated_at || ""
        return bTime.localeCompare(aTime)
      })
    if (activeEntries.length > 0) {
      return activeEntries[0][0]
    }
  }

  // Try nodes array shape
  if (graph.nodes) {
    const activeNodes = graph.nodes
      .filter(function(n) { return n.status === "active" })
      .sort(function(a, b) {
        const aTime = a.updated_at || ""
        const bTime = b.updated_at || ""
        return bTime.localeCompare(aTime)
      })
    if (activeNodes.length > 0) {
      return activeNodes[0].id
    }
  }

  return null
}

async function buildRegistryView(
  fishTrailDir: string,
  activeTopicId: string,
): Promise<{
  active_topic: string
  topics: Record<string, { title: string; status: string }>
}> {
  // Try v1 registry first
  const registry = await readJSON<TopicRegistry>(join(fishTrailDir, "topic-registry.json"))
  if (registry && registry.topics && Object.keys(registry.topics).length > 0) {
    return { active_topic: activeTopicId, topics: registry.topics }
  }

  // Fall back to graph
  const graph = await readJSON<TopicGraph>(join(fishTrailDir, "topic_graph.json"))
  const topics: Record<string, { title: string; status: string }> = {}

  if (graph && graph.topics) {
    for (const id of Object.keys(graph.topics)) {
      const node = graph.topics[id]
      topics[id] = { title: node.title, status: node.status }
    }
  } else if (graph && graph.nodes) {
    for (const node of graph.nodes) {
      topics[node.id] = { title: node.title, status: node.status }
    }
  }

  return { active_topic: activeTopicId, topics }
}

function formatTopicContext(
  registryView: { active_topic: string; topics: Record<string, { title: string; status: string }> },
  activeTopic: TopicData | null,
  graph: TopicGraph | null,
  opts: Required<PluginOptions>,
): string {
  const lines: string[] = [
    "## Active Topic Context (auto-injected by plugin)",
    "",
  ]

  if (activeTopic) {
    const status = activeTopic.status || "active"
    lines.push("- **Current topic**: " + registryView.active_topic + " - " + activeTopic.title + " (" + status + ")")
    if (activeTopic.scope) {
      const scopeStr = truncate(activeTopic.scope, opts.maxSummaryLen)
      lines.push("  - Scope: " + scopeStr)
    }
    if (activeTopic.summary) {
      const summaryStr = truncate(activeTopic.summary, opts.maxSummaryLen)
      lines.push("  - Summary: " + summaryStr)
    }
  } else {
    lines.push("- **Current topic**: " + registryView.active_topic + " (details not found on disk)")
  }

  // Related topics
  const relatedTopics = Object.entries(registryView.topics)
    .filter(function(entry) { return entry[0] !== registryView.active_topic })
    .filter(function(entry) { const s = entry[1].status; return s === "active" || s === "warm" })
    .slice(0, opts.maxTopics)

  if (relatedTopics.length > 0) {
    lines.push("")
    lines.push("- **Related topics**:")
    for (const item of relatedTopics) {
      lines.push("  - " + item[0] + " - " + item[1].title + " (" + item[1].status + ")")
    }
  }

  // Topic graph edges
  if (graph && graph.edges) {
    const activeEdges = graph.edges
      .filter(function(e) { return e.source === registryView.active_topic || e.target === registryView.active_topic })
      .slice(0, 3)
    if (activeEdges.length > 0) {
      lines.push("")
      lines.push("- **Topic relations**:")
      for (const edge of activeEdges) {
        const other = edge.source === registryView.active_topic ? edge.target : edge.source
        lines.push("  - " + other + " (" + edge.relation + ")")
      }
    }
  }

  lines.push("")
  lines.push("Topic context above is automatically injected by plugin. " +
    "Do NOT call topic_detect or get_memory_context for routine turns. " +
    "MCP tools (topic_list, topic_create, session_bind, etc.) are available " +
    "ONLY for user-initiated topic management actions.")

  return lines.join("\n")
}

const plugin: Plugin = async ({ directory }, options) => {
  const rawOpts = (options as Record<string, unknown>) || {}
  const pluginOpts: Required<PluginOptions> = {
    maxTopics: (rawOpts.maxTopics as number) ?? 5,
    maxSummaryLen: (rawOpts.maxSummaryLen as number) ?? 200,
  }

  return {
    name: "system-prompt-context-inject",

    "experimental.chat.system.transform": async (_input, output) => {
      const fishTrailDir = join(directory, FISH_TRAIL_DIR)

      // Resolve active topic with fallback chain
      const activeTopicId = await resolveActiveTopic(fishTrailDir)
      if (!activeTopicId) {
        console.log(
          "[system-prompt-context-inject] No active topic found in any state file " +
          "(cold start or no topics created yet). Skipping injection.",
        )
        return
      }

      // Build unified registry view
      const registryView = await buildRegistryView(fishTrailDir, activeTopicId)

      // Read active topic data
      let activeTopic: TopicData | null = null
      try {
        const topicFiles = await readdir(join(fishTrailDir, "topics"))
        const prefix = activeTopicId.slice(0, 8)
        const matchFile = topicFiles.find(function(f) {
          return f === activeTopicId + ".json" || f.startsWith(prefix)
        })
        if (matchFile) {
          activeTopic = await readJSON<TopicData>(join(fishTrailDir, "topics", matchFile))
        }
      } catch {
        console.log(
          "[system-prompt-context-inject] topics/ directory not found. " +
          "Injection will contain topic ID only.",
        )
      }

      // Read topic graph
      const graph = await readJSON<TopicGraph>(join(fishTrailDir, "topic_graph.json"))

      // Format and inject
      const contextBlock = formatTopicContext(registryView, activeTopic, graph, pluginOpts)
      output.system.push(contextBlock)

      const relatedCount = Object.keys(registryView.topics).length - 1
      console.log(
        "[system-prompt-context-inject] Injected topic context: " +
        "active=" + activeTopicId + ", related=" + relatedCount,
      )
    },
  }
}

export default plugin