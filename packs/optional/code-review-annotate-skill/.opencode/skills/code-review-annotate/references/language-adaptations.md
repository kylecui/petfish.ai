# Language Adaptations — comment formats and per-language bugbug categories

SKILL.md sections 1-2 use C as the baseline. This file carries the per-language
equivalents: how the Purpose/Calls/Returns triple maps to each language's
comment mechanism, plus bugbug categories specific to each runtime. The
hard constraints (add comment lines only, zero deletions, skip already
annotated functions) are identical everywhere and are not repeated here.

---

## Go

```go
// Purpose: <one line: what this function does>
// Calls: <parameter meaning; when/by whom it is invoked>
// Returns: <exact semantics; for (v, err): when err is nil vs not>
```

- godoc convention starts comments with the function name (`// Foo does ...`)
  so godoc can extract them; this pipeline keeps the triple-line structure and
  allows the name-leading line as the first prefix
- bugbug additions: goroutine leaks (no exit path, ctx not propagated); defer
  accumulating inside loops; channel deadlocks (unbuffered send with no
  receiver); ignored errors (`_ =`); concurrent map read/write without a lock;
  WaitGroup Add/Done mismatch; time.After leaking inside loops

## Rust

```rust
/// Purpose: <one line> (doc comments use ///; plain comments stay //)
/// Calls: <parameter meaning; invocation context>
/// Returns: <Result<T, E> variant semantics; what Option::None represents>
```

- Doc comments (`///`) and plain comments (`//`) are different mechanisms:
  function headers here always use `///`; an existing `///` block counts as
  already annotated — skip it
- bugbug additions: `unwrap()/expect()` outside test paths; `unsafe` blocks
  without a SAFETY comment; `clone()` papering over borrow checking
  (performance debt); lossy `as` casts (u64 to u32); panic paths (index out of
  bounds, overflow assertions in debug); `RefCell` double-borrow

## Python

```python
def foo(x):
    """Purpose: <one line>

    Calls: <parameter meaning; invocation context>
    Returns: <exact semantics; None and exception semantics>
    """
```

- The docstring carries the triple structure; functions with an existing
  docstring are skipped; trivial one-liners get a single-line docstring
- bugbug additions: mutable default arguments (`def f(x=[])`); SQL or command
  strings built by concatenation (use parameterized queries); `subprocess`
  with `shell=True`; bare `except:` or `except Exception: pass`; resources
  opened without a with-block (files, locks, connections); `is` used for value
  comparison; shared mutable global state; dynamic code execution

## Java

```java
/**
 * Purpose: <one line>
 * Calls: <parameter meaning; invocation context>
 * Returns: <exact semantics; null meaning / @throws>
 */
```

- Javadoc `/** */` carries the header; existing Javadoc counts as annotated.
  The `-Werror=comment` class of breakage does not exist in Java, but a `*/`
  inside comment text terminates the block early - comment text must not
  contain `*/`
- bugbug additions: `equals` without `hashCode`; mutable static fields; `==`
  on Strings holding captured input; autoboxing NPE; shared `SimpleDateFormat`
  (not thread-safe); reliance on `finalize`; swallowed exceptions (caught,
  logged, neither handled nor rethrown)

## JavaScript / TypeScript

```javascript
/**
 * Purpose: <one line>
 * Calls: <parameter meaning; invocation context (event loop / promise chain / callback)>
 * Returns: <exact semantics; promise resolve/reject; whether mutable arguments are modified in place>
 */
```

- JSDoc carries the header; TypeScript projects should add `@param`/`@returns`
  types; existing JSDoc/TSDoc counts as annotated
- bugbug additions: `==` loose comparison; dynamic code construction;
  `innerHTML` as an injection surface; missing await (floating promises); empty
  catch blocks; `var` hoisting misuse; event listeners never removed (leaks);
  `JSON.parse` without try

---

## Trimming rules

1. For each language: keep the generic categories from SKILL.md section 2
   (security / memory / logic), add that language's additions from this file,
   and drop the C-specific domain categories that do not apply
2. Project-specific contracts (numbering schemes, logging conventions, known
   debt registries) are injected into the subagent prompt as CONTEXT - never
   written into this file
3. Comment language follows the project's existing comments - an
   English-commented project uses `Purpose/Calls/Returns` (the triple-line
   structure is unchanged)
