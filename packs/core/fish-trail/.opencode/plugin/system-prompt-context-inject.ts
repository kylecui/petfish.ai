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
 * The TopicDetector class below was merged from lib/plugin/topic-detector.ts
 * (which is kept as canonical source but no longer installed to plugin dirs).
 * Tier 1 keyword + Jaccard + signal + bilingual + drift detection ported from
 * topic_detector.py. Tier 2 stays MCP-side for on-demand use only (#150).
 *
 * Bun transpiler note:
 *   Do NOT use (x || "").method() - Bun/JSC miscompiles method calls on
 *   || fallback expressions. Always assign to variable first.
 *   Use function() instead of arrow functions in .filter()/.sort()/.map()
 *   when they contain || comparisons with method calls.
 *
 * Config via opencode.json plugin tuple:
 *   ["path/to/plugin", { "maxTopics": 5, "maxSummaryLen": 200, "detectionMode": "disk" }]
 *   ["path/to/plugin", { "maxTopics": 5, "maxSummaryLen": 200, "detectionMode": "experimental.realtime" }]
 *   ["path/to/plugin", { "compressionLevel": "full" }]  // verbose for Flash-tier models
 *   ["path/to/plugin", { "reflectiveBriefEnabled": true }]   // v1.2: enable reflective brief compression
 *   ["path/to/plugin", { "adaptiveCompressionEnabled": true }]  // v1.2: enable adaptive compression
 *
 * v1.2 feature flags (default false):
 *   - reflectiveBriefEnabled: enables reflective brief compression
 *   - adaptiveCompressionEnabled: enables adaptive compression
 *
 * "disk" (default): reads previous turn's state from disk only. Zero overhead.
 * "experimental.realtime": requires patched OpenCode with lastUserMessage support (#163).
 *   Falls back to disk-mode if patch is absent. Not recommended — wait for upstream.
 *   See: https://github.com/anomalyco/opencode/pull/28993
 * Cold start: when no active topic exists, injects minimal guidance instead of skipping.
 */

import type { Plugin } from "@opencode-ai/plugin"
import { readFile, readdir, writeFile, mkdir, open, appendFile, stat, rename } from "node:fs/promises"
import { join } from "node:path"
import { execSync } from "node:child_process"

// ═══════════════════════════════════════════════════════════════════════════════
// Cache-stable Memory Blocks (#164) + Reflective Compression (#166)
// ═══════════════════════════════════════════════════════════════════════════════
//
// The plugin outputs 3 separate blocks to output.system, each with a
// different change frequency. DeepSeek V4 Pro uses automatic implicit prefix
// caching — by keeping stable blocks byte-identical across turns, the provider
// can reuse cached KV entries for the unchanged prefix.
//
// Block order (low→high change frequency):
//   1. Registry Block: topic list + status → changes on create/delete only
//   2. Warm Brief Block: related topic one-liners → changes on status transition
//   3. Active Focus Block: current topic + reflective brief + mode → every turn
//
// #166 Reflective Compression:
//   - Each block uses semantically dense compact notation instead of verbose labels
//   - Active Focus merges title+scope, replaces full summary with reflective brief
//   - Mode indicator compacted from ~15 tokens to ~5
//   - Cold-start block compressed from ~50 tokens to ~12
//   - Target: ~100-120 tokens per turn for Active Focus (down from ~260)
//
// Previous turn's block content is persisted to disk. On each turn, we compare
// current state with previous state and output byte-identical content for
// unchanged blocks (enabling prefix cache hits).

const INJECTED_STATE_FILENAME = "injected-block-state.json"

interface AdaptiveSwitch {
  ts: string
  from: string
  to: string
  round: number
}

interface AdaptiveState {
  mode: "compact" | "full" | "unknown"
  roundCounter: number
  cooldownUntil: number
  signalHistory: number[]
  roundsWithHighSignal: number
  roundsWithLowSignal: number
  switchHistory: AdaptiveSwitch[]
  unstable: boolean
  signalCold: boolean
}

interface BriefMetrics {
  total_topics: number
  topics_with_brief: number
  brief_hit_rate: number
  heuristic_ratio: number
  agent_reject_rate: number
  last_updated: string
}

interface InjectedBlockState {
  registryHash: string
  warmHash: string
  registryBlock: string
  warmBlock: string
  opencodeVersion: string
  adaptiveState?: AdaptiveState
  _brief_metrics?: BriefMetrics
}

/** Simple hash for detecting content changes without storing full content. */
function simpleHash(str: string): string {
  let h = 0
  for (let i = 0; i < str.length; i++) {
    const c = str.charCodeAt(i)
    h = ((h << 5) - h + c) | 0
  }
  return h.toString(36)
}

// ═══════════════════════════════════════════════════════════════════════════════
// Types (from lib/plugin/topic-detector.ts — internal, not exported)
// ═══════════════════════════════════════════════════════════════════════════════

interface TopicRef {
  id?: string
  title?: string
  scope?: string
  tags?: string[]
}

interface DetectResult {
  relation: "continue" | "fork" | "switch" | "merge" | "archive" | "reset" | "bridge"
  confidence: number
  risk: number
  risk_level: "low" | "medium" | "high"
  target_topic: string | null
  suggestion: string
}

type Relation = DetectResult["relation"]

interface RiskProfileEntry {
  risk: number
  risk_level: DetectResult["risk_level"]
}

interface OpenCodePatchState {
  /** OpenCode version when patch state was last recorded */
  opencodeVersion: string
  /** Whether the system.transform hook exposed lastUserMessage at this version */
  lastUserMessageAvailable: boolean
  /** ISO timestamp of last check */
  lastChecked: string
  /** If a patched binary was installed, which version */
  patchedBinaryVersion?: string
}

// ═══════════════════════════════════════════════════════════════════════════════
// OpenCode version tracking & auto-patch detection (#163)
// ═══════════════════════════════════════════════════════════════════════════════

const PATCH_STATE_FILENAME = "opencode-patch-state.json"
let _patchStateLogged = false

/**
 * Detect the currently installed OpenCode version.
 * Tries `opencode --version` first, then falls back to reading the binary.
 */
function getOpenCodeVersion(): string {
  try {
    const ver = execSync("opencode --version", { encoding: "utf-8", timeout: 5000 }).trim()
    return ver || "unknown"
  } catch {
    return "unknown"
  }
}

/**
 * Read previous patch state from disk. Returns null if never written.
 */
async function readPatchState(fishTrailDir: string): Promise<OpenCodePatchState | null> {
  try {
    const raw = await readFile(join(fishTrailDir, PATCH_STATE_FILENAME), "utf-8")
    return JSON.parse(raw) as OpenCodePatchState
  } catch {
    return null
  }
}

/**
 * Write current patch state to disk.
 */
async function writePatchState(fishTrailDir: string, state: OpenCodePatchState): Promise<void> {
  try {
    await mkdir(fishTrailDir, { recursive: true })
    await writeFile(
      join(fishTrailDir, PATCH_STATE_FILENAME),
      JSON.stringify(state, null, 2),
      "utf-8",
    )
  } catch (e) {
    // Non-critical — best effort
    _warn("Failed to write patch state: " + String(e))
  }
}

/**
 * Check OpenCode version change and auto-patch status.
 * Called once per session on first system.transform invocation.
 * Logs version changes and provides guidance for enabling realtime mode.
 */
async function checkAutoPatch(
  fishTrailDir: string,
  lastUserMessageAvailable: boolean,
): Promise<void> {
  if (_patchStateLogged) return
  _patchStateLogged = true

  const currentVersion = getOpenCodeVersion()
  const prevState = await readPatchState(fishTrailDir)

  const currentState: OpenCodePatchState = {
    opencodeVersion: currentVersion,
    lastUserMessageAvailable,
    lastChecked: new Date().toISOString(),
  }

  // Detect version change
  if (prevState && prevState.opencodeVersion !== currentVersion) {
    _warn(
      "OpenCode version changed: " +
      prevState.opencodeVersion + " -> " + currentVersion,
    )
    if (prevState.patchedBinaryVersion && !lastUserMessageAvailable) {
      _warn(
        "Patched OpenCode was replaced by upgrade. " +
        "Disk mode will continue to work. For realtime, see: " +
        "uv run scripts/patch_opencode.py --check",
      )
    }
  }

  // Guidance for users who want realtime mode
  if (!lastUserMessageAvailable && (!prevState || !prevState.lastUserMessageAvailable)) {
    _warn(
      "Disk mode is active (one-turn delay, zero overhead). " +
      "Realtime detection requires upstream OpenCode support — " +
      "follow PR https://github.com/anomalyco/opencode/pull/28993",
    )
  }

  // Persist state
  if (prevState) {
    currentState.patchedBinaryVersion = prevState.patchedBinaryVersion
  }
  await writePatchState(fishTrailDir, currentState)
}

// ═══════════════════════════════════════════════════════════════════════════════
// Helper functions (from lib/plugin/topic-detector.ts)
// ═══════════════════════════════════════════════════════════════════════════════

function isCJK(char: string): boolean {
  return char >= "\u4e00" && char <= "\u9fff"
}

function containsCJK(text: string): boolean {
  for (let i = 0; i < text.length; i++) {
    if (isCJK(text[i])) return true
  }
  return false
}

// Regex for splitting on non-word, non-CJK characters.
// Created fresh each use to avoid lastIndex issues with global regex.
function splitTokens(text: string): string[] {
  return text.split(/[^\w\u4e00-\u9fff]+/u)
}

/**
 * Insert a space between Latin/digit characters and CJK characters so that
 * tokenization produces clean boundaries.  E.g. "Webhook挂载" → "Webhook 挂载".
 */
function normalizeCJKBoundaries(text: string): string {
  // Latin/digit followed by CJK
  let result = text.replace(/([a-z0-9])([\u4e00-\u9fff])/giu, "$1 $2")
  // CJK followed by Latin/digit
  result = result.replace(/([\u4e00-\u9fff])([a-z0-9])/giu, "$1 $2")
  return result
}

// ═══════════════════════════════════════════════════════════════════════════════
// TopicDetector class (from lib/plugin/topic-detector.ts — internal singleton)
// ═══════════════════════════════════════════════════════════════════════════════

class TopicDetector {
  // ── Bilingual mapping (Chinese → English) ──────────────────────────────────
  readonly bilingualMap: Record<string, string> = {
    "测试": "test",
    "验证": "verification",
    "验收": "acceptance",
    "升级": "upgrade",
    "部署": "deploy",
    "安装": "install",
    "开发": "development",
    "发布": "release",
    "修复": "fix",
    "问题": "issue",
    "功能": "feature",
    "配置": "config",
    "脚本": "script",
    "文档": "documentation",
    "检查": "check",
    "审计": "audit",
    "质量": "quality",
    "门禁": "gate",
    "评分": "score",
    "风险": "risk",
    "话题": "topic",
    "上下文": "context",
    "污染": "contamination",
    "隔离": "isolation",
    "感知": "detection",
    "能力": "capability",
    "技能": "skill",
    "伙伴": "companion",
    "课程": "course",
    "实验": "lab",
    "提纲": "outline",
    "正文": "content",
    "平台": "platform",
    "命令": "command",
    "服务": "service",
    "重启": "restart",
    "改动": "change",
    "生效": "effective",
    "回归": "regression",
    "覆盖": "coverage",
    "断言": "assertion",
    "用例": "test case",
    "冒烟": "smoke test",
  }

  // ── Synonym / equivalence groups ───────────────────────────────────────────
  readonly synonymGroups: ReadonlyArray<ReadonlySet<string>> = [
    new Set([
      "test", "testing", "qa", "verification", "check", "validate",
      "acceptance", "regression", "smoke test", "assertion", "test case", "coverage",
    ]),
    new Set(["companion", "petfish", "gateway"]),
    new Set(["topic", "context", "fish-trail", "drift", "detection"]),
    new Set(["deploy", "deployment", "ci", "cd"]),
    new Set(["skill", "pack", "capability"]),
    new Set(["mcp", "server", "service", "tool"]),
    new Set(["install", "setup", "init"]),
    new Set(["upgrade", "update", "migration", "change", "effective"]),
  ]

  // ── Signal phrase lists ────────────────────────────────────────────────────
  readonly resetSignals: readonly string[] = [
    "重新开始", "忘掉前面", "清空上下文", "从头来", "全部重来",
    "start over", "fresh start", "reset context", "forget everything", "clean slate",
    "forget all", "forget it all", "forget it", "clear everything", "clear all",
    "wipe", "erase everything", "start fresh", "start clean", "new conversation",
    "brand new", "from scratch", "blank slate", "tabula rasa",
  ]

  readonly archiveSignals: readonly string[] = [
    "做完了", "可以关了", "结束这个", "这个话题完成", "归档",
    "done with this", "close this", "archive", "finished", "wrap up",
  ]

  readonly switchSignals: readonly string[] = [
    "回到", "继续之前的", "切换到", "转到",
    "go back to", "switch to", "return to", "continue with",
  ]

  readonly mergeSignals: readonly string[] = [
    "合并", "合到一起", "合在一起", "整合",
    "merge", "combine", "consolidate", "bring together",
  ]

  readonly forkSignals: readonly string[] = [
    "另外", "顺便", "额外", "分出来", "单独处理", "岔开一下", "分叉", "子话题",
    "by the way", "also", "separately", "side task", "branch off",
    "quick tangent", "fork", "split off", "spin off", "subtopic",
  ]

  readonly bridgeSignals: readonly string[] = [
    "关联", "桥接", "交叉引用", "这两个有关系",
    "relate", "bridge", "cross-reference", "these are related",
  ]

  // ── Stopwords ──────────────────────────────────────────────────────────────
  readonly stopwords: ReadonlySet<string> = new Set([
    // English
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by",
    "for", "from", "how", "i", "in", "into", "is", "it", "its",
    "me", "my", "of", "on", "or", "our", "please",
    "that", "the", "their", "them", "then", "there", "these", "they",
    "this", "those", "to", "us", "we", "with", "you", "your",
    // Chinese
    "的", "了", "和", "与", "并", "是", "在", "把", "将", "对",
    "为", "用", "到", "从", "上", "下", "中", "这", "那",
    "一个", "一些", "这个", "那个", "我们", "你们", "他们",
    "以及", "然后", "现在",
  ])

  // ── Risk profile ───────────────────────────────────────────────────────────
  readonly riskProfile: Record<Relation, RiskProfileEntry> = {
    "continue": { risk: 0, risk_level: "low" },
    "fork": { risk: 30, risk_level: "low" },
    "switch": { risk: 40, risk_level: "medium" },
    "merge": { risk: 50, risk_level: "medium" },
    "archive": { risk: 10, risk_level: "low" },
    "reset": { risk: 40, risk_level: "medium" },
    "bridge": { risk: 35, risk_level: "medium" },
  }

  /** Minimum Jaccard overlap to consider a fuzzy switch. */
  readonly minFuzzySwitchOverlap: number = 0.4

  // ── Public API ─────────────────────────────────────────────────────────────

  /**
   * Detect the relation between a new message and existing topics.
   *
   * @param text          User input text
   * @param currentTopic  Currently active topic (null if none)
   * @param allTopics     All known topics in the graph
   */
  detect(
    text: string,
    currentTopic: TopicRef | null,
    allTopics: TopicRef[],
  ): DetectResult {
    const rawText = text || ""
    const normalizedText = rawText.trim()
    const loweredText = normalizedText.toLowerCase()
    const keywords = this.extractKeywords(normalizedText)
    const currentTopicId = currentTopic ? (currentTopic.id || null) : null

    // 1. Reset signals — highest priority
    if (this.containsAny(loweredText, this.resetSignals)) {
      return this.buildResult({
        relation: "reset",
        confidence: 0.95,
        targetTopic: null,
        suggestion: "Start a fresh topic with empty context and do not inherit earlier discussion.",
      })
    }

    // 2. Archive signals
    if (this.containsAny(loweredText, this.archiveSignals)) {
      return this.buildResult({
        relation: "archive",
        confidence: 0.80,
        targetTopic: null,
        suggestion: this.archiveSuggestion(currentTopic),
      })
    }

    // 3. Switch target detection
    const switchTarget = this.findBestSwitchTarget(
      normalizedText,
      keywords,
      allTopics || [],
      currentTopicId,
    )
    const explicitSwitch = this.containsAny(loweredText, this.switchSignals)

    if (switchTarget && (
      explicitSwitch ||
      this.topicExplicitlyReferenced(loweredText, keywords, switchTarget)
    )) {
      return this.buildResult({
        relation: "switch",
        confidence: 0.85,
        targetTopic: switchTarget.id || null,
        suggestion: this.switchSuggestion(switchTarget, false),
      })
    }

    // 4. Fuzzy switch (high keyword overlap but no explicit signal)
    if (switchTarget) {
      const overlap = this.calculateTopicOverlap(keywords, switchTarget)
      if (overlap >= this.minFuzzySwitchOverlap) {
        return this.buildResult({
          relation: "switch",
          confidence: 0.60,
          targetTopic: switchTarget.id || null,
          suggestion: this.switchSuggestion(switchTarget, true),
        })
      }
    }

    // 5. Merge signals
    if (this.containsAny(loweredText, this.mergeSignals)) {
      return this.buildResult({
        relation: "merge",
        confidence: 0.70,
        targetTopic: null,
        suggestion: "This may require merging topics. Confirm before combining contexts.",
      })
    }

    // 6. Fork signals
    if (this.containsAny(loweredText, this.forkSignals)) {
      return this.buildResult({
        relation: "fork",
        confidence: 0.80,
        targetTopic: null,
        suggestion: this.forkSuggestion(currentTopic),
      })
    }

    // 7. Bridge signals
    if (this.containsAny(loweredText, this.bridgeSignals)) {
      return this.buildResult({
        relation: "bridge",
        confidence: 0.60,
        targetTopic: null,
        suggestion: "These topics seem related. Confirm whether to create a bridge instead of merging them.",
      })
    }

    // 8. Semantic drift detection
    if (currentTopic && keywords.size > 0) {
      const driftResult = this.checkSemanticDrift(normalizedText, keywords, currentTopic)
      if (driftResult) {
        return driftResult
      }
    }

    // 9. Default: continue
    return this.buildResult({
      relation: "continue",
      confidence: 0.90,
      targetTopic: null,
      suggestion: this.continueSuggestion(currentTopic),
    })
  }

  // ── Keyword extraction ─────────────────────────────────────────────────────

  /**
   * Split text into lowercase keywords, remove stopwords, and expand CJK
   * tokens into unigrams and bigrams.
   */
  extractKeywords(text: string): Set<string> {
    const raw = text || ""
    let normalized = raw.toLowerCase()
    normalized = normalizeCJKBoundaries(normalized)

    const tokens = splitTokens(normalized)
    const keywords = new Set<string>()

    for (const token of tokens) {
      const stripped = token.replace(/^_+|_+$/g, "") // strip leading/trailing underscores
      if (!stripped) continue
      if (this.stopwords.has(stripped)) continue
      if (/^\d+$/.test(stripped)) continue
      // Skip single ASCII characters (typically noise)
      if (stripped.length === 1 && stripped.charCodeAt(0) < 128) continue
      keywords.add(stripped)
    }

    // Expand CJK tokens into unigrams + bigrams
    for (const kw of Array.from(keywords)) {
      let hasCJK = false
      for (let i = 0; i < kw.length; i++) {
        if (isCJK(kw[i])) { hasCJK = true; break }
      }
      if (hasCJK) {
        this.addCJKKeywords(kw, keywords)
      }
    }

    return keywords
  }

  /**
   * For a CJK-containing token, add individual CJK characters (unigrams)
   * and adjacent CJK pairs (bigrams) to the keyword set.
   */
  private addCJKKeywords(token: string, keywords: Set<string>): void {
    // Extract CJK-only run
    let cjkOnly = ""
    for (let i = 0; i < token.length; i++) {
      if (isCJK(token[i])) cjkOnly += token[i]
    }
    if (!cjkOnly) return

    // Add individual CJK characters
    for (let i = 0; i < cjkOnly.length; i++) {
      const ch = cjkOnly[i]
      if (!this.stopwords.has(ch)) {
        keywords.add(ch)
      }
    }

    // Add bigrams
    if (cjkOnly.length >= 2) {
      for (let i = 0; i < cjkOnly.length - 1; i++) {
        const bigram = cjkOnly.slice(i, i + 2)
        if (!this.stopwords.has(bigram)) {
          keywords.add(bigram)
        }
      }
    }
  }

  // ── Overlap / switch targeting ─────────────────────────────────────────────

  /**
   * Calculate Jaccard similarity between message keywords and a topic's
   * title + scope keywords.
   */
  calculateTopicOverlap(keywords: Set<string>, topic: TopicRef): number {
    const title = topic.title || ""
    const scope = topic.scope || ""
    const topicText = title + " " + scope
    const topicKeywords = this.extractKeywords(topicText)

    if (keywords.size === 0 || topicKeywords.size === 0) return 0.0

    const unionSize = new Set([...keywords, ...topicKeywords]).size
    if (unionSize === 0) return 0.0

    let intersection = 0
    for (const kw of keywords) {
      if (topicKeywords.has(kw)) intersection++
    }
    return intersection / unionSize
  }

  /**
   * Find the best existing topic candidate for a switch.
   * Excludes the current topic and scores by keyword overlap +
   * explicit reference boost.
   */
  findBestSwitchTarget(
    _text: string,
    keywords: Set<string>,
    allTopics: TopicRef[],
    currentTopicId: string | null,
  ): TopicRef | null {
    const rawText = _text || ""
    const loweredText = rawText.toLowerCase()

    let bestTopic: TopicRef | null = null
    let bestScore = 0.0

    for (const topic of (allTopics || [])) {
      const topicId = topic.id || null
      if (currentTopicId !== null && topicId === currentTopicId) continue

      const overlap = this.calculateTopicOverlap(keywords, topic)
      let score = overlap

      if (this.topicExplicitlyReferenced(loweredText, keywords, topic)) {
        score = Math.max(score, 1.0)
      }

      if (score > bestScore) {
        bestScore = score
        bestTopic = topic
      }
    }

    if (bestScore <= 0.0) return null
    return bestTopic
  }

  // ── Signal matching ────────────────────────────────────────────────────────

  /**
   * Check whether `text` contains any signal phrase.
   *
   * - Multi-word phrases and CJK phrases are matched as substrings.
   * - Single-word non-CJK phrases are matched as exact tokens.
   */
  containsAny(text: string, phrases: readonly string[]): boolean {
    const raw = text || ""
    const loweredText = raw.toLowerCase()
    const rawTokens = new Set(
      splitTokens(loweredText).filter(function(t) { return t.length > 0 }),
    )

    for (const phrase of phrases) {
      const phraseLower = phrase.toLowerCase()
      const hasSpace = phraseLower.indexOf(" ") !== -1
      const hasCJK = containsCJK(phraseLower)

      if (hasSpace || hasCJK) {
        if (loweredText.indexOf(phraseLower) !== -1) return true
        continue
      }

      if (rawTokens.has(phraseLower)) return true
    }

    return false
  }

  /**
   * Check whether `loweredText` or its keywords explicitly reference the
   * given topic (by title or scope).
   */
  topicExplicitlyReferenced(
    loweredText: string,
    keywords: Set<string>,
    topic: TopicRef,
  ): boolean {
    const title = topic.title || ""
    const titleStr = String(title).trim()
    const scope = topic.scope || ""
    const scopeStr = String(scope).trim()

    if (titleStr) {
      const titleLower = titleStr.toLowerCase()

      // CJK title — substring match
      if (containsCJK(titleLower) && loweredText.indexOf(titleLower) !== -1) {
        return true
      }
      // Multi-word title — substring match
      if (titleLower.indexOf(" ") !== -1 && loweredText.indexOf(titleLower) !== -1) {
        return true
      }

      // Subset check: all title keywords present in input keywords
      const titleKeywords = this.extractKeywords(titleStr)
      if (titleKeywords.size > 0) {
        let allPresent = true
        for (const tk of titleKeywords) {
          if (!keywords.has(tk)) { allPresent = false; break }
        }
        if (allPresent) return true
      }
    }

    if (scopeStr) {
      const scopeLower = scopeStr.toLowerCase()
      if (containsCJK(scopeLower) && loweredText.indexOf(scopeLower) !== -1) {
        return true
      }
    }

    return false
  }

  // ── Bilingual expansion ────────────────────────────────────────────────────

  /**
   * Expand a keyword set with bilingual equivalents, synonym groups, and
   * simple English plural stemming.
   */
  expandBilingual(keywords: Set<string>): Set<string> {
    const expanded = new Set(keywords)

    for (const kw of Array.from(keywords)) {
      // Chinese → English (forward lookup)
      const enFromMap = this.bilingualMap[kw]
      if (enFromMap !== undefined) {
        expanded.add(enFromMap)
      }

      // English → Chinese (reverse lookup)
      for (const zh of Object.keys(this.bilingualMap)) {
        const en = this.bilingualMap[zh]
        if (kw === en || kw === en + "s" || kw + "s" === en) {
          expanded.add(zh)
          expanded.add(en)
        }
      }

      // Simple English plural stemming
      if (kw.endsWith("s") && kw.length > 3) {
        expanded.add(kw.slice(0, -1))
      }
      if (!kw.endsWith("s") && kw.length > 2) {
        expanded.add(kw + "s")
      }

      // Synonym group expansion
      for (const group of this.synonymGroups) {
        if (group.has(kw)) {
          for (const member of group) {
            expanded.add(member)
          }
          break
        }
      }
    }

    return expanded
  }

  // ── Semantic drift ─────────────────────────────────────────────────────────

  /**
   * Detect semantic drift by comparing message keywords to the current topic.
   *
   * Uses bilingual keyword expansion and meaningful-token filtering (len >= 2)
   * to handle cross-language scenarios.
   *
   * Tier 1: Keyword Jaccard (fast, <1ms).
   * Tier 2 (embedding) stays MCP-side — see #150.
   * When the ambiguous zone would consult embeddings, we fall through to the
   * zero/near-zero relevance fork result.
   */
  checkSemanticDrift(
    _text: string,
    keywords: Set<string>,
    currentTopic: TopicRef,
  ): DetectResult | null {
    // Build topic keyword set from title + scope + tags
    const title = currentTopic.title || ""
    const scope = currentTopic.scope || ""
    const rawTags = currentTopic.tags || []
  const tags = rawTags.join(" ")
    const topicText = title + " " + scope + " " + tags
    const topicKeywords = this.extractKeywords(topicText)

    // If current topic has no keywords (no title/scope/tags), skip drift check
    if (topicKeywords.size === 0) return null

    // Expand both sets with bilingual equivalents
    const expandedKeywords = this.expandBilingual(keywords)
    const expandedTopic = this.expandBilingual(topicKeywords)

    // Meaningful-token filter: only count tokens with len >= 2
    // This prevents CJK single-character inflation of the denominator
    const meaningfulInput = new Set<string>()
    for (const k of expandedKeywords) {
      if (k.length >= 2) meaningfulInput.add(k)
    }
    const meaningfulTopic = new Set<string>()
    for (const k of expandedTopic) {
      if (k.length >= 2) meaningfulTopic.add(k)
    }

    // Need enough meaningful input tokens for comparison
    if (meaningfulInput.size < 3) return null

    // Calculate relevance: intersection of meaningful tokens / input count
    let intersection = 0
    for (const k of meaningfulInput) {
      if (meaningfulTopic.has(k)) intersection++
    }
    const relevance = intersection / meaningfulInput.size

    // High relevance — clearly on-topic
    if (relevance >= 0.10) return null

    // Tier 2 (embedding) stays MCP-side - see #150
    // In the Python version, the ambiguous zone (relevance > 0.0) would
    // consult embeddings.  Since Tier 2 is intentionally excluded from
    // this port, we fall through to the zero/near-zero relevance handling.

    // Zero or near-zero relevance with meaningful keywords — likely drift
    const risk = relevance === 0.0 ? 45 : 35
    const confidence = relevance === 0.0 ? 0.65 : 0.55
    const topicTitle = this.topicTitle(currentTopic) || "current topic"

    return {
      relation: "fork",
      confidence: confidence,
      risk: risk,
      risk_level: "medium",
      target_topic: null,
      suggestion: 'This message appears unrelated to "' + topicTitle + '". ' +
        "Consider forking a new topic or confirming you want to continue.",
    }
  }

  // ── Suggestion helpers ─────────────────────────────────────────────────────

  private continueSuggestion(currentTopic: TopicRef | null): string {
    const title = this.topicTitle(currentTopic)
    if (title) {
      return 'Continue current topic "' + title + '".'
    }
    return "Continue in the current context."
  }

  private forkSuggestion(currentTopic: TopicRef | null): string {
    const title = this.topicTitle(currentTopic)
    if (title) {
      return 'Create a child topic from "' + title + '" and handle this as a side task.'
    }
    return "Create a separate topic for this side task."
  }

  private archiveSuggestion(currentTopic: TopicRef | null): string {
    const title = this.topicTitle(currentTopic)
    if (title) {
      return 'This sounds complete. Confirm archiving topic "' + title + '".'
    }
    return "This sounds complete. Confirm archiving the current topic."
  }

  private switchSuggestion(targetTopic: TopicRef, fuzzy: boolean): string {
    const title = this.topicTitle(targetTopic) || targetTopic.id || "target topic"
    if (fuzzy) {
      return 'This looks closer to existing topic "' + title + '"; consider switching to it.'
    }
    return 'Switch to existing topic "' + title + '" and load its context.'
  }

  // ── Utility ────────────────────────────────────────────────────────────────

  private buildResult(params: {
    relation: Relation
    confidence: number
    targetTopic: string | null
    suggestion: string
  }): DetectResult {
    const entry = this.riskProfile[params.relation]
    return {
      relation: params.relation,
      confidence: params.confidence,
      risk: entry.risk,
      risk_level: entry.risk_level,
      target_topic: params.targetTopic,
      suggestion: params.suggestion,
    }
  }

  private topicTitle(topic: TopicRef | null): string | null {
    if (!topic) return null
    const title = topic.title
    if (title === undefined || title === null) return null
    const s = String(title).trim()
    return s || null
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Plugin code
// ═══════════════════════════════════════════════════════════════════════════════

const FISH_TRAIL_DIR = ".petfish/fish-trail"

interface PluginOptions {
  maxTopics?: number
  maxSummaryLen?: number
  // "disk" (default): reads previous turn's topic state from disk. Zero overhead, one-turn delay.
  // "realtime": attempts per-turn detection. Requires upstream OpenCode support for
  //   lastUserMessage (see #163, PR: https://github.com/anomalyco/opencode/pull/28993).
  //   Falls back to disk-mode behavior if not available.
  // "experimental.realtime": same as "realtime" — use this in opencode.json to make the
  //   experimental status explicit.
  detectionMode?: "disk" | "realtime" | "experimental.realtime"
  // #166/#167: Compression level for injected topic context.
  //   "compact" (default): reflective brief + merged title/scope + compact mode indicator.
  //     Optimized for Pro-tier models (DeepSeek V4 Pro, Claude Sonnet) that attend well
  //     to semantic summaries. ~48 tokens for Active Focus block.
  //   "full": verbose labels + full summary text + detailed mode indicator.
  //     Better for Flash-tier models that may lose signal in compressed output. ~108 tokens.
  compressionLevel?: "compact" | "full"
  debug?: boolean
  // v1.2 feature flags — default false (off)
  reflectiveBriefEnabled?: boolean
  adaptiveCompressionEnabled?: boolean
}

const _PREFIX = "[system-prompt-context-inject] "
const _LOG_ROTATE_SIZE = 1_000_000 // 1MB
let _logDir = "" // set on first hook call

function _writeLog(msg: string): void {
  if (!_logDir) return
  const logPath = join(_logDir, "plugin-debug.log")
  const ts = new Date().toISOString()
  const line = ts + " " + _PREFIX + msg + "\n"
  // Fire-and-forget write + rotate
  appendFile(logPath, line).catch(function() {})
  // Rotate check (best-effort, non-blocking)
  stat(logPath).then(function(s) {
    if (s.size > _LOG_ROTATE_SIZE) {
      rename(logPath, logPath + ".1").catch(function() {})
    }
  }).catch(function() {})
}

function _log(msg: string): void {
  if (!_debugEnabled) return
  _writeLog(msg)
}

function _warn(msg: string): void {
  // Always write to log file (captures errors even when debug=false)
  _writeLog(msg)
  // Only console.error in debug mode to avoid polluting TUI
  if (_debugEnabled) console.error(_PREFIX + msg)
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
  reflective_brief?: string  // v1.2: pre-compressed semantic brief from MCP server
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

// v1.2: Resolved adaptive mode (set during injection, read by formatActiveFocusBlock)
let _adaptiveResolvedMode: string = "compact"

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

/**
 * v1.2: Compute brief metrics from all topic files on disk.
 * Reads each topic JSON and checks for reflective_brief, brief_model, brief_stats.
 */
async function computeBriefMetrics(fishTrailDir: string): Promise<BriefMetrics> {
  const now = new Date().toISOString()
  const defaultMetrics: BriefMetrics = {
    total_topics: 0,
    topics_with_brief: 0,
    brief_hit_rate: 0,
    heuristic_ratio: 0,
    agent_reject_rate: 0,
    last_updated: now,
  }

  try {
    const topicsDir = join(fishTrailDir, "topics")
    const files = await readdir(topicsDir)
    const jsonFiles = files.filter(function(f: string) { return f.endsWith(".json") })

    let totalAttempts = 0
    let totalAccepted = 0
    let totalRejected = 0
    let totalHeuristic = 0
    let totalWithBrief = 0

    for (const f of jsonFiles) {
      const data = await readJSON<Record<string, any>>(join(topicsDir, f))
      if (!data) continue
      defaultMetrics.total_topics++

      if (data.reflective_brief) {
        totalWithBrief++
      }

      const stats = data.brief_stats
      if (stats) {
        totalAttempts += (stats.agent_attempts || 0)
        totalAccepted += (stats.agent_accepted || 0)
        totalRejected += (stats.agent_rejected || 0)
        totalHeuristic += (stats.heuristic_count || 0)
      }
    }

    defaultMetrics.topics_with_brief = totalWithBrief
    defaultMetrics.brief_hit_rate = defaultMetrics.total_topics > 0
      ? totalWithBrief / defaultMetrics.total_topics : 0

    const totalGenerated = totalAccepted + totalHeuristic
    defaultMetrics.heuristic_ratio = totalGenerated > 0
      ? totalHeuristic / totalGenerated : 0

    defaultMetrics.agent_reject_rate = totalAttempts > 0
      ? totalRejected / totalAttempts : 0

    defaultMetrics.last_updated = now
  } catch {
    // topics/ dir doesn't exist yet
  }

  return defaultMetrics
}

/**
 * #164/#166: Format Block 1 — Topic Registry (stable, changes on create/delete).
 * #166: Reflective compression — compact table format, strip redundant labels.
 * Deterministically sorted by topic ID for byte-identical output across turns.
 */
function formatRegistryBlock(
  registryView: { active_topic: string; topics: Record<string, { title: string; status: string }> },
  opts: Required<PluginOptions>,
): string {
  // #166: Compact header — model knows this is auto-injected, no need to say so
  const lines: string[] = [
    "## Topics",
    "",
  ]
  // Sort by topic ID for deterministic output
  const sorted = Object.entries(registryView.topics)
    .sort(function(a, b) { return a[0].localeCompare(b[0]) })
  for (const item of sorted) {
    const marker = item[0] === registryView.active_topic ? "→" : " "
    // #166: Drop parenthetical status when it's "active" — the → marker already signals active
    const statusTag = item[1].status !== "active" ? "/" + item[1].status : ""
    lines.push(marker + " " + item[0] + statusTag + " " + item[1].title)
  }
  lines.push("")
  return lines.join("\n")
}

/**
 * #164/#166: Format Block 2 — Warm Topics Brief (semi-stable, changes on status transition).
 * #166: Reflective compression — omit verbose header, inline relations,
 * suppress "active" status (only show non-active like /warm, /paused).
 */
function formatWarmBriefBlock(
  registryView: { active_topic: string; topics: Record<string, { title: string; status: string }> },
  graph: TopicGraph | null,
  opts: Required<PluginOptions>,
): string {
  const warmTopics = Object.entries(registryView.topics)
    .filter(function(entry) { return entry[0] !== registryView.active_topic })
    .filter(function(entry) { const s = entry[1].status; return s === "active" || s === "warm" })
    .sort(function(a, b) { return a[0].localeCompare(b[0]) })
    .slice(0, opts.maxTopics)

  if (warmTopics.length === 0) {
    // #166: Empty case — return minimal single-line block instead of 3-line header+none
    return "## Related\n—\n"
  }

  const lines: string[] = [
    "## Related",
    "",
  ]
  for (const item of warmTopics) {
    // Find edge relation if available
    let relation = ""
    if (graph && graph.edges) {
      const edge = graph.edges.find(function(e) {
        return (e.source === registryView.active_topic && e.target === item[0]) ||
               (e.target === registryView.active_topic && e.source === item[0])
      })
      if (edge) relation = "·" + edge.relation
    }
    // #166: suppress "active" status, only show when non-active (e.g. /warm, /paused)
    const statusTag = (item[1].status !== "active" && item[1].status !== "warm")
      ? "/" + item[1].status : ""
    lines.push("- " + item[0] + statusTag + " " + item[1].title + relation)
  }
  lines.push("")
  return lines.join("\n")
}

/**
 * #166: Extract a reflective brief from a topic summary.
 * Tries to find the "current position" within the summary:
 *   - If summary contains "At:" or "Progress:" lines, extract those
 *   - Otherwise take first sentence (up to first period) or first 120 chars
 * Returns empty string if no compressible content.
 */
function reflectiveBrief(summary: string | undefined, maxLen: number): string {
  if (!summary) return ""
  const trimmed = summary.trim()
  if (trimmed.length === 0) return ""

  // Strategy 1: Look for "At:" or "Progress:" prefixes (common in our summaries)
  const posMatch = trimmed.match(/(?:At|Progress|Status|Current)[:]\s*(.+?)(?:\.|$)/m)
  if (posMatch && posMatch[1]) {
    const brief = posMatch[1].trim()
    return brief.length > maxLen ? brief.substring(0, maxLen) + "…" : brief
  }

  // Strategy 2: First sentence
  const firstSentence = trimmed.match(/^(.+?[.!?])(?:\s|$)/)
  if (firstSentence && firstSentence[1]) {
    const brief = firstSentence[1].trim()
    return brief.length > maxLen ? brief.substring(0, maxLen) + "…" : brief
  }

  // Strategy 3: Hard truncation at maxLen
  return trimmed.length > maxLen ? trimmed.substring(0, maxLen) + "…" : trimmed
}

/**
 * v1.2: Measure recall signal from mcp-call-log.jsonl.
 * Returns topic_show frequency (0.0~1.0) from last windowSize entries.
 * Returns null if file doesn't exist or has no data.
 */
async function measureRecallSignal(
  fishTrailDir: string,
  windowSize: number,
): Promise<number | null> {
  const logPath = join(fishTrailDir, "mcp-call-log.jsonl")
  let fh: import("fs/promises").FileHandle | null = null
  try {
    fh = await open(logPath, "r")
    const fstat = await fh.stat()
    if (fstat.size === 0) return null

    const readStart = Math.max(0, fstat.size - 65536)
    const buf = Buffer.allocUnsafe(fstat.size - readStart)
    await fh.read(buf, 0, buf.length, readStart)
    const text = buf.toString("utf-8")
    const lines = text.split("\n").filter(function(l) { return l.trim().length > 0 })

    const recent = lines.slice(-windowSize)
    if (recent.length === 0) return null

    let topicShowCount = 0
    for (const line of recent) {
      try {
        const entry = JSON.parse(line)
        if (entry.tool === "topic_show") {
          topicShowCount++
        }
      } catch {
        // skip malformed
      }
    }

    return topicShowCount / recent.length
  } catch {
    return null
  } finally {
    if (fh) await fh.close()
  }
}

/**
 * v1.2: Adaptive compression state machine.
 * UNKNOWN → COMPACT/FULL based on signal, with hysteresis + cooldown + oscillation lock.
 */
function resolveAdaptiveMode(
  current: AdaptiveState,
  signal: number | null,
  totalRounds: number,
): AdaptiveState {
  const next: AdaptiveState = {
    mode: current.mode,
    roundCounter: totalRounds,
    cooldownUntil: current.cooldownUntil,
    signalHistory: (current.signalHistory || []).concat([signal || 0]).slice(-5),
    roundsWithHighSignal: current.roundsWithHighSignal,
    roundsWithLowSignal: current.roundsWithLowSignal,
    switchHistory: current.switchHistory || [],
    unstable: current.unstable,
    signalCold: current.signalCold,
  }

  if (signal === null) {
    next.signalCold = true
    return next
  }
  next.signalCold = false

  // UNKNOWN → initial decision
  if (current.mode === "unknown") {
    next.mode = signal > 0.3 ? "full" : "compact"
    next.switchHistory = next.switchHistory.concat([{
      ts: new Date().toISOString(),
      from: "unknown",
      to: next.mode,
      round: totalRounds,
    }])
    next.cooldownUntil = totalRounds + 10
    return next
  }

  // Cooldown check
  if (totalRounds < (current.cooldownUntil || 0)) {
    return next
  }

  // Oscillation unlock
  if (current.unstable) {
    const history = next.signalHistory
    const stable = history.length >= 5 && history.every(function(s) {
      return s <= 0.1 || s >= 0.3
    })
    if (stable) {
      next.unstable = false
    } else {
      return next
    }
  }

  // Track consecutive signal
  if (signal > 0.3) {
    next.roundsWithHighSignal = (current.roundsWithHighSignal || 0) + 1
    next.roundsWithLowSignal = 0
  } else if (signal <= 0.1) {
    next.roundsWithLowSignal = (current.roundsWithLowSignal || 0) + 1
    next.roundsWithHighSignal = 0
  } else {
    next.roundsWithHighSignal = 0
    next.roundsWithLowSignal = 0
  }

  // Switch with 3-round hysteresis
  if (current.mode === "compact" && next.roundsWithHighSignal >= 3) {
    next.mode = "full"
    next.roundsWithHighSignal = 0
    next.roundsWithLowSignal = 0
    next.cooldownUntil = totalRounds + 10
    next.switchHistory = next.switchHistory.concat([{
      ts: new Date().toISOString(),
      from: "compact",
      to: "full",
      round: totalRounds,
    }])
  } else if (current.mode === "full" && next.roundsWithLowSignal >= 3) {
    next.mode = "compact"
    next.roundsWithHighSignal = 0
    next.roundsWithLowSignal = 0
    next.cooldownUntil = totalRounds + 10
    next.switchHistory = next.switchHistory.concat([{
      ts: new Date().toISOString(),
      from: "full",
      to: "compact",
      round: totalRounds,
    }])
  }

  // Oscillation detection: 5 switches in <65 rounds → lock full
  const recentSw = next.switchHistory.slice(-5)
  if (recentSw.length >= 5) {
    const span = totalRounds - recentSw[0].round
    if (span < 65) {
      next.unstable = true
      next.mode = "full"
      next.cooldownUntil = totalRounds + 20
    }
  }

  return next
}

/**
 * #164/#166/#167: Format Block 3 — Active Topic Focus (volatile, changes every turn).
 * #166: Reflective compression — semantically dense brief replaces raw metadata.
 *   - Merge title + scope into one line (eliminates "Scope:" label)
 *   - Replace full summary with reflective brief (current position only)
 *   - Compact mode indicator to inline bracket notation
 *   - Strip "(auto-injected, volatile)" — model doesn't need this meta-commentary
 * #167: compressionLevel option — "compact" (default) or "full" (verbose).
 *   - compact: ~48 tokens, optimized for Pro-tier models
 *   - full: ~108 tokens, better for Flash-tier models that may lose signal
 */
function formatActiveFocusBlock(
  registryView: { active_topic: string; topics: Record<string, { title: string; status: string }> },
  activeTopic: TopicData | null,
  detectionResult: { relation: string; confidence: number; risk: number; risk_level: string; target_topic: string | null } | null,
  opts: Required<PluginOptions>,
): string {
  // Reset detection — minimal block (same for both compression levels)
  if (detectionResult && detectionResult.relation === "reset") {
    return "## Focus\nRESET·" + registryView.active_topic + "\n[" + opts.detectionMode + "]\n"
  }

  // #167: Branch on compressionLevel
  if (opts.compressionLevel === "full") {
    return formatActiveFocusFull(registryView, activeTopic, detectionResult, opts)
  }
  if (opts.compressionLevel === "compact") {
    return formatActiveFocusCompact(registryView, activeTopic, detectionResult, opts)
  }
  // adaptive (or unspecified): use resolved adaptive mode
  return _adaptiveResolvedMode === "full"
    ? formatActiveFocusFull(registryView, activeTopic, detectionResult, opts)
    : formatActiveFocusCompact(registryView, activeTopic, detectionResult, opts)
}

/**
 * #167: Compact format (default) — ~48 tokens.
 * Reflective brief, merged title+scope, compact mode indicator.
 */
function formatActiveFocusCompact(
  registryView: { active_topic: string; topics: Record<string, { title: string; status: string }> },
  activeTopic: TopicData | null,
  detectionResult: { relation: string; confidence: number; risk: number; risk_level: string; target_topic: string | null } | null,
  opts: Required<PluginOptions>,
): string {
  const lines: string[] = [
    "## Focus",
    "",
  ]

  if (activeTopic) {
    const title = activeTopic.title || registryView.active_topic
    const scopeExcerpt = activeTopic.scope
      ? " · " + truncate(activeTopic.scope, 80)
      : ""
    const statusTag = activeTopic.status && activeTopic.status !== "active"
      ? " (" + activeTopic.status + ")" : ""
    lines.push(registryView.active_topic + " " + title + statusTag + scopeExcerpt)

    // v1.2: Prefer pre-compressed reflective_brief when available and enabled
    const brief = (opts.reflectiveBriefEnabled && activeTopic.reflective_brief)
      ? activeTopic.reflective_brief
      : reflectiveBrief(activeTopic.summary, 120)
    if (brief) {
      lines.push(brief)
    }
  } else {
    lines.push(registryView.active_topic + " (not on disk)")
  }

  if (detectionResult && opts.detectionMode === "realtime") {
    const targetTag = detectionResult.target_topic ? "→" + detectionResult.target_topic : ""
    const riskTag = detectionResult.risk_level !== "low" ? "/" + detectionResult.risk_level : ""
    lines.push(detectionResult.relation + riskTag +
      " c" + detectionResult.confidence.toFixed(1) +
      " r" + detectionResult.risk + targetTag)
  }

  lines.push("")
  lines.push("[disk|rMCP:off|detail:topic_show]")
  return lines.join("\n")
}

/**
 * #167: Full format (verbose) — ~108 tokens.
 * Explicit labels, full summary text, detailed detection metadata.
 * Better for Flash-tier models that may lose signal in compact output.
 */
function formatActiveFocusFull(
  registryView: { active_topic: string; topics: Record<string, { title: string; status: string }> },
  activeTopic: TopicData | null,
  detectionResult: { relation: string; confidence: number; risk: number; risk_level: string; target_topic: string | null } | null,
  opts: Required<PluginOptions>,
): string {
  const lines: string[] = [
    "## Active Focus (auto-injected, volatile)",
    "",
  ]

  if (activeTopic) {
    const status = activeTopic.status || "active"
    lines.push("Topic: " + registryView.active_topic + " — " + activeTopic.title + " (" + status + ")")
    if (activeTopic.scope) {
      const s = truncate(activeTopic.scope, opts.maxSummaryLen)
      lines.push("Scope: " + s)
    }
    if (activeTopic.summary) {
      const s = truncate(activeTopic.summary, opts.maxSummaryLen)
      lines.push("Summary: " + s)
    }
    // v1.2: If reflective_brief exists and enabled, show it as compressed context
    if (opts.reflectiveBriefEnabled && activeTopic.reflective_brief) {
      lines.push("Brief: " + activeTopic.reflective_brief)
    }
  } else {
    lines.push("Topic: " + registryView.active_topic + " (details not found on disk)")
  }

  // Realtime detection metadata (verbose)
  if (detectionResult && opts.detectionMode === "realtime") {
    lines.push("")
    lines.push("Detection: " + detectionResult.relation +
      " (conf=" + detectionResult.confidence.toFixed(2) +
      ", risk=" + detectionResult.risk + "/" + detectionResult.risk_level +
      (detectionResult.target_topic ? ", target=" + detectionResult.target_topic : "") + ")")
  }

  lines.push("")
  // Verbose mode indicator
  lines.push("[fish-trail-mode: " + opts.detectionMode + " | routine-MCP: suppressed | deep-query: topic_show]")
  return lines.join("\n")
}

/**
 * Read previous injected block state from disk.
 * Returns null if never written or on error.
 */
async function readInjectedState(fishTrailDir: string): Promise<InjectedBlockState | null> {
  try {
    const raw = await readFile(join(fishTrailDir, INJECTED_STATE_FILENAME), "utf-8")
    return JSON.parse(raw) as InjectedBlockState
  } catch {
    return null
  }
}

/**
 * Write current injected block state to disk for next-turn comparison.
 */
async function writeInjectedState(fishTrailDir: string, state: InjectedBlockState): Promise<void> {
  try {
    await mkdir(fishTrailDir, { recursive: true })
    await writeFile(
      join(fishTrailDir, INJECTED_STATE_FILENAME),
      JSON.stringify(state, null, 2),
      "utf-8",
    )
  } catch (e) {
    _warn("Failed to write injected state: " + String(e))
  }
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

/**
 * #158: OpenCode does not pass plugin tuple options to the plugin function.
 * The second argument `options` is undefined at runtime despite opencode.json config.
 * We must read options ourselves from opencode.json as fallback.
 *
 * Resolution order:
 *   1. Function argument `options` (if OpenCode someday passes it)
 *   2. opencode.json plugin tuple entry matching this plugin filename
 *   3. Environment variable FISH_TRAIL_DETECTION_MODE
 *   4. Hardcoded defaults
 */
const PLUGIN_FILENAME = "system-prompt-context-inject"
let _optionsLogged = false
let _inputShapeLogged = false
let _clientProbeLogged = false
let _noTopicWarned = false
let _realtimeFallbackWarned = false
let _debugEnabled = false

async function resolvePluginOptions(directory: string, fnOptions: unknown): Promise<Required<PluginOptions>> {
  const defaults: Required<PluginOptions> = {
    maxTopics: 5,
    maxSummaryLen: 200,
    detectionMode: "disk",
    compressionLevel: "compact",
    debug: false,
    reflectiveBriefEnabled: false,
    adaptiveCompressionEnabled: false,
  }

  // Layer 1: function argument
  if (fnOptions && typeof fnOptions === "object" && Object.keys(fnOptions as Record<string, unknown>).length > 0) {
    const raw = fnOptions as Record<string, unknown>
    const rawMode = raw.detectionMode as string | undefined
    const rawCompress = raw.compressionLevel as string | undefined
    return {
      maxTopics: (raw.maxTopics as number) ?? defaults.maxTopics,
      maxSummaryLen: (raw.maxSummaryLen as number) ?? defaults.maxSummaryLen,
      detectionMode: rawMode === "realtime" || rawMode === "experimental.realtime" ? "realtime" : "disk",
      compressionLevel: rawCompress === "full" ? "full" : "compact",
      debug: raw.debug === true,
      reflectiveBriefEnabled: raw.reflectiveBriefEnabled === true,
      adaptiveCompressionEnabled: raw.adaptiveCompressionEnabled === true,
    }
  }

  // Layer 2: read from opencode.json
  try {
    const configPath = join(directory, "opencode.json")
    const configRaw = await readFile(configPath, "utf-8")
    const config = JSON.parse(configRaw) as Record<string, unknown>
    const plugins = config.plugin
    if (Array.isArray(plugins)) {
      for (const entry of plugins) {
        // Tuple format: ["path/to/plugin.ts", { options }]
        if (Array.isArray(entry) && entry.length === 2) {
          const path = String(entry[0])
          const opts = entry[1] as Record<string, unknown>
          if (path.includes(PLUGIN_FILENAME) && opts && typeof opts === "object") {
            const rawMode = opts.detectionMode as string | undefined
            const rawCompress = opts.compressionLevel as string | undefined
            return {
              maxTopics: (opts.maxTopics as number) ?? defaults.maxTopics,
              maxSummaryLen: (opts.maxSummaryLen as number) ?? defaults.maxSummaryLen,
              detectionMode: rawMode === "realtime" || rawMode === "experimental.realtime" ? "realtime" : "disk",
              compressionLevel: rawCompress === "full" ? "full" : "compact",
              debug: opts.debug === true,
              reflectiveBriefEnabled: opts.reflectiveBriefEnabled === true,
              adaptiveCompressionEnabled: opts.adaptiveCompressionEnabled === true,
            }
          }
        }
      }
    }
  } catch {
    // opencode.json not found or parse failed — continue to env fallback
  }

  // Layer 3: environment variable
  const envMode = process.env.FISH_TRAIL_DETECTION_MODE
  if (envMode === "realtime" || envMode === "experimental.realtime") {
    return { ...defaults, detectionMode: "realtime" }
  }

  // Layer 4: defaults
  return defaults
}

const plugin: Plugin = async ({ directory, client, serverUrl }, options) => {
  // Resolve options with full fallback chain (#158)
  const pluginOptsPromise = resolvePluginOptions(directory, options)

  return {
    name: "system-prompt-context-inject",

    "experimental.chat.system.transform": async (input, output) => {
      const pluginOpts = await pluginOptsPromise
      _debugEnabled = pluginOpts.debug
      const fishTrailDir = join(directory, FISH_TRAIL_DIR)
      _logDir = fishTrailDir

      // #158: Log resolved options on first call for debugging
      if (!_optionsLogged) {
        _optionsLogged = true
        _log(
          "options resolved: " +
          "maxTopics=" + pluginOpts.maxTopics +
          ", maxSummaryLen=" + pluginOpts.maxSummaryLen +
          ", detectionMode=" + pluginOpts.detectionMode +
          ", client.available=" + String(!!client) +
          ", serverUrl=" + (serverUrl ? serverUrl.toString() : "n/a"),
        )
      }

      // #160b: Dump input shape for runtime debugging
      if (!_inputShapeLogged) {
        _inputShapeLogged = true
        const inputKeys = input && typeof input === "object"
          ? Object.keys(input as Record<string, unknown>).join(",")
          : String(typeof input)
        const msgsLen = input && typeof input === "object" && Array.isArray((input as Record<string, unknown>).messages)
          ? String((input as Record<string, unknown>).messages.length)
          : "n/a"
        _log(
          "input shape: keys=[" + inputKeys + "] messages.len=" + msgsLen,
        )
      }

      // #163: Auto-patch detection — check OpenCode version and lastUserMessage availability.
      // Logs version changes, provides guidance for enabling realtime mode.
      const hasLastUserMessage = "lastUserMessage" in (input as Record<string, unknown>)
      await checkAutoPatch(fishTrailDir, hasLastUserMessage)

      // #163: Probe — try client.messages() to fetch latest user message
      // This tests whether the OpenCode SDK session store has the current user message
      // available BEFORE system.transform is called. If it does, we can use this for
      // realtime detection (Scheme D) instead of relying on the hook input.
      if (!_clientProbeLogged && client && input.sessionID) {
        _clientProbeLogged = true
        try {
          const msgsResult = await client.messages({
            path: { id: input.sessionID },
            query: { limit: 3 },
          })
          if (msgsResult.status === 200 && Array.isArray(msgsResult.data)) {
            const msgCount = msgsResult.data.length
            // Find last user message and extract text from parts
            let lastUserText = "(none)"
            for (let i = msgsResult.data.length - 1; i >= 0; i--) {
              const msgEntry = msgsResult.data[i]
              if (msgEntry.info && msgEntry.info.role === "user") {
                const textParts = Array.isArray(msgEntry.parts)
                  ? msgEntry.parts.filter(function(p: { type: string }) { return p.type === "text" })
                  : []
                if (textParts.length > 0) {
                  const fullText = textParts.map(function(p: { text: string }) { return p.text }).join(" ")
                  const preview = fullText.length > 60 ? fullText.slice(0, 60) + "..." : fullText
                  lastUserText = JSON.stringify(preview)
                }
                break
              }
            }
            _log(
              "#163 client probe: " +
              "msgs=" + msgCount + ", lastUserText=" + lastUserText,
            )
          } else {
            _log(
              "#163 client probe: " +
              "status=" + msgsResult.status + " (expected 200)",
            )
          }
        } catch (e) {
          _log(
            "#163 client probe FAILED: " + String(e),
          )
        }
      } else if (!_clientProbeLogged) {
        _clientProbeLogged = true
        _log(
          "#163 client probe SKIPPED: " +
          "client=" + String(!!client) + ", sessionID=" + String(input.sessionID),
        )
      }

      // Resolve active topic with fallback chain
      const activeTopicId = await resolveActiveTopic(fishTrailDir)
      if (!activeTopicId) {
        // Cold start: no topics created yet. Log once, then inject minimal guidance.
        if (!_noTopicWarned) {
          _noTopicWarned = true
          _log(
            "No active topic found " +
            "(cold start or no topics created yet). Injecting cold-start guidance.",
          )
        }
        // Inject a minimal cold-start block so the model knows MCP tools exist
        // #166: Reflective compression — compact cold-start block
        output.system.push([
          "## Topics",
          "No active topic. Use `topic_create` to start.",
          "[disk]",
        ].join("\n"))
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
        _log(
          "topics/ directory not found. " +
          "Injection will contain topic ID only.",
        )
      }

      // Read topic graph
      const graph = await readJSON<TopicGraph>(join(fishTrailDir, "topic_graph.json"))

      // Realtime detection (if enabled)
      let detectionResult: { relation: string; confidence: number; risk: number; risk_level: string; target_topic: string | null } | null = null
      if (pluginOpts.detectionMode === "realtime") {
        // #163: Realtime mode requires either input.lastUserMessage (patched OpenCode)
        // or client.messages() SDK access. If neither provides user text, fall back
        // to disk mode for this session and warn once.
        // Check if OpenCode has been patched to pass lastUserMessage (#163)
        const patchedUserMsg = (input as Record<string, unknown>).lastUserMessage as string | undefined
        
        // #157: Extract user message robustly.
        // OpenCode hook exposes messages via input.messages, not input.content.
        // 1. If input.messages exists, find the last user message
        // 2. Else if input.content exists, use it directly
        // 3. Support both string and part-array content formats
        // #163: If hook input has no messages, try client.messages() SDK call
        let userMsg = patchedUserMsg || await extractUserMessage(input)

        if ((!userMsg || userMsg.length === 0) && client && input.sessionID) {
          try {
            const msgsResult = await client.messages({
              path: { id: input.sessionID },
              query: { limit: 1 },
            })
            if (msgsResult.status === 200 && Array.isArray(msgsResult.data) && msgsResult.data.length > 0) {
              const lastEntry = msgsResult.data[msgsResult.data.length - 1]
              if (lastEntry.info && lastEntry.info.role === "user" && Array.isArray(lastEntry.parts)) {
                const textParts = lastEntry.parts.filter(function(p: { type: string }) { return p.type === "text" })
                if (textParts.length > 0) {
                  userMsg = textParts.map(function(p: { text: string }) { return p.text }).join(" ")
                }
              }
            }
          } catch (e) {
            // client.messages() failed — continue with empty userMsg
            _warn("client.messages() failed: " + String(e))
          }
        }

        // #163: If still no user message, realtime is not functional.
        // Fall back silently to disk-mode behavior for this turn.
        if (!userMsg || userMsg.length === 0) {
          if (!_realtimeFallbackWarned) {
            _realtimeFallbackWarned = true
            _log(
              "Realtime mode configured but no user message available. " +
              "OpenCode system.transform hook does not expose user messages (#163). " +
              "Falling back to disk-mode behavior. " +
              "To enable true realtime detection, follow upstream PR: https://github.com/anomalyco/opencode/pull/28993",
            )
          }
        }

        // Debug: log extracted message length for troubleshooting (#159)
        _log(
          "Realtime detection input: " +
          "userMsg.length=" + (userMsg ? userMsg.length : 0) +
          ", first60=" + (userMsg ? JSON.stringify(userMsg.slice(0, 60)) : "null"),
        )

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

            // Debug: log detection result (#159)
            _log(
              "Realtime detection result: " +
              "relation=" + (detectionResult ? detectionResult.relation : "null") +
              ", confidence=" + (detectionResult ? detectionResult.confidence.toFixed(2) : "n/a") +
              ", target=" + (detectionResult && detectionResult.target_topic ? detectionResult.target_topic : "none"),
            )
          } catch (e) {
            // Detection failure must not break injection
            _warn("Realtime detection failed: " + String(e))
          }
        }
      }

      // Format and inject (#164: cache-stable 3-block architecture)
      const registryBlock = formatRegistryBlock(registryView, pluginOpts)
      const warmBlock = formatWarmBriefBlock(registryView, graph, pluginOpts)

      // #164: Read previous state before building active block (adaptive needs it)
      const prevState = await readInjectedState(fishTrailDir)

      // v1.2: Adaptive compression — measure signal and resolve mode
      if (pluginOpts.adaptiveCompressionEnabled) {
        const signal = await measureRecallSignal(fishTrailDir, 20)
        const prevAdaptive = prevState ? prevState.adaptiveState : undefined
        const defaultAdaptive: AdaptiveState = {
          mode: "compact",
          roundCounter: 0,
          cooldownUntil: 0,
          signalHistory: [],
          roundsWithHighSignal: 0,
          roundsWithLowSignal: 0,
          switchHistory: [],
          unstable: false,
          signalCold: false,
        }
        const adaptiveState = resolveAdaptiveMode(
          prevAdaptive || defaultAdaptive,
          signal,
          (prevAdaptive ? prevAdaptive.roundCounter : 0) + 1,
        )
        _adaptiveResolvedMode = adaptiveState.mode
        // Persist in injected state for next round
        if (prevState) {
          prevState.adaptiveState = adaptiveState
        }
        _log("adaptive signal=" + String(signal) + " mode=" + adaptiveState.mode + " round=" + adaptiveState.roundCounter)
      }

      const activeBlock = formatActiveFocusBlock(registryView, activeTopic, detectionResult, pluginOpts)

      const registryHash = simpleHash(registryBlock)
      const warmHash = simpleHash(warmBlock)
      const registryChanged = !prevState || prevState.registryHash !== registryHash
      const warmChanged = !prevState || prevState.warmHash !== warmHash
      // Active block always changes (volatile by design)

      // Push 3 separate blocks to output.system
      // Stable blocks first, volatile last — optimizes prefix cache behavior
      output.system.push(registryBlock)
      output.system.push(warmBlock)
      output.system.push(activeBlock)

      // v1.2: Compute brief metrics (every 10 rounds or if not yet computed)
      const prevRoundCount = prevState?.adaptiveState?.roundCounter || 0
      const prevMetrics = prevState?._brief_metrics
      const shouldComputeMetrics = !prevMetrics || prevRoundCount % 10 === 0
      const briefMetrics = shouldComputeMetrics
        ? await computeBriefMetrics(fishTrailDir)
        : prevMetrics

      await writeInjectedState(fishTrailDir, {
        registryHash,
        warmHash,
        registryBlock,
        warmBlock,
        opencodeVersion: getOpenCodeVersion(),
        adaptiveState: prevState ? prevState.adaptiveState : undefined,
        _brief_metrics: briefMetrics,
      })

      const relatedCount = Object.keys(registryView.topics).length - 1
      const modeTag = pluginOpts.detectionMode === "realtime" ? "realtime" : "disk"
      const cacheTag = "registry=" + (registryChanged ? "MISS" : "HIT") +
        ", warm=" + (warmChanged ? "MISS" : "HIT") +
        ", active=MISS"
      _log(
        "Injected 3-block context (" + modeTag + " mode): " +
        "active=" + activeTopicId + ", related=" + relatedCount + ", cache=" + cacheTag,
      )
    },
  }
}

export default plugin
