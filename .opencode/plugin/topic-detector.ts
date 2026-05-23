/**
 * Tier 1 topic change detector - keyword + Jaccard + signal + bilingual + drift.
 * Ported from topic_detector.py.
 * Tier 2 (semantic/embedding) is intentionally NOT included - it stays MCP-side
 * for on-demand use only (#150).
 *
 * Bun transpiler note:
 *   Do NOT use (x || "").method() - Bun/JSC miscompiles method calls on
 *   || fallback expressions. Always assign to variable first.
 *   Use function() instead of arrow functions in .filter()/.sort()/.map()
 *   when they contain || comparisons with method calls.
 */

// ─── Types ───────────────────────────────────────────────────────────────────

export interface TopicRef {
  id?: string
  title?: string
  scope?: string
  tags?: string[]
}

export interface DetectResult {
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

// ─── Helper functions ────────────────────────────────────────────────────────

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

// ─── Main class ──────────────────────────────────────────────────────────────

export class TopicDetector {
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
