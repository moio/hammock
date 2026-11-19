---
name: license
description: Set up or verify a repository's own OSS license file. Downloads the canonical SPDX license text with correct copyright year and holder, or checks that existing LICENSE files match canonical SPDX terms with correct attribution. Use whenever the user wants to add a license, asks "which license should I use", mentions relicensing or dual licensing, says a license file looks wrong, or wants a copyright line or license attribution checked. Not for dependency license compliance scanning.
---

# License file setup and verification

Goal: the repository contains license file(s) whose **terms** match the canonical SPDX text (no modifications), with **copyright year and holder** correctly set.

Scope: the repository's own license only. Out of scope: license compliance of dependencies, LICENSE-vs-COPYING nuances beyond file detection, third-party notices files (do not touch them).

A bundled script does the deterministic part — comparing terms against SPDX — so your judgment goes where it matters: identifying licenses, attribution, and compatibility. Don't eyeball word-level diffs when the script can produce them exactly; don't ask the script questions it can't answer.

## Inputs you need

Ask the user for anything not known from context:

1. **SPDX license identifier** (e.g. `MIT`, `Apache-2.0`, `GPL-3.0-only`, `BSD-3-Clause`). If the user says "MIT-style" or is vague, ask. For copyleft licenses, ask `-only` vs `-or-later` explicitly (see the GPL note in Mode 1).
2. **Copyright holder** — the name to appear in the copyright line. For individuals ask for the exact string they want (e.g. `Jane Doe`, `Jane Doe <jane@example.com>`, or `Jane Doe and contributors`). For orgs, use the org's legal name.
3. **Contact email** for the copyright line, if the user wants one. Some projects include it, some don't — follow the user's preference, don't guess.

Never invent a copyright holder. If a project has a `CONTRIBUTING.md`, `.mailmap`, or package metadata naming an author/org, propose that as default and confirm.

## Mode 1: download and install

When the repo has no license file, or the user wants a different license than the present one:

1. Fetch canonical text from SPDX:

   ```sh
   curl -fsSL "https://raw.githubusercontent.com/spdx/license-list-data/main/text/<SPDX-ID>.txt"
   ```

   If that 404s, try `https://spdx.org/licenses/<SPDX-ID>.txt`; if that also fails, the ID is wrong or not in the SPDX list — confirm with the user. Do not write license text from memory; always fetch or verify against SPDX.

2. Determine the copyright year:
   - New project: current year (`date +%Y`).
   - Existing content (git history present): earliest commit year — `git log --reverse --format=%as | head -1` — written as a range `<earliest>-<current>` if they differ (e.g. `2019-2025`), single year if equal. Confirm the range convention with the user only if the history is ambiguous (e.g. history starts with an import commit).
3. Fill the license's copyright placeholder. SPDX texts use `<year> <copyright holders>` (MIT, BSD), `[yyyy] [name of copyright owner]` (Apache-2.0 appendix), or similar markers. Replace only those placeholders:
   - `Copyright (c) 2019-2025 Jane Doe` or `Copyright (c) 2019-2025 Jane Doe <jane@example.com>`
   - For licenses without a copyright placeholder, note that and skip this step.
4. Write to `LICENSE`. Existing conventions in the repo override: use `LICENSE.md`/`COPYING`/`LICENSE.txt` if those names are already established by sibling files or tooling. Detect the extension convention: if the repo is markdown-heavy (docs in `.md`), prefer `LICENSE.md`; plain repos usually use bare `LICENSE`. When unsure, ask.
5. **Verify what you just wrote** — this closes the loop deterministically:

   ```sh
   python <skill-dir>/scripts/compare_spdx.py compare <license-file> --spdx-id <SPDX-ID>
   ```

   It reports OK, or the exact word-level divergence from canonical text (it ignores formatting, wrapping, and copyright lines — those are checked separately). Exit code 0 means the terms are canonical.

6. **GPL-family note**: the canonical text of `GPL-3.0-only` and `GPL-3.0-or-later` is identical — the choice is declared *outside* the license file, in source-file headers ("or any later version") and package metadata (`GPL-3.0-or-later`). After writing the file, tell the user which headers/metadata express their choice, and flag if they conflict. Same pattern applies to AGPL and LGPL.
7. If the repo previously had a different license and now gets a new one, warn: relicensing requires consent from all copyright holders of existing contributions. Do not silently overwrite a nonempty license file with different terms — show the diff and get explicit approval.
8. Point out (but do not edit without being asked) files that commonly reference the license: `package.json` (`license` field), `pyproject.toml`, `Cargo.toml`, `README.md` badge/section, `LICENSE` detection in CI. Offer to align them to the SPDX identifier — for multiple licenses, that may be an SPDX expression (e.g. `MIT OR Apache-2.0`).

