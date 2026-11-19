## Eval Prompt

We want to relicense from GPL-3.0-only to Apache-2.0. Also our LICENSE-APACHE file in vendor/ has been hand-edited — check it.

### Tool: bash
```
{"command": "ls -R | head -50 && echo --- && head -20 vendor/LICENSE-APACHE && echo ... && diff <(curl -s https://www.apache.org/licenses/LICENSE-2.0.txt) vendor/LICENSE-APACHE"}
```

### Tool result (bash, error=True)
```
LICENSE
pyproject.toml
README.md
vendor

./vendor:
lib

./vendor/lib:
LICENSE-APACHE
---
head: vendor/LICENSE-APACHE: No such file or directory


Command exited with code 1
```

### Tool: bash
```
{"command": "head -15 vendor/lib/LICENSE-APACHE; echo ===; grep -rn \"GPL\\|license\" pyproject.toml README.md | head; echo ===; head -5 LICENSE; grep -rn \"Copyright\" vendor/lib/LICENSE-APACHE"}
```

### Tool result (bash, error=False)
```
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

"License" shall mean the terms and conditions for use, reproduction, and distribution as defined by Sections 1 through 9 of this document.

"Licensor" shall mean the copyright owner or entity authorized by the copyright owner that is granting the License.

"Legal Entity" shall mean the union of the acting entity and all other entities that control, are controlled by, or are under common control with that entity. For the purposes of this definition, "control" means (i) the power, direct or indirect, to cause the direction or management of such entity, whether by contract or otherwise, or (ii) ownership of fifty percent (50%) or more of the outstanding shares, or (iii) beneficial ownership of such entity.

"You" (or "Your") shall mean an individual or Legal Entity exercising permissions granted by this License.
===
pyproject.toml:4:license = "GPL-3.0-only"
===
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright © 2007 Free Software Foundation, Inc. <https://fsf.org/>

vendor/lib/LICENSE-APACHE:29:2. Grant of Copyright Licen
```

### Tool: bash
```
{"command": "sed -n 25-65p vendor/lib/LICENSE-APACHE 2>/dev/null || sed -n '25,70p' vendor/lib/LICENSE-APACHE; echo ===; sed -n '55,70p' vendor/lib/LICENSE-APACHE"}
```

### Tool result (bash, error=False)
```
"Contribution" shall mean any work of authorship, including the original version of the Work and any modifications or additions to that Work or Derivative Works thereof, that is intentionally submitted to Licensor for inclusion in the Work by the copyright owner or by an individual or Legal Entity authorized to submit on behalf of the copyright owner. For the purposes of this definition, "submitted" means any form of electronic, verbal, or written communication sent to the Licensor or its representatives, including but not limited to communication on electronic mailing lists, source code control systems, and issue tracking systems that are managed by, or on behalf of, the Licensor for the purpose of discussing and improving the Work, but excluding communication that is conspicuously marked or otherwise designated in writing by the copyright owner as "Not a Contribution."

"Contributor" shall mean Licensor and any individual or Legal Entity on behalf of whom a Contribution has been received by Licensor and subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of this License, each Contributor hereby grants to You a perpetual, 
```

### Assistant
Let me try diffing against the canonical text from apache.org:

### Tool: bash
```
{"command": "curl -s --max-time 10 https://www.apache.org/licenses/LICENSE-2.0.txt -o /tmp/canonical-apache.txt && diff /tmp/canonical-apache.txt vendor/lib/LICENSE-APACHE && echo IDENTICAL"}
```

### Tool result (bash, error=True)
```
0a1,3
> Apache License
> Version 2.0, January 2004
> http://www.apache.org/licenses/
2,4c5
<                                  Apache License
<                            Version 2.0, January 2004
<                         http://www.apache.org/licenses/
---
> TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION
6c7
<    TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION
---
> 1. Definitions.
8c9
<    1. Definitions.
---
> "License" shall mean the terms and conditions for use, reproduction, and distribution as defined by Sections 1 through 9 of this document.
10,11c11
<       "License" shall mean the terms and conditions for use, reproduction,
<       and distribution as defined by Sections 1 through 9 of this document.
---
> "Licensor" shall mean the copyright owner or entity authorized by the copyright owner that is granting the License.
13,14c13
<       "Licensor" shall mean the copyright owner or entity authorized by
<       the copyright owner that is granting the License.
---
> "Legal Entity" shall mean the union of the acting entity and all other entities that control, are controlled by, or are under common control with that entity. For the purposes of this 
```

