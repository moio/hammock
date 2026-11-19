# THE GOLDEN RULE: Less is more.

Do not add code, text, or solve problems unless absolutely required or explicitly given permission.

Strive for DRY and conciseness without sacrificing clarity.

No cruft: whenever you restructure things, clean up what you touch.

No backwards compatibility: do not add wrappers, compatibilty layers, etc. Correct callers when changing signatures.

# Skill writing

Skills must:
 - be placed in `.agent/skills`
 - be harness-agnostic, do not make assumptions on features (eg. subagents)
 - only use Python, stdlib only, only if scripts are needed
