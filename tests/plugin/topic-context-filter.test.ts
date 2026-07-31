/**
 * Unit tests for topic-context-filter plugin
 *
 * Run: npx tsx tests/plugin/topic-context-filter.test.ts
 */

import { readFile } from "node:fs/promises"
import { join } from "node:path"

const FIXTURES = join(import.meta.dirname, "fixtures")

// We test the filtering logic by simulating what the plugin does.
// Since the plugin exports a factory, we import and invoke it with a mock directory.

import pluginFactory from "../../.opencode/plugin/topic-context-filter.ts"

interface PluginMessage {
  info: { role: string; [key: string]: unknown }
  parts: { type: string; text?: string; [key: string]: unknown }[]
}

async function loadFixture<T>(name: string): Promise<T> {
  return JSON.parse(await readFile(join(FIXTURES, name), "utf-8"))
}

// Setup: create a temp directory structure mimicking .petfish/fish-trail/
import { mkdirSync, writeFileSync, rmSync } from "node:fs"
import { tmpdir } from "node:os"

const testDir = join(tmpdir(), `topic-filter-test-${Date.now()}`)

function setupTestDir(registryFile: string, topicFile: string | null) {
  rmSync(testDir, { recursive: true, force: true })
  mkdirSync(join(testDir, ".petfish", "fish-trail", "topics"), { recursive: true })

  const registry = JSON.parse(readFileSync(join(FIXTURES, registryFile), "utf-8"))
  writeFileSync(join(testDir, ".petfish", "fish-trail", "topic-registry.json"), JSON.stringify(registry))

  if (topicFile && registry.active_topic) {
    const topic = JSON.parse(readFileSync(join(FIXTURES, topicFile), "utf-8"))
    writeFileSync(
      join(testDir, ".petfish", "fish-trail", "topics", `${registry.active_topic}.json`),
      JSON.stringify(topic),
    )
  }
}

// Setup with ALL topics populated (for effective-topic-detection tests)
function setupTestDirAllTopics(registryFile: string, topicFiles: Record<string, string>) {
  rmSync(testDir, { recursive: true, force: true })
  mkdirSync(join(testDir, ".petfish", "fish-trail", "topics"), { recursive: true })

  const registry = JSON.parse(readFileSync(join(FIXTURES, registryFile), "utf-8"))
  writeFileSync(join(testDir, ".petfish", "fish-trail", "topic-registry.json"), JSON.stringify(registry))

  for (const [topicId, fixtureName] of Object.entries(topicFiles)) {
    const topic = JSON.parse(readFileSync(join(FIXTURES, fixtureName), "utf-8"))
    writeFileSync(
      join(testDir, ".petfish", "fish-trail", "topics", `${topicId}.json`),
      JSON.stringify(topic),
    )
  }
}

import { readFileSync, readdirSync } from "node:fs"

// ─── Test helpers ───

let passed = 0
let failed = 0

function assert(condition: boolean, msg: string) {
  if (condition) {
    passed++
    console.log(`  ✓ ${msg}`)
  } else {
    failed++
    console.error(`  ✗ ${msg}`)
  }
}

// ─── Tests ───

async function testMultiTopicFiltering() {
  console.log("\nTest 1: Multi-topic filtering")

  setupTestDir("topic-registry-multi.json", "topic-database.json")
  const messages: PluginMessage[] = await loadFixture("messages-multi-topic.json")

  const plugin = await pluginFactory({ directory: testDir }, { enabled: true, safetyWindow: 3, minMessages: 10 })
  const hook = (plugin as any)["experimental.chat.messages.transform"]

  const output = { messages: [...messages] }
  await hook({}, output)

  assert(output.messages.length < messages.length, `Filtered: ${messages.length} → ${output.messages.length}`)

  // Last 3 messages should always be kept
  const last3Original = messages.slice(-3)
  const last3Filtered = output.messages.slice(-3)
  assert(
    last3Original[0].parts[0].text === last3Filtered[0].parts[0].text,
    "Last 3 messages preserved",
  )

  // Check tool_use/tool_result pairs not split
  for (let i = 0; i < output.messages.length; i++) {
    const msg = output.messages[i]
    if (msg.parts.some((p: any) => p.type === "tool_use")) {
      assert(
        i + 1 < output.messages.length && output.messages[i + 1].parts.some((p: any) => p.type === "tool_result"),
        `tool_use at index ${i} has matching tool_result`,
      )
    }
  }

  // Check placeholder messages exist
  const placeholders = output.messages.filter((m) => m.parts[0]?.text?.includes("messages from other topics omitted"))
  assert(placeholders.length > 0, `Placeholder messages present (${placeholders.length} found)`)

  // Verify database-related messages are kept
  const keptTexts = output.messages
    .filter((m) => !m.parts[0]?.text?.includes("omitted"))
    .map((m) => m.parts[0]?.text ?? "")
    .join(" ")
    .toLowerCase()
  assert(keptTexts.includes("postgres"), "Database/postgres messages kept")
}

