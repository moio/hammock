---
name: skill-creator
description: Create new skills or edit existing ones. Use whenever the user wants to create a skill, turn a workflow into a skill, or modify a skill's instructions or description.
---

# Skill Creator

Create skills that are small, harness-agnostic, and easy for a model to follow. Less is more: every line in a skill costs context and attention on every future invocation.

## Capture intent

The conversation often already contains the workflow ("turn this into a skill"). In that case, extract what you need from history — tools used, sequence of steps, corrections the user made — and confirm with the user. Otherwise ask:

1. What should the skill enable the model to do?
2. When should it trigger?
3. What does good output look like?

## Write the SKILL.md

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description, optional compatibility)
│   └── Markdown instructions
├── references/  (optional — docs loaded into context as needed)
└── scripts/  (optional — Python, stdlib only)
```

- **name**: kebab-case identifier, same as the directory name.
- **description**: the only triggering mechanism. State what it does AND when to use it, including contexts where the user wouldn't name it explicitly. Slightly pushy descriptions counter undertriggering: instead of "Builds dashboards", write "Builds internal dashboards. Use whenever the user mentions dashboards, metrics, or displaying company data."
- **compatibility**: optional and rarely needed. Only add it when the skill requires specific tools, commands, or dependencies to be present in the environment (e.g. "requires gh and jq").
- **Body**: instructions only. All "when to use" info goes in the description, not the body.

Place skills in `.agents/skills/<skill-name>/`.

### Writing rules

- Imperative form, explain the *why* instead of stacking MUSTs and NEVERs. Models follow reasoning better than rigid rules.
- Keep the body well under 500 lines. If it grows past that, move detail into `references/*.md` files and point to them with clear guidance on when to read each one. For large reference files (>300 lines), include a table of contents.
- Generalize: instructions should work across many prompts, not just the examples that inspired the skill. Watch for overfitted rules and all-caps rigidness — reframe them.
- Harness-agnostic: don't assume subagents, special tools, browser access, or a specific product. Say "do X yourself or in parallel if the harness allows".
- Scripts, if any, must be Python with stdlib only.

### Domain organization

When a skill supports multiple domains or frameworks, organize by variant so the model only reads what's relevant:

```
cloud-deploy/
├── SKILL.md (workflow + which reference to pick)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

## Test

Ask 1–3 test prompts a real user would type (share them with the user first). Run each by reading the skill and following its instructions yourself — one at a time is fine. Present outputs to the user, ask for feedback, improve, and repeat until they're satisfied. Skip elaborate baselines and metrics unless the user asks.

## Validate

Before finishing, check the skill structurally:

```bash
python .agents/skills/skill-creator/scripts/validate_skill.py <skill-dir>
```

Checks frontmatter format, name conventions, and description limits.

## Editing an existing skill

- Preserve the original name and directory.
- Make targeted edits; don't rewrite wholesale unless asked.
- After each meaningful change, rerun a test prompt and the validator.
