/**
 * system-prompt-context-inject - Topic State Injection Plugin
 *
 * Reads topic state from .petfish/fish-trail/ and injects it into the
 * cached system prompt prefix, eliminating per-turn MCP tool calls.
 *
 * Dual-mode detection:
 *   - "disk" (default): reads previous turn's state from disk only.
 *     Zero-turn overhead, zero mis-detection risk, one-turn delay.
 *   - "realtime": also runs Tier 1 detection on the user message.
 *     Zero-turn delay, ~5-8% token overhead, catches explicit switches.
 *
 * Active topic resolution (fallback order):
 *   1. topic-registry.json.active_topic  (v1 layout)
 *   2. topic_graph.json.active_topic     (v2 layout)
 *   3. Most recent active topic from topic_graph.json.topics
 *
 * Tier 2 (semantic/embedding) detection is NOT included here.
 * It stays MCP-side as the `topic_detect` tool with embedding support.
 * See #150 for rationale.
 *
 * Bun transpiler note:
 *   Do NOT use (x || "").method() - Bun/JSC miscompiles method calls on
 *   || fallback expressions. Always assign to variable first.
 *
 * Config via opencode.json plugin tuple:
 *   ["path/to/plugin", { "maxTopics": 5, "maxSummaryLen": 200, "detectionMode": "disk" }]
 *   ["path/to/plugin", { "maxTopics": 5, "maxSummaryLen": 200, "detectionMode": "realtime" }]
 */

import type { Plugin } from "@opencode-ai/plugin"
import { readFile, readdir } from "node:fs/promises"
import { join } from "node:path"
import { TopicDetector } from "./topic-detector"

const FISH_TRAIL_DIR = ".petfish/fish-trail"