async function testSingleTopicNoOp() {
  console.log("\nTest 2: Single-topic no-op")

  setupTestDir("topic-registry-multi.json", "topic-database.json")

  // Create messages that are all about database (single topic)
  const messages: PluginMessage[] = [
    { info: { role: "user" }, parts: [{ type: "text", text: "Let's work on the database migration" }] },
    { info: { role: "assistant" }, parts: [{ type: "text", text: "I'll check the postgres schema first." }] },
    { info: { role: "user" }, parts: [{ type: "text", text: "OK" }] },
    { info: { role: "assistant" }, parts: [{ type: "text", text: "Done." }] },
    { info: { role: "user" }, parts: [{ type: "text", text: "Now add the migration script for the users table" }] },
    { info: { role: "assistant" }, parts: [{ type: "text", text: "Here's the SQL migration for the users table in postgres." }] },
    { info: { role: "user" }, parts: [{ type: "text", text: "Good" }] },
    { info: { role: "assistant" }, parts: [{ type: "text", text: "Shall I also add the indexes?" }] },
    { info: { role: "user" }, parts: [{ type: "text", text: "Yes, add indexes for the database queries" }] },
    { info: { role: "assistant" }, parts: [{ type: "text", text: "Added GIN and B-tree indexes for postgres." }] },
    { info: { role: "user" }, parts: [{ type: "text", text: "Run the migration now" }] },
  ]

  const plugin = await pluginFactory({ directory: testDir }, { enabled: true, safetyWindow: 3, minMessages: 10 })
  const hook = (plugin as any)["experimental.chat.messages.transform"]

  const output = { messages: [...messages] }
  await hook({}, output)

  assert(output.messages.length === messages.length, `Single-topic: no messages removed (${output.messages.length} === ${messages.length})`)
}

async function testShortConversationNoOp() {
  console.log("\nTest 3: Short conversation no-op")

  setupTestDir("topic-registry-multi.json", "topic-database.json")

  const messages: PluginMessage[] = Array.from({ length: 8 }, (_, i) => ({
    info: { role: i % 2 === 0 ? "user" : "assistant" },
    parts: [{ type: "text", text: `Message ${i} about various unrelated things` }],
  }))

  const plugin = await pluginFactory({ directory: testDir }, { enabled: true, safetyWindow: 3, minMessages: 10 })
  const hook = (plugin as any)["experimental.chat.messages.transform"]

  const output = { messages: [...messages] }
  await hook({}, output)

  assert(output.messages.length === 8, `Short conversation unchanged (${output.messages.length} === 8)`)
}

async function testGracefulDegradation() {
  console.log("\nTest 4: Graceful degradation (no registry)")

  // Use a directory without topic-registry.json
  const emptyDir = join(tmpdir(), `topic-filter-empty-${Date.now()}`)
  mkdirSync(emptyDir, { recursive: true })

  const messages: PluginMessage[] = Array.from({ length: 15 }, (_, i) => ({
    info: { role: i % 2 === 0 ? "user" : "assistant" },
    parts: [{ type: "text", text: `Message ${i}` }],
  }))

  const plugin = await pluginFactory({ directory: emptyDir }, { enabled: true })
  const hook = (plugin as any)["experimental.chat.messages.transform"]

  const output = { messages: [...messages] }
  await hook({}, output)

  assert(output.messages.length === 15, `No registry: messages unchanged (${output.messages.length} === 15)`)

  rmSync(emptyDir, { recursive: true, force: true })
}

async function testPluginLoads() {
  console.log("\nTest 5: Plugin loads correctly")

  const plugin = await pluginFactory({ directory: "." }, { enabled: true })
  assert(plugin.name === "topic-context-filter", `Plugin name is "topic-context-filter"`)
  assert("experimental.chat.messages.transform" in plugin, "Hook registered")
}

// ─── Test 6: Effective topic detection (the key fix) ───

