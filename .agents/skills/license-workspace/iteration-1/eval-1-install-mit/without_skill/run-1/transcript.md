## Eval Prompt

Add a license to this repo. My name is Jane Doe, email jane@example.com. I want MIT.

### Tool: bash
```
{"command": "ls -a && date +%Y"}
```

### Tool result (bash, error=False)
```
.
..
.git
README.md
2026

```

### Tool: write
```
{"content": "MIT License\n\nCopyright (c) 2026 Jane Doe <jane@example.com>\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the \"Software\"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\
```

### Tool result (write, error=False)
```
Successfully wrote to LICENSE
```

### Assistant
Added `LICENSE` with the standard MIT license text, copyright `2026 Jane Doe <jane@example.com>` (year taken from the current date).

Optional next step: add a `license` field to your `README.md` or package metadata to declare MIT — happy to do that if you'd like.