## Mode 2: verify

When the repo already has license file(s):

1. **Find them**: search for `LICENSE*`, `LICENCE*`, `COPYING*`, `COPYRIGHT*`, `NOTICE*` in the root and any subdirectory. Multiple license files are legitimate (dual licensing, per-directory licenses, `LICENSE-APACHE`/`LICENSE-MIT` pairs) — inventory them all before judging.

2. **Identify each file's SPDX ID** before comparing — Mode 1 knows the ID, Mode 2 must find it. In order of evidence strength:
   - Package metadata: `license` field in `package.json`, `license`/`classifier` in `pyproject.toml`, `license` in `Cargo.toml` — treat as a strong hypothesis, still verify against the text.
   - The script's identify mode, which scores the file against the SPDX license list:

     ```sh
     python <skill-dir>/scripts/compare_spdx.py identify <license-file>
     ```

     It prints the top candidates with match ratios; ≥95% is a confident match. Below that, treat as unidentifiable and report the closest candidates rather than guessing.
   - License file names (`LICENSE-APACHE` → `Apache-2.0`) and README statements — weakest, use only as hints for what to fetch.

3. **Compare terms against SPDX**:

   ```sh
   python <skill-dir>/scripts/compare_spdx.py compare <license-files...> --spdx-id <SPDX-ID>
   ```

   Whitespace, re-wrapping, typographic quotes, and copyright lines are ignored automatically; **any word-level difference in the terms it reports is a finding** — relay the exact diff to the user. If the file is missing entirely (license added by headers or metadata only), that is a finding on its own: say so and offer Mode 1.

4. **Check attribution** (the script strips copyright lines, so you do this part): every copyright line must have a year and a holder. Flag:
   - missing or placeholder values (`<year>`, `<copyright holders>`, `[yyyy]`, `Your Name`, `[year]`)
   - years: verify against git history of the files the license covers (`git log --reverse --format=%as -- <paths> | head -1`). A stale single year (e.g. `Copyright (c) 2018` with commits in 2025) is a finding — propose `<first>-<current>`. Do not auto-bump the end year of an existing range without confirming; some projects intentionally freeze it.
   - holder consistency: if the same holder appears in multiple files with different spellings, flag it.

5. **Check compatibility across files** (only when there are multiple distinct licenses):
   - Report the license combination and whether it is a *declared* dual/multi-license (e.g. `LICENSE-APACHE` + `LICENSE-MIT`, or "OR" expressions in package metadata) or an *accidental* mix (e.g. a vendored GPL directory next to an MIT root).
   - For an accidental mix, check directionality: permissive into permissive is generally fine; GPL-family code inside a more permissive project is a real finding — report it, do not attempt to fix it yourself. Point at the affected paths.
   - Note: this is structural compatibility of the repo's own files, not dependency compliance — restate that if the results could be misread that way.

6. **Report format** — a short table:

   | File | SPDX match | Terms | Attribution |
   |---|---|---|---|
   | LICENSE | MIT | OK / MISMATCH (diff excerpt) | OK / stale year / placeholder |

   followed by proposed fixes. Apply fixes only after the user approves them.

## The bundled script

`scripts/compare_spdx.py` — Python 3 standard library only, no dependencies. Fetches canonical text from SPDX over the network; for offline runs, download the text first and pass `--spdx-text <file>`.

- `compare <files...> --spdx-id <ID>`: verify terms against canonical text. Exit 0 = all match, 1 = mismatch, 2 = usage/network error. `--spdx-text` for offline use.
- `identify <file>`: score against candidate licenses from the SPDX list; prints ranked candidates, confident best match at ≥95%. Exit 1 when nothing matches confidently.

Limitations worth knowing: it ignores formatting and copyright lines by design (attribution is your job), and `identify` shortlists candidates by keyword overlap — a heavily modified license may land in no shortlist, which is itself a useful signal that the terms were altered.