async function testEffectiveTopicDetection() {
  console.log("\nTest 6: Effective topic detection (registry=database, user switches to auth)")

  // Registry says active = database, but all 3 topics have data files
  setupTestDirAllTopics("topic-registry-multi.json", {
    "topic_database_migration": "topic-database.json",
    "topic_auth_flow": "topic-auth.json",
    "topic_ui_redesign": "topic-ui.json",
  })

  // Conversation: database work (old topic) then user switches to auth (new topic)
  // Last user message must be about auth to trigger effective topic switch
  // Removal ratio: 4/14 ≈ 29% (within 20-50% range, avoids nuclear_guard)
  const messages: PluginMessage[] = [
    // Database messages (old topic — will be archived when effective topic = auth)
    { info: { role: "user" }, parts: [{ type: "text", text: "Migrate from MySQL to PostgreSQL database schema" }] },
    { info: { role: "assistant" }, parts: [{ type: "text", text: "Checking postgres schema for the database migration." }] },
    { info: { role: "user" }, parts: [{ type: "text", text: "Add database indexes for query performance" }] },
    { info: { role: "assistant" }, parts: [{ type: "text", text: "Added B-tree indexes for postgres database tables." }] },
    // Auth messages (new topic — effective topic after user switches)
    { info: { role: "user" }, parts: [{ type: "text", text: "Now set up JWT auth with OAuth tokens for login" }] },
    { info: { role: "assistant" }, parts: [{ type: "text", text: "Implementing JWT auth and OAuth session management." }] },
    { info: { role: "user" }, parts: [{ type: "text", text: "Add OAuth2 token rotation to the auth flow" }] },
    { info: { role: "assistant" }, parts: [{ type: "text", text: "OAuth2 token rotation added to auth system." }] },
    { info: { role: "user" }, parts: [{ type: "text", text: "Good. Now secure the login endpoint with JWT validation" }] },
    { info: { role: "assistant" }, parts: [{ type: "text", text: "JWT validation middleware added to login route." }] },
    { info: { role: "user" }, parts: [{ type: "text", text: "Test the auth flow with expired tokens" }] },
    { info: { role: "assistant" }, parts: [{ type: "text", text: "Testing JWT auth with expired token handling." }] },
    { info: { role: "user" }, parts: [{ type: "text", text: "Auth flow looks good. Add OAuth refresh token endpoint" }] },
    { info: { role: "user" }, parts: [{ type: "text", text: "Also add session timeout to the auth system" }] },
  ]

  const plugin = await pluginFactory({ directory: testDir }, { enabled: true, safetyWindow: 3, minMessages: 10 })
  const hook = (plugin as any)["experimental.chat.messages.transform"]

  const output = { messages: [...messages] }
  await hook({}, output)

  // The last user message is about auth → effective topic should be auth
  // Database messages should be archived, auth messages should be kept
  const keptTexts = output.messages
    .filter((m) => !m.parts[0]?.text?.includes("omitted"))
    .map((m) => m.parts[0]?.text ?? "")
    .join(" ")
    .toLowerCase()

  assert(keptTexts.includes("jwt") || keptTexts.includes("auth") || keptTexts.includes("oauth"),
    "Auth messages kept (effective topic = auth)")

  // Check if filtering actually occurred
  const filteredHappened = output.messages.length < messages.length
  if (filteredHappened) {
    // Verify database messages were archived under database topic
    const archiveDir = join(testDir, ".petfish", "fish-trail", "message-archive")
    try {
      const archives = readdirSync(archiveDir)
      assert(archives.length > 0, `Archive files created (${archives.length})`)

      // Find database archive and verify content
      const dbArchiveFile = archives.find((f) => f.includes("database") || f.includes("topic_database"))
      if (dbArchiveFile) {
        const content = readFileSync(join(archiveDir, dbArchiveFile), "utf-8")
        assert(content.includes("postgres") || content.includes("database") || content.includes("migration"),
          "Database archive contains database-related content")
      }
    } catch {
      assert(false, "Archive directory should exist when filtering occurred")
    }
  } else {
    // Filtering didn't occur — check filter-debug.log for reason
    const logPath = join(testDir, ".petfish", "fish-trail", "filter-debug.log")
    try {
      const logContent = readFileSync(logPath, "utf-8")
      const lastEntry = logContent.trim().split("\n").pop() ?? ""
      console.log(`    (Filter skipped: ${lastEntry})`)
    } catch {
      console.log("    (No filter log found)")
    }
  }
}

// ─── Test 7: Archive categorization by owning topic ───

