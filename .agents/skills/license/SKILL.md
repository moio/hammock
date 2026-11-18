---
name: license
description: Set up or verify a repository's own OSS license file. Downloads the canonical SPDX license text with correct copyright year and holder, or checks that existing LICENSE files match canonical SPDX terms with correct attribution. Use when asked to add a license, fix a license file, or verify license files. Not for dependency license compliance scanning.
---

# License file setup and verification

Goal: the repository contains license file(s) whose **terms** are byte-equivalent to the canonical SPDX text (no modifications), with **copyright year and holder** correctly set.

Scope: the repository's own license only. Out of scope: license compliance of dependencies, LICENSE-vs-COPYING nuances beyond file detection, third-party notices files (do not touch them).

## Inputs you need

Ask the user for anything not known from context:

1. **SPDX license identifier** (e.g. `MIT`, `Apache-2.0`, `GPL-3.0-only`, `BSD-3-Clause`). If the user says "MIT-style" or is vague, ask.
2. **Copyright holder** — the name to appear in the copyright line. For individuals ask for the exact string they want (e.g. `Jane Doe`, `Jane Doe <jane@example.com>`, or `Jane Doe and contributors`). For orgs, use the org's legal name.
3. **Contact email** for the copyright line, if the user wants one. Some projects include it, some don't — follow the user's preference, don't guess.

Never invent a copyright holder. If a project has a `CONTRIBUTING.md`, `.mailmap`, or package metadata naming an author/org, propose that as default and confirm.

## Mode 1: download and install

When the repo has no license file, or the user wants a different license than the present one:

1. Fetch canonical text from SPDX:

   ```sh
   curl -fsSL "https://raw.githubusercontent.com/spdx/license-list-data/main/text/<SPDX-ID>.txt"
   ```

   If that 404s, the ID is wrong or not in the SPDX list — confirm with the user. Do not write license text from memory; always fetch or verify against SPDX.

2. Determine the copyright year:
   - New project: current year.
   - Existing content (git history present): earliest commit year, written as a range `<earliest>-<current>` if they differ (e.g. `2019-2025`), single year if equal. Confirm the range convention with the user only if the history is ambiguous (e.g. history starts with an import commit).
3. Fill the license's copyright placeholder. SPDX texts use `<year> <copyright holders>` (MIT, BSD) or similar markers (Apache-2.0 uses the appendix boilerplate). Replace only those placeholders:
   - `Copyright (c) 2019-2025 Jane Doe` or `Copyright (c) 2019-2025 Jane Doe <jane@example.com>`
   - For licenses without a copyright placeholder, note that and skip this step.
4. Write to `LICENSE`. Existing conventions in the repo override: use `LICENSE.md`/`COPYING`/`LICENSE.txt` if those names are already established by sibling files or tooling. Detect the extension convention: if the repo is markdown-heavy (docs in `.md`), prefer `LICENSE.md`; plain repos usually use bare `LICENSE`. When unsure, ask.
5. If the repo previously had a different license and now gets a new one, warn: relicensing requires consent from all copyright holders of existing contributions. Do not silently overwrite a nonempty license file with different terms — show the diff and get explicit approval.
6. Point out (but do not edit without being asked) files that commonly reference the license: `package.json` (`license` field), `pyproject.toml`, `Cargo.toml`, `README.md` badge/section, `LICENSE` detection in CI. Offer to align them to the SPDX identifier.

## Mode 2: verify

When the repo already has license file(s):

1. **Find them**: search for `LICENSE*`, `LICENCE*`, `COPYING*`, `COPYRIGHT*`, `NOTICE*` in the root and any subdirectory. Multiple license files are legitimate (dual licensing, per-directory licenses, `LICENSE-APACHE`/`LICENSE-MIT` pairs) — inventory them all before judging.

2. **Compare terms against SPDX**: strip the copyright line(s) (lines matching `Copyright \(c\)\|Copyright ©\|©`) and compare the remainder with the canonical SPDX text for the best-matching identifier. Whitespace and trailing-newline differences are fine; **any word-level difference in the terms is a finding** — report the exact diverging lines. If you cannot identify which SPDX license the text matches, say so explicitly and list the closest candidates rather than guessing.

3. **Check attribution**: every copyright line must have a year and a holder. Flag:
   - missing or placeholder values (`<year>`, `<copyright holders>`, `Your Name`, `[year]`)
   - years: verify against git history of the files the license covers (earliest commit year). A stale single year (e.g. `Copyright (c) 2018` with commits in 2025) is a finding — propose `<first>-<current>`. Do not auto-bump the end year of an existing range without confirming; some projects intentionally freeze it.
   - holder consistency: if the same holder appears in multiple files with different spellings, flag it.

4. **Check compatibility across files** (only when there are multiple distinct licenses):
   - Report the license combination and whether it is a *declared* dual/multi-license (e.g. `LICENSE-APACHE` + `LICENSE-MIT`, or "OR" expressions in package metadata) or an *accidental* mix (e.g. a vendored GPL directory next to an MIT root).
   - For an accidental mix, check directionality: permissive into permissive is generally fine; GPL-family code inside a more permissive project is a real finding — report it, do not attempt to fix it yourself. Point at the affected paths.
   - Note: this is structural compatibility of the repo's own files, not dependency compliance — restate that if the results could be misread that way.

5. **Report format** — a short table:

   | File | SPDX match | Terms | Attribution |
   |---|---|---|---|
   | LICENSE | MIT | OK / MISMATCH (lines N, M) | OK / stale year / placeholder |

   followed by proposed fixes. Apply fixes only after the user approves them.
