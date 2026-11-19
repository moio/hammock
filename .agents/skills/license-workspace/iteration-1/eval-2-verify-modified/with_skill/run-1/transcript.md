## Eval Prompt

Is our license file still correct? Someone said it might have been edited by accident.

### Tool: read
```
{"path": "/Users/SMOIOLI/synced/repos/hammock/.agents/skills/license/SKILL.md"}
```

### Tool: bash
```
{"command": "ls -la /private/tmp/license-eval-fixtures/eval-2-verify; find . -iname \"LICENSE*\" -not -path \"./node_modules/*\" | head"}
```

### Tool result (read, error=False)
```
---
name: license
description: Set up or verify a repository's own OSS license file. Downloads the canonical SPDX license text with correct copyright year and holder, or checks that existing LICENSE files match canonical SPDX terms with correct attribution. Use whenever the user wants to add a license, asks "which license should I use", mentions relicensing or dual licensing, says a license file looks wrong, or wants a copyright line or license attribution checked. Not for dependency license compliance scanning.
---

# License file setup and verification

Goal: the repository contains license file(s) whose **terms** match the canonical SPDX text (no modifications), with **copyright year and holder** correctly set.

Scope: the repository's own license only. Out of scope: license compliance of dependencies, LICENSE-vs-COPYING nuances beyond file detection, third-party notices files (do not touch them).

A bundled script does the deterministic part — comparing terms against SPDX — so your judgment goes where it matters: identifying licenses, attribution, and compatibility. Don't eyeball word-level diffs when the script can produce them exactly; don't ask the script questions it can't 
```

### Tool result (bash, error=False)
```
total 16
drwxr-xr-x   5 SMOIOLI  wheel   160 Nov 19 09:36 .
drwxr-xr-x   6 SMOIOLI  wheel   192 Nov 19 09:36 ..
drwxr-xr-x  12 SMOIOLI  wheel   384 Nov 19 09:36 .git
-rw-r--r--   1 SMOIOLI  wheel  1063 Nov 19 09:36 LICENSE
-rw-r--r--   1 SMOIOLI  wheel    25 Nov 19 09:36 README.md
./LICENSE

```

### Tool: bash
```
{"command": "python3 /Users/SMOIOLI/synced/repos/hammock/.agents/skills/license/scripts/compare_spdx.py identify LICENSE; head -5 LICENSE"}
```

### Tool result (bash, error=False)
```
 98.8%  MIT
 65.2%  HPND-sell-MIT-disclaimer-xserver
 10.5%  FSFAP-no-warranty-disclaimer
  7.5%  WTFNMFPL
  6.9%  ANTLR-PD-fallback
  1.4%  GFDL-1.2-no-invariants-or-later
  1.3%  GFDL-1.1-no-invariants-or-later
  1.3%  GFDL-1.3-no-invariants-or-later

Best match: MIT (98.8%)
MIT License

Copyright (c) 2018 Jane Doe

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and

```

### Tool: bash
```
{"command": "python3 /Users/SMOIOLI/synced/repos/hammock/.agents/skills/license/scripts/compare_spdx.py compare LICENSE --spdx-id MIT; git log --reverse --format=%as | head -1; git log --format=%as -1; cat package.json 2>/dev/null; cat README.md"}
```

### Tool result (bash, error=False)
```
LICENSE: MISMATCH vs SPDX MIT
  (word-level differences; whitespace/wrapping ignored)
  context: ...IS PROVIDED "AS IS",
  - WITHOUT
  + WITH
  context: ...IS", WITHOUT WARRANTY OF
  - ANY
  + SOME
2018-03-10
2026-02-20
# Grep Toolkit
more code

```

### Assistant
Your suspicion is confirmed — the LICENSE has been edited. Here's the report:

| File | SPDX match | Terms | Attribution |
|---|---|---|---|
| `LICENSE` | MIT (98.8%) | **MISMATCH** — 2 words altered | Stale year |

**Terms findings** (exact word-level diff vs canonical MIT):
- `"...IS PROVIDED "AS IS", ~~WITHOUT~~ WITH WARRANTY..."` — "WITHOUT" was changed to "WITH"
- `"...IS", ~~ANY~~ SOME WARRANTY OF ANY KIND..."` — wait, more precisely: "WITHOUT WARRANTY OF ~~ANY~~ SOME..." — "ANY" was changed to "SOME"

Someone accidentally flipped "WITHOUT WARRANTY OF ANY KIND" into "WITH SOME WARRANTY OF... KIND", which legally inverts the disclaimer. This needs fixing.

**Attribution finding:**
- Copyright line reads `Copyright (c) 2018 Jane Doe` (holder — confirm this is correct), but git history spans **2018 → 2026**, so the year is stale. Convention would suggest `2018-2026`.

**Proposed fixes** (need your approval before I edit):
1. Restore the canonical MIT wording — replace `WITH SOME WARRANTY` back to `WITHOUT WARRANTY OF ANY` (i.e., re-fetch the canonical SPDX MIT text and re-apply the copyright line).
2. Update the copyright line to `Copyright (c) 2018-2026 Jane Doe` — unless you intentionally froze the year.

Shall I apply both?