interface PluginOptions {
  maxTopics?: number
  maxSummaryLen?: number
  detectionMode?: "disk" | "realtime"  // default: "disk"
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

// Singleton detector for realtime mode (lazy-initialized)
let _detector: TopicDetector | null = null
function getDetector(): TopicDetector {
  if (!_detector) {
    _detector = new TopicDetector()
  }
  return _detector
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

  if (graph.active_topic) {
    return graph.active_topic
  }

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
  const registry = await readJSON<TopicRegistry>(join(fishTrailDir, "topic-registry.json"))
  if (registry && registry.topics && Object.keys(registry.topics).length > 0) {
    return { active_topic: activeTopicId, topics: registry.topics }
  }

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

function formatDetectionMeta(result: {
  relation: string
  confidence: number
  risk: number
  risk_level: string
  target_topic: string | null
}): string {
  const lines: string[] = [
    "- **Realtime detection**:",
    "  - Relation: " + result.relation,
    "  - Confidence: " + result.confidence.toFixed(2),
    "  - Risk: " + result.risk + " (" + result.risk_level + ")",
  ]
  if (result.target_topic) {
    lines.push("  - Target: " + result.target_topic)
  }
  if (result.relation === "switch" || result.relation === "fork") {
    lines.push(
      "  - If this is an unintended topic shift, consider using MCP `topic_detect` " +
      "for deeper analysis or `topic_create`/`topic_link` to formalize the split.",
    )
  }
  return lines.join("\n")
}

function formatTopicContext(
  registryView: { active_topic: string; topics: Record<string, { title: string; status: string }> },
  activeTopic: TopicData | null,
  graph: TopicGraph | null,
  detectionResult: { relation: string; confidence: number; risk: number; risk_level: string; target_topic: string | null } | null,
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

  // Realtime detection metadata (if enabled and available)
  if (detectionResult && opts.detectionMode === "realtime") {
    lines.push("")
    lines.push(formatDetectionMeta(detectionResult))
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
  lines.push("Topic context above is automatically injected by plugin " +
    "(" + opts.detectionMode + " mode). " +
    "Do NOT call topic_detect or get_memory_context for routine turns. " +
    "MCP tools (topic_list, topic_create, session_bind, topic_detect with semantic=True) " +
    "are available ONLY for user-initiated topic management or deep analysis.")

  return lines.join("\n")
}

/**
 * Extract the last user message from the OpenCode hook input.
 * #157: OpenCode exposes messages via input.messages (array), not input.content.
 * Falls back to input.content if messages array is not available.
 * Supports both string content and part-array content formats.
 */
async function extractUserMessage(input: unknown): Promise<string> {
  if (!input || typeof input !== "object") return ""

  const obj = input as Record<string, unknown>

  // Path 1: input.messages array (OpenCode system transform hook)
  if (Array.isArray(obj.messages)) {
    // Iterate backward to find the last user message
    for (let i = obj.messages.length - 1; i >= 0; i--) {
      const msg = obj.messages[i]
      if (msg && typeof msg === "object" && (msg as Record<string, unknown>).role === "user") {
        const content = (msg as Record<string, unknown>).content
        // String content
        if (typeof content === "string") return content
        // Part-array content: [{ type: "text", text: "..." }, ...]
        if (Array.isArray(content)) {
          const textParts = content
            .filter(function(part) { return part && typeof part === "object" && (part as Record<string, unknown>).type === "text" })
            .map(function(part) { return String((part as Record<string, unknown>).text || "") })
          return textParts.join("\n")
        }
      }
    }
    return ""
  }

  // Path 2: input.content (direct content, some hook implementations)
  if ("content" in obj) {
    const content = obj.content
    if (typeof content === "string") return content
    if (Array.isArray(content)) {
      const textParts = content
        .filter(function(part) { return part && typeof part === "object" && (part as Record<string, unknown>).type === "text" })
        .map(function(part) { return String((part as Record<string, unknown>).text || "") })
      return textParts.join("\n")
    }
  }

  return ""
}

const plugin: Plugin = async ({ directory }, options) => {
  const rawOpts = (options as Record<string, unknown>) || {}
  const pluginOpts: Required<PluginOptions> = {
    maxTopics: (rawOpts.maxTopics as number) ?? 5,
    maxSummaryLen: (rawOpts.maxSummaryLen as number) ?? 200,
    detectionMode: (rawOpts.detectionMode as "disk" | "realtime") ?? "disk",
  }

  return {
    name: "system-prompt-context-inject",

    "experimental.chat.system.transform": async (input, output) => {
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
        // #156: Only use exact filename match. 8-char prefix is not unique
        // (e.g. topic_20260523_5dfe and topic_20260523_01f8 both start with "topic_20").
        // If exact match fails, scan file contents by "id" field as secondary fallback.
        let matchFile = topicFiles.find(function(f) {
          return f === activeTopicId + ".json"
        })
        if (!matchFile) {
          // Secondary: match by "id" field inside each JSON file
          for (const f of topicFiles) {
            if (!f.endsWith(".json")) continue
            const data = await readJSON<TopicData & { id?: string }>(join(fishTrailDir, "topics", f))
            if (data && data.id === activeTopicId) {
              matchFile = f
              break
            }
          }
        }
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

      // Realtime detection (if enabled)
      let detectionResult: { relation: string; confidence: number; risk: number; risk_level: string; target_topic: string | null } | null = null
      if (pluginOpts.detectionMode === "realtime") {
        // #157: Extract user message robustly.
        // OpenCode hook exposes messages via input.messages, not input.content.
        // 1. If input.messages exists, find the last user message
        // 2. Else if input.content exists, use it directly
        // 3. Support both string and part-array content formats
        const userMsg = await extractUserMessage(input)

        if (userMsg && userMsg.length > 0) {
          try {
            // Build currentTopic and allTopics for detector
            const currentTopicForDetect = activeTopic
              ? { id: activeTopicId, title: activeTopic.title || "", scope: activeTopic.scope || "", tags: activeTopic.tags || [] }
              : null

            const allTopicsForDetect = Object.entries(registryView.topics).map(function(entry) {
              return { id: entry[0], title: entry[1].title, scope: "", tags: [] as string[] }
            })

            detectionResult = getDetector().detect(userMsg, currentTopicForDetect, allTopicsForDetect)
          } catch (e) {
            // Detection failure must not break injection
            console.log("[system-prompt-context-inject] Realtime detection failed: " + String(e))
          }
        }
      }

      // Format and inject
      const contextBlock = formatTopicContext(registryView, activeTopic, graph, detectionResult, pluginOpts)
      output.system.push(contextBlock)

      const relatedCount = Object.keys(registryView.topics).length - 1
      const modeTag = pluginOpts.detectionMode === "realtime" ? "realtime" : "disk"
      console.log(
        "[system-prompt-context-inject] Injected topic context (" + modeTag + " mode): " +
        "active=" + activeTopicId + ", related=" + relatedCount,
      )
    },
  }
}

export default plugin