### Assistant
The diff is mostly line re-wrapping. Let me normalize whitespace and compare word-for-word to catch any actual hand edits:

### Tool: bash
```
{"command": "tr -s ' \\n' ' ' < vendor/lib/LICENSE-APACHE > /tmp/vend.txt; tr -s ' \\n' ' ' < /tmp/canonical-apache.txt > /tmp/canon.txt; diff <(fold -w90 /tmp/canon.txt) <(fold -w90 /tmp/vend.txt)"}
```

### Tool result (bash, error=True)
```
1,114c1,114
<  Apache License Version 2.0, January 2004 http://www.apache.org/licenses/ TERMS AND CONDIT
< IONS FOR USE, REPRODUCTION, AND DISTRIBUTION 1. Definitions. "License" shall mean the term
< s and conditions for use, reproduction, and distribution as defined by Sections 1 through 
< 9 of this document. "Licensor" shall mean the copyright owner or entity authorized by the 
< copyright owner that is granting the License. "Legal Entity" shall mean the union of the a
< cting entity and all other entities that control, are controlled by, or are under common c
< ontrol with that entity. For the purposes of this definition, "control" means (i) the powe
< r, direct or indirect, to cause the direction or management of such entity, whether by con
< tract or otherwise, or (ii) ownership of fifty percent (50%) or more of the outstanding sh
< ares, or (iii) beneficial ownership of such entity. "You" (or "Your") shall mean an indivi
< dual or Legal Entity exercising permissions granted by this License. "Source" form shall m
< ean the preferred form for making modifications, including but not limited to software sou
< rce code, documentation source, and configuration files. "Object" form
```

### Assistant
The fold offsets obscure it — let me compare the token streams directly:

### Tool: bash
```
{"command": "diff <(tr -s ' \\n' '\\n' < /tmp/canon.txt) <(tr -s ' \\n' '\\n' < /tmp/vend.txt)"}
```

### Tool result (bash, error=True)
```
1d0
< 


Command exited with code 1
```

### Assistant
The vendor license is clean — after normalizing whitespace, it's word-for-word the canonical Apache-2.0 text. Now let me do the relicense:

### Tool: bash
```
{"command": "cat pyproject.toml"}
```

### Tool result (bash, error=False)
```
[project]
name = "treebark"
version = "0.2.0"
license = "GPL-3.0-only"

```

### Tool: bash
```
{"command": "cp vendor/lib/LICENSE-APACHE LICENSE && wc -l LICENSE"}
```

### Tool result (bash, error=False)
```
      73 LICENSE

```

### Tool: edit
```
{"edits": [{"newText": "license = \"Apache-2.0\"", "oldText": "license = \"GPL-3.0-only\""}], "path": "pyproject.toml"}
```

### Tool result (edit, error=False)
```
Successfully replaced 1 block(s) in pyproject.toml.
```

### Tool: bash
```
{"command": "cat pyproject.toml; head -3 LICENSE; grep -rn \"GPL\" . --include='*' -l"}
```

### Tool result (bash, error=True)
```
[project]
name = "treebark"
version = "0.2.0"
license = "Apache-2.0"
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/


Command exited with code 1
```

### Assistant
Done. Summary:

**vendor/lib/LICENSE-APACHE check** ✅
- Compared word-for-word against the canonical text from apache.org (after normalizing whitespace/line-wrapping): **no hand edits**. It's the verbatim Apache-2.0 text, just reformatted — lines unwrapped, indentation stripped, and the boxed title header flattened. Content-wise it's safe to use verbatim.

**Relicense GPL-3.0-only → Apache-2.0** ✅
- `LICENSE` — replaced GPL-3.0 text with the Apache-2.0 text (copy of the verified vendor file).
- `pyproject.toml` — `license = "GPL-3.0-only"` → `license = "Apache-2.0"`.
- No remaining GPL references in the repo.

Two follow-ups to consider:
1. **README** — there's no license section/badge there; you may want to add one stating Apache-2.0.
2. **Legal note**: relicensing requires consent from all copyright holders of existing contributions (unless covered by a CLA). If `vendor/lib` is third-party Apache-2.0 code, keep its license file and add attribution/NOTICE as required by Apache-2.0 §4(d).