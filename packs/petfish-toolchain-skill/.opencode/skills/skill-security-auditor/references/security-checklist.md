# skill-security-auditor checklist

This checklist is the manual review companion for `scripts/audit_skill.py`.

## TrustSkills scoring model

- `0.0` = safe or no meaningful risk signal
- `1.0` = dangerous and should fail the gate
- Default gate suggestion: fail at `>= 0.5`
- Severity weights used by the bundled scanner:
  - `CRITICAL = 1.0`
  - `HIGH = 0.6`
  - `MEDIUM = 0.3`
  - `LOW = 0.1`
  - `INFO = 0.0`

## 1. File System

### FS-01 — Destructive delete patterns
- **What to check:** `rm -rf`, `shutil.rmtree`, recursive delete helpers, wildcard deletes, delete loops over large path sets.
- **Why it's dangerous:** A skill can wipe repositories, user home directories, temp roots, or release artifacts.
- **Severity:** `CRITICAL` for broad destructive commands, `HIGH` for unsafe recursive deletion.
- **Remediation:** Restrict deletion scope, require explicit path allowlists, add dry-run, and block destructive defaults.

### FS-02 — Path traversal and escape scope
- **What to check:** `..`, parent path joins, unvalidated user input used as file paths, archive extraction without path checks.
- **Why it's dangerous:** A skill meant to touch one directory may read or write anywhere on disk.
- **Severity:** `HIGH`
- **Remediation:** Normalize paths, resolve against a fixed root, reject escaping paths, and log the effective target.

### FS-03 — Unrestricted writes
- **What to check:** writes to arbitrary user-provided paths, pack-wide rewrites without narrowing, output paths missing bounds checks.
- **Why it's dangerous:** Overwrites config, source, secrets, or system files outside the intended skill scope.
- **Severity:** `HIGH`
- **Remediation:** Constrain writes to a declared workspace root, require explicit file lists, and prefer preview modes.

### FS-04 — Broad glob patterns
- **What to check:** `**/*`, repo-wide recursive scans combined with delete or rewrite actions, mass rename patterns.
- **Why it's dangerous:** Makes accidental high-blast-radius changes easy.
- **Severity:** `MEDIUM`
- **Remediation:** Narrow globs, exclude sensitive directories, and separate discovery from mutation.

### FS-05 — Hardcoded absolute paths
- **What to check:** absolute Windows or POSIX paths in scripts or instructions.
- **Why it's dangerous:** Breaks portability and can accidentally target sensitive locations.
- **Severity:** `LOW`
- **Remediation:** Use relative paths, CLI arguments, or resolved workspace roots.

## 2. Credentials

### CR-01 — `.env` and secret file access
- **What to check:** reads of `.env`, `.env.local`, `.npmrc`, `credentials`, `secrets`, or similar files.
- **Why it's dangerous:** These files often contain production credentials and internal tokens.
- **Severity:** `HIGH`
- **Remediation:** Remove the read, replace with mock data, or require explicit user-provided non-secret input.

### CR-02 — SSH material and browser profiles
- **What to check:** `.ssh`, private keys, known_hosts writes, browser profile directories, saved session stores.
- **Why it's dangerous:** Enables credential theft, session hijack, or infrastructure compromise.
- **Severity:** `HIGH`
- **Remediation:** Never read private key material, avoid persistent profile harvesting, and use isolated auth flows.

### CR-03 — API keys and token harvesting
- **What to check:** regexes for `token`, `api_key`, `bearer`, cookie stores, clipboard secret collection.
- **Why it's dangerous:** Skills can silently extract credentials unrelated to the requested task.
- **Severity:** `HIGH`
- **Remediation:** Remove harvesting logic, require explicit user consent for auth material, and mask logs.

### CR-04 — Hardcoded credentials
- **What to check:** secrets embedded in source, examples, or default config.
- **Why it's dangerous:** Leaks immediately and encourages unsafe reuse.
- **Severity:** `HIGH`
- **Remediation:** Replace with environment variables, placeholders, or documented setup steps.

## 3. Network

### NW-01 — Remote download and pipe-to-shell
- **What to check:** download-and-execute flows, remote installers, shell pipelines from network content.
- **Why it's dangerous:** One-step remote code execution.
- **Severity:** `CRITICAL`
- **Remediation:** Download to disk only when necessary, verify integrity, review content manually, and never auto-execute.

### NW-02 — Network access without clear purpose
- **What to check:** HTTP requests in scripts, silent telemetry, upload endpoints, undocumented third-party APIs.
- **Why it's dangerous:** Expands data exposure and makes secret leakage easier.
- **Severity:** `MEDIUM`
- **Remediation:** Document the purpose, limit domains, set timeouts, and avoid transmitting local content unless required.

### NW-03 — Data exfiltration patterns
- **What to check:** uploads of local files, environment dumps, secret-bearing logs, POST requests carrying workspace data.
- **Why it's dangerous:** Sensitive project data may leave the machine.
- **Severity:** `CRITICAL`
- **Remediation:** Remove exfiltration logic, redact payloads, and require explicit user approval for outbound data.

## 4. Execution

### EX-01 — Dynamic code execution
- **What to check:** `eval`, `exec`, `compile`, template-driven command construction, arbitrary interpreter entry points.
- **Why it's dangerous:** Converts untrusted strings into code.
- **Severity:** `HIGH`, or `CRITICAL` when fed by remote content.
- **Remediation:** Replace with parsing, dispatch tables, or strict command allowlists.

### EX-02 — Shell execution without safeguards
- **What to check:** `shell=True`, `os.system`, PowerShell expression execution, string-built commands.
- **Why it's dangerous:** Raises injection risk and widens command surface.
- **Severity:** `MEDIUM` to `HIGH`
- **Remediation:** Use argument arrays, explicit allowlists, escaping only as a last resort, and document why shell mode is required.

### EX-03 — Unsafe subprocess usage
- **What to check:** `subprocess.run/call/Popen` without `check=True`, missing timeouts, inherited stdin, or command strings built from user input.
- **Why it's dangerous:** Hides failures and increases abuse potential.
- **Severity:** `MEDIUM`
- **Remediation:** Use explicit argument lists, `check=True`, timeouts, and narrow inputs.

### EX-04 — Executable content in references
- **What to check:** shell or PowerShell snippets in `references/`, shebangs, hidden payloads in docs.
- **Why it's dangerous:** Users may copy-paste unsafe commands from supposedly passive guidance.
- **Severity:** `MEDIUM`
- **Remediation:** Move executable helpers into `scripts/`, document risks, and keep references explanatory.

## 5. Permissions

### PM-01 — Privilege escalation
- **What to check:** `sudo`, admin-only commands, service manager control, system directory writes.
- **Why it's dangerous:** Turns a skill into a host-level operator.
- **Severity:** `HIGH`
- **Remediation:** Require explicit approval, narrow the action, and explain why elevated access is unavoidable.

### PM-02 — Overly broad file permissions
- **What to check:** `chmod 777`, world-writable dirs, permissive ACL changes, ownership changes.
- **Why it's dangerous:** Weakens the host security boundary for later abuse.
- **Severity:** `HIGH`
- **Remediation:** Use least privilege, prefer read-only defaults, and grant only the minimum required bits.

### PM-03 — Missing preview or dry-run on risky actions
- **What to check:** scripts that modify or delete data without a preview mode.
- **Why it's dangerous:** Makes mistakes irreversible and hides blast radius.
- **Severity:** `LOW`
- **Remediation:** Add `--dry-run`, show targets first, and require a second explicit step for apply.

## 6. MCP and Tools

### MT-01 — Unrestricted tool lists
- **What to check:** instructions like “use any tool”, “all tools allowed”, or broad shell access without scope.
- **Why it's dangerous:** Removes the safety boundary between requested work and available power.
- **Severity:** `HIGH`
- **Remediation:** Name the exact tools, explain why each is needed, and narrow the allowed action set.

### MT-02 — Dangerous MCP servers
- **What to check:** MCP servers that can run arbitrary commands, browse secrets, or write anywhere without approval language.
- **Why it's dangerous:** External servers may extend the attack surface beyond local review.
- **Severity:** `HIGH`
- **Remediation:** Document server capability, require explicit approval, and isolate high-privilege servers.

### MT-03 — Hidden remote execution via tool wrappers
- **What to check:** tools or MCP instructions that indirectly fetch and run code, including helper installers.
- **Why it's dangerous:** Looks like “just a tool call” but behaves like arbitrary execution.
- **Severity:** `CRITICAL`
- **Remediation:** Split fetch from review, block auto-run behavior, and require integrity checks.

## 7. Prompt Injection

### PI-01 — Instruction override phrases
- **What to check:** “ignore previous instructions”, “override system rules”, “skip approvals”, “do not mention safeguards”.
- **Why it's dangerous:** A malicious or sloppy skill can deliberately defeat the agent safety model.
- **Severity:** `HIGH`
- **Remediation:** Remove override language and state explicit boundaries instead.

### PI-02 — Secret disclosure requests
- **What to check:** requests to reveal hidden prompts, environment variables, auth tokens, or internal config.
- **Why it's dangerous:** Converts the skill into an extraction prompt.
- **Severity:** `CRITICAL`
- **Remediation:** Ban secret disclosure instructions and replace with privacy-safe alternatives.

### PI-03 — Role confusion or authority spoofing
- **What to check:** phrases pretending to be system, developer, admin, or security owner without real authority.
- **Why it's dangerous:** Confuses the execution boundary and can coerce unsafe behavior.
- **Severity:** `MEDIUM`
- **Remediation:** Use plain role descriptions and clearly separate user intent from policy.

### PI-04 — Ambiguous approval semantics
- **What to check:** instructions that imply consent, silent apply behavior, or “assume approval” wording.
- **Why it's dangerous:** High-risk actions may occur without a clear user decision.
- **Severity:** `HIGH`
- **Remediation:** Require explicit confirmation before destructive, privileged, or networked actions.

## Review decision checklist

- Score `< fail-threshold` and no unaccepted `CRITICAL` findings: candidate to pass.
- Score `>= fail-threshold`: fail the gate until remediated.
- Any secret exfiltration, remote execution, or destructive default should be treated as release-blocking unless explicitly redesigned.