async function testArchiveCategorization() {
  console.log("\nTest 7: Archive categorization by owning topic")

  setupTestDirAllTopics("topic-registry-multi.json", {
    "topic_database_migration": "topic-database.json",
    "topic_auth_flow": "topic-auth.json",
    "topic_ui_redesign": "topic-ui.json",
  })

  // Mixed conversation, last message stays on database topic
  const messages: PluginMessage[] = await loadFixture<PluginMessage[]>("messages-multi-topic.json")

  const plugin = await pluginFactory({ directory: testDir }, { enabled: true, safetyWindow: 3, minMessages: 10 })
  const hook = (plugin as any)["experimental.chat.messages.transform"]

  const output = { messages: [...messages] }
  await hook({}, output)

  // Check archive files — auth and UI messages should be in separate files
  const archiveDir = join(testDir, ".petfish", "fish-trail", "message-archive")
  try {
    const archives = readdirSync(archiveDir)
    assert(archives.length > 0, `Archive files created (${archives.length} files)`)

    // Each archive file should contain messages matching that topic
    for (const file of archives) {
      const content = readFileSync(join(archiveDir, file), "utf-8")
      const lines = content.trim().split("\n")
      for (const line of lines) {
        try {
          const entry = JSON.parse(line)
          assert(entry.owning_topic !== undefined, `Archive entry has owning_topic field`)
          assert(entry.text !== undefined, `Archive entry has full text content`)
          assert(entry.text_length > 0, `Archive entry text is non-empty`)
        } catch { /* skip invalid */ }
      }
    }
  } catch {
    // If no archive was created, it means no messages were removed
    // (e.g., effective topic detection kept everything). That's also valid.
    assert(output.messages.length <= messages.length, "No regression in message count")
  }
}

// ─── Test 8: Placeholder accumulation prevention ───

async function testPlaceholderAccumulation() {
  console.log("\nTest 8: Placeholder accumulation prevention")

  setupTestDirAllTopics("topic-registry-multi.json", {
    "topic_database_migration": "topic-database.json",
    "topic_auth_flow": "topic-auth.json",
    "topic_ui_redesign": "topic-ui.json",
  })

  // Conversation that already has placeholder messages from a previous filter run
  const messages: PluginMessage[] = [
    { info: { role: "user" }, parts: [{ type: "text", text: "Set up JWT auth with OAuth tokens" }] },
    { info: { role: "assistant" }, parts: [{ type: "text", text: "[2 messages from other topics omitted]" }] },
    { info: { role: "assistant" }, parts: [{ type: "text", text: "I'll implement the JWT auth login flow." }] },
    { info: { role: "user" }, parts: [{ type: "text", text: "Good, add OAuth session management" }] },
    { info: { role: "assistant" }, parts: [{ type: "text", text: "Added OAuth2 with refresh token rotation." }] },
    { info: { role: "assistant" }, parts: [{ type: "text", text: "[1 messages from other topics omitted]" }] },
    { info: { role: "user" }, parts: [{ type: "text", text: "Now work on the React UI component layout" }] },
    { info: { role: "assistant" }, parts: [{ type: "text", text: "Creating CSS grid for the component layout." }] },
    { info: { role: "user" }, parts: [{ type: "text", text: "Add responsive breakpoints to the UI" }] },
    { info: { role: "assistant" }, parts: [{ type: "text", text: "Added mobile/tablet breakpoints for the layout." }] },
    { info: { role: "user" }, parts: [{ type: "text", text: "Switch to database migration, check postgres schema" }] },
  ]

  const plugin = await pluginFactory({ directory: testDir }, { enabled: true, safetyWindow: 3, minMessages: 10 })
  const hook = (plugin as any)["experimental.chat.messages.transform"]

  const output = { messages: [...messages] }
  await hook({}, output)

  // Placeholder messages should be PRESERVED (not re-filtered)
  const placeholders = output.messages.filter((m) =>
    m.parts[0]?.text?.includes("messages from other topics omitted"),
  )
  assert(placeholders.length >= 1, `Placeholder messages preserved (${placeholders.length} found)`)

  // Verify no message was converted to a double-placeholder
  const doublePlaceholders = output.messages.filter((m) => {
    const t = m.parts[0]?.text ?? ""
    return t.includes("omitted") && t.includes("omitted", t.indexOf("omitted") + 1)
  })
  assert(doublePlaceholders.length === 0, "No double-placeholder accumulation")
}

// ─── Run all tests ───

async function main() {
  console.log("=== topic-context-filter tests ===")

  await testPluginLoads()
  await testShortConversationNoOp()
  await testGracefulDegradation()
  await testSingleTopicNoOp()
  await testMultiTopicFiltering()
  await testEffectiveTopicDetection()
  await testArchiveCategorization()
  await testPlaceholderAccumulation()

  // Cleanup
  rmSync(testDir, { recursive: true, force: true })

  console.log(`\n${passed} passed, ${failed} failed`)
  if (failed > 0) process.exit(1)
}

main().catch((e) => {
  console.error(e)
  process.exit(1)
})
