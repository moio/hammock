#!/usr/bin/env python3
"""Structural validation of a skill directory. Stdlib only.

Adapted from Anthropic's skill-creator (MIT):
https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator
"""

import re
import sys
from pathlib import Path

ALLOWED_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}


def parse_frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---\s*(?:\n|$)", text, re.DOTALL)
    if not match:
        return None, "no valid YAML frontmatter block (--- ... ---)"
    frontmatter = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.startswith((" ", "\t", "#")):
            continue
        key, _, value = line.partition(":")
        value = value.strip().strip("'\"")
        if value:
            frontmatter[key.strip()] = value
    return frontmatter, None


def validate(skill_path):
    skill_path = Path(skill_path)
    skill_md = skill_path / "SKILL.md"
    if not skill_md.is_file():
        return False, f"SKILL.md not found in {skill_path}"

    fm, err = parse_frontmatter(skill_md.read_text())
    if fm is None:
        return False, err

    extra = set(fm) - ALLOWED_KEYS
    if extra:
        return False, f"unexpected frontmatter keys: {', '.join(sorted(extra))}"
    if "name" not in fm:
        return False, "missing 'name' in frontmatter"
    if "description" not in fm:
        return False, "missing 'description' in frontmatter"

    name = fm["name"]
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
        return False, f"name '{name}' should be kebab-case"
    if name != skill_path.name:
        return False, f"name '{name}' does not match directory name '{skill_path.name}'"

    description = fm["description"]
    if "<" in description or ">" in description:
        return False, "description must not contain angle brackets"
    if len(description) > 1024:
        return False, f"description too long ({len(description)} chars, max 1024)"

    return True, "skill is valid"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <skill-directory>")
        sys.exit(1)
    ok, message = validate(sys.argv[1])
    print(message)
    sys.exit(0 if ok else 1)
