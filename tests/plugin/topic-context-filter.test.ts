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

import { readFileSync } from "node:fs"

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

// ─── Run all tests ───

async function main() {
  console.log("=== topic-context-filter tests ===")

  await testPluginLoads()
  await testShortConversationNoOp()
  await testGracefulDegradation()
  await testSingleTopicNoOp()
  await testMultiTopicFiltering()

  // Cleanup
  rmSync(testDir, { recursive: true, force: true })

  console.log(`\n${passed} passed, ${failed} failed`)
  if (failed > 0) process.exit(1)
}

main().catch((e) => {
  console.error(e)
  process.exit(1)
})
