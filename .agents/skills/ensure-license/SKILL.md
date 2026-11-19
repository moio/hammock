---
name: ensure-license
description: Set up or verify a repository's own OSS license file. Use when asked to add a license, fix a license file, or verify license files. Not for dependency license compliance scanning.
---

# License file

Invariant: the project root contains license file(s) whose **terms** are equivalent to the canonical SPDX text of the project's license, with **copyright year and holder** correctly set.

Scope: the project root only. Out of scope: licenses in subdirectories and vendored code (do not touch or report them), dependency compliance, third-party notices files (do not touch them).

Idempotence: applying this skill twice produces no further changes.

## Inputs

Ask the user for anything not known from context:

1. **SPDX license identifier** (e.g. `MIT`, `Apache-2.0`, `GPL-3.0-only`, `BSD-3-Clause`). If the user says "MIT-style" or is vague, ask.
2. **Copyright holder** — the name for the copyright line. For individuals ask for the exact string (e.g. `Jane Doe`, `Jane Doe <jane@example.com>`, or `Jane Doe and contributors`); for orgs, the legal name.
3. **Contact email** for the copyright line, if wanted. Follow the user's preference, don't guess.

Never invent a copyright holder. If `CONTRIBUTING.md`, `.mailmap`, or package metadata names an author/org, propose that as default and confirm.

## Canon

The canonical SPDX text is the reference. Always fetch it, never write license text from memory:

```sh
curl -fsSL "https://raw.githubusercontent.com/spdx/license-list-data/main/text/<SPDX-ID>.txt"
```

A 404 means the ID is wrong or not in the SPDX list — confirm with the user.

Copyright years come from git history of the files the license covers (earliest commit year). The expected attribution is `<first>-<current>` when they differ, single year if equal.

## Converge

Compare the current state to the invariant, then apply the minimal action:

- **No license file** → install: fetch canonical text, fill the copyright placeholder (SPDX texts use `<year> <copyright holders>`, or appendix boilerplate for Apache-2.0; note and skip licenses without one), write to `LICENSE`. Use `LICENSE.md`/`COPYING`/`LICENSE.txt` instead when sibling files or tooling already establish that convention; markdown-heavy repos may prefer `LICENSE.md`. When unsure, ask.
- **Different license terms present** → relicensing requires consent from all copyright holders of existing contributions. Show the diff and get explicit approval before overwriting.
- **Terms diverge from canon** → report the diverging lines, propose restoring canonical text.
- **Attribution drift** → placeholder values (`<year>`, `Your Name`), missing year/holder, or stale years are findings; propose the fix. Don't auto-bump the end year of an existing range without confirming — some projects intentionally freeze it. Flag inconsistent holder spellings across files.

After convergence, point out (but don't edit unasked) files that commonly reference the license: `package.json` (`license` field), `pyproject.toml`, `Cargo.toml`, `README.md` badge/section, CI license detection. Offer to align them to the SPDX identifier.

## Check (read-only)

When the user asks to verify rather than fix:

1. Inventory root license files: `LICENSE*`, `LICENCE*`, `COPYING*`, `COPYRIGHT*`, `NOTICE*`. Multiple files can be legitimate (dual licensing, `LICENSE-APACHE`/`LICENSE-MIT` pairs) — inventory all before judging.
2. Compare terms with canon: ignore whitespace and trailing-newline differences; any word-level difference in the terms is a finding — report the exact diverging lines. If you can't identify which SPDX license the text matches, say so and list the closest candidates rather than guessing.
3. Check attribution per the drift rules above.
4. With multiple distinct licenses, report whether the combination is *declared* (dual/multi-license) or *accidental* (e.g. a GPL-family file next to an MIT root). Permissive-into-permissive is generally fine; the reverse is a real finding — report it, don't fix it. Note this is structural compatibility of the repo's own files, not dependency compliance, if results could be misread that way.

Report as a short table:

| File | SPDX match | Terms | Attribution |
|---|---|---|---|
| LICENSE | MIT | OK / MISMATCH (lines N, M) | OK / stale year / placeholder |

followed by proposed fixes. Apply fixes only after the user approves them.
