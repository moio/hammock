## Eval Prompt

Add a license to this repo. My name is Jane Doe, email jane@example.com. I want MIT.

### Tool: read
```
{"path": "/Users/SMOIOLI/.agents/skills/license/SKILL.md"}
```

### Tool result (read, error=True)
```
ENOTDIR: not a directory, access '/Users/SMOIOLI/.agents/skills/license/SKILL.md'
```

### Tool: read
```
{"path": "/Users/SMOIOLI/synced/repos/hammock/.agents/skills/license/SKILL.md"}
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

### Tool: bash
```
{"command": "ls -a; git log --reverse --format=%as 2>/dev/null | head -1; date +%Y"}
```

### Tool result (bash, error=False)
```
.
..
.git
README.md
2026-01-15
2026

```

### Tool: bash
```
{"command": "curl -fsSL \"https://raw.githubusercontent.com/spdx/license-list-data/main/text/MIT.txt\" -o /tmp/mit.txt && head -5 /tmp/mit.txt"}
```

### Tool result (bash, error=False)
```
MIT License

Copyright (c) <year> <copyright holders>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and

```

### Tool: bash
```
{"command": "sed \"s/<year> <copyright holders>/2026 Jane Doe <jane@example.com>/\" /tmp/mit.txt > LICENSE && python /Users/SMOIOLI/synced/repos/hammock/.agents/skills/license/scripts/compare_spdx.py compare LICENSE --spdx-id MIT"}
```

### Tool result (bash, error=True)
```
/bin/bash: python: command not found


Command exited with code 127
```

### Tool: bash
```
{"command": "python3 /Users/SMOIOLI/synced/repos/hammock/.agents/skills/license/scripts/compare_spdx.py compare LICENSE --spdx-id MIT && cat LICENSE | head -4"}
```

### Tool result (bash, error=False)
```
LICENSE: OK — terms match SPDX MIT
MIT License

Copyright (c) 2026 Jane Doe <jane@example.com>


```

### Assistant
Done — created `LICENSE` with the canonical SPDX MIT text, filled in as `Copyright (c) 2026 Jane Doe <jane@example.com>` (verified against SPDX, terms match exactly).

One thing you may want to align (I didn't edit it): `README.md` or any package metadata could reference the license. Let me know if you'd like that.