---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit or optimize an existing skill, run evals to test a skill, benchmark skill performance against a baseline, or improve a skill's description for better triggering. Also use this when a user says "turn this into a skill" after a successful workflow.
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

At a high level, the process of creating a skill goes like this:

- Decide what you want the skill to do and roughly how it should do it
- Write a draft of the skill
- Create a few test prompts and run an agent-with-access-to-the-skill on them
- Help the user evaluate the results both qualitatively and quantitatively
- Rewrite the skill based on feedback from the user's evaluation (and any glaring flaws visible in the quantitative results)
- Repeat until you're satisfied
- Expand the test set and try again at larger scale

Your job is to figure out where the user is in this process and jump in to help them progress. Maybe they say "I want a skill for X" — help them narrow it down, draft it, write test cases, run them, and iterate. Maybe they already have a draft — go straight to the eval/iterate part of the loop.

Be flexible: if the user says "I don't need to run a bunch of evaluations, just vibe with me", do that instead. The full evaluation machinery exists to catch things a draft-only workflow misses, not to gate every change.

## Hammock conventions

This skill lives in the hammock repository, which has two project rules that shape how you write and adapt skills here:

1. **Skills live in `.agents/skills/<skill-name>/`** with `SKILL.md` at the root of that directory.
2. **Skills are harness-agnostic.** They must not assume harness-specific features such as subagents, a particular CLI tool, parallel task spawning, or harness-specific tools. Where a workflow benefits from such a feature, describe the preferred path *and* the fallback, so the skill degrades gracefully in any harness.

Keep both rules in mind when writing new skills for this project: state fallbacks explicitly, and bundle only what runs anywhere (e.g. Python 3 stdlib scripts).

## Creating a skill

### Capture intent

Start by understanding the user's intent. The current conversation might already contain a workflow the user wants to capture (e.g. they say "turn this into a skill"). If so, extract answers from the conversation history first — the tools used, the sequence of steps, corrections the user made, input/output formats observed. The user may need to fill the gaps, and should confirm before proceeding.

1. What should this skill enable the agent to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases to verify the skill works? Skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Skills with subjective outputs (writing style, art) often don't need them. Suggest the appropriate default based on the skill type, but let the user decide.

### Interview and research

Proactively ask questions about edge cases, input/output formats, example files, success criteria, and dependencies. Don't write test prompts until this is ironed out.

If the skill resembles existing skills in `.agents/skills/`, read one or two of them first — matching the house style makes the new skill easier to review and maintain. Come prepared with context to reduce burden on the user.

## Writing the SKILL.md

Based on the interview, fill in these components:

- **name**: skill identifier, matching the directory name
- **description**: when to trigger, what it does. This is the primary triggering mechanism — include both what the skill does AND specific contexts for when to use it. All "when to use" info goes here, not in the body. Agents currently tend to *undertrigger* skills — to not use them when they'd be useful. To combat this, make descriptions a little "pushy": instead of "How to build a simple fast dashboard", write "How to build a simple fast dashboard. Use this whenever the user mentions dashboards, data visualization, or displaying metrics, even if they don't explicitly ask for a 'dashboard.'"
- **the rest of the skill :)**

### Anatomy of a skill

```
.agents/skills/skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled resources (optional)
    ├── scripts/    - executable code for deterministic/repetitive tasks
    ├── references/ - docs loaded into context as needed
    └── assets/     - files used in output (templates, icons, fonts)
```

### Progressive disclosure

Skills use a three-level loading system:

1. **Metadata** (name + description) — always in context (~100 words)
2. **SKILL.md body** — in context whenever the skill triggers (<500 lines ideal)
3. **Bundled resources** — as needed (unlimited; scripts can execute without being loaded)

These counts are approximate — going longer is fine when it earns its place.

**Key patterns:**
- Keep SKILL.md under 500 lines; if approaching the limit, add another layer of hierarchy with clear pointers to where the agent should go next.
- Reference files clearly from SKILL.md with guidance on when to read them.
- For large reference files (>300 lines), include a table of contents.

**Domain organization**: when a skill supports multiple domains/frameworks, organize by variant so the agent reads only the relevant file:

```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

### Principle of lack of surprise

Skills must not contain malware, exploit code, or content that could compromise system security. A skill's contents should not surprise the user in their intent. Don't go along with requests to create misleading skills or skills designed to facilitate unauthorized access, data exfiltration, or other malicious activities. Things like "roleplay as an XYZ" are OK though.

### Writing patterns

Prefer the imperative form in instructions.

**Defining output formats:**
```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**Examples** are useful. Format them like this (deviate if Input/Output don't fit):
```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### Writing style

Explain *why* things matter instead of stacking heavy-handed MUSTs. Today's models are smart: given reasoning rather than rote rules, they generalize far better. If you catch yourself writing ALWAYS or NEVER in caps, or super-rigid structures, that's a yellow flag — reframe and explain the reasoning instead. Make the skill general, not overfitted to specific examples. Write a draft, then reread it with fresh eyes and improve it.

## Test cases

After writing the draft, come up with 2-3 realistic test prompts — the kind of thing a real user would actually say. Share them with the user: "Here are a few test cases I'd like to try. Do these look right, or do you want to add more?" Then run them.

Save test cases to `evals/evals.json` inside the skill directory. Don't write assertions yet — just the prompts. You'll draft assertions while the runs are in progress.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

See `references/schemas.md` for the full schema (including the `expectations` field, which you'll add later).

## Running and evaluating test cases

Put results in `<skill-name>-workspace/` as a sibling of the skill directory (for skills in this repo: `.agents/skills/<skill-name>-workspace/`). Within the workspace, organize by iteration (`iteration-1/`, `iteration-2/`, ...) and within that, each test case gets a directory with a descriptive name (`eval-0-descriptive-name/`, ...). Create directories as you go, not upfront.

### Step 0: choose an execution mode

Different harnesses offer different ways to run test cases. Pick the best mode available, in this order of preference:

- **Mode A — parallel isolated runs**: the harness supports spawning subagents or background tasks. Run each test case in its own agent, all launched at once. Most rigorous: the executing agent has no knowledge of the skill's intent beyond what the skill provides.
- **Mode B — sequential isolated runs**: you can start a fresh session per test case but not in parallel. Same rigor, slower.
- **Mode C — inline**: you have no isolation mechanism. Read the skill's SKILL.md, then follow its instructions to accomplish each test prompt yourself, one at a time. You wrote the skill and you're also running it, so you have full context — a useful sanity check, not a rigorous test. The human review step compensates.

Whichever mode you use, state the choice to the user so they know how rigorous the results are.

### Step 1: run all configurations at once

For each test case, run two configurations — one with the skill, one without:

- **Creating a new skill**: baseline is no skill at all. Same prompt, no skill, save to `without_skill/outputs/`.
- **Improving an existing skill**: baseline is the old version. Before editing, snapshot the skill (`cp -r <skill-path> <workspace>/skill-snapshot/`), then point baseline runs at the snapshot. Save to `old_skill/outputs/`.

Baselines make the comparison meaningful — they tell you whether the skill actually adds value rather than whether the task is doable. In Mode C, skip baselines (you can't run yourself "without knowing what you know") and rely on qualitative review; say so when presenting results.

Launch everything as early as possible: in Mode A, spawn all runs (with-skill AND baseline) in the same turn so they finish around the same time; in Mode B, run them in a fixed order (all with-skill runs, then all baselines) before grading anything.

Each run saves its outputs to:

```
<workspace>/iteration-<N>/eval-<ID>-<name>/<with_skill|without_skill|old_skill>/outputs/
```

Also write an `eval_metadata.json` per test case:

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "expectations": []
}
```

If this iteration uses new or modified prompts, create these files fresh — don't assume they carry over.

### Step 2: while runs are in progress, draft expectations

Use the waiting time productively. Draft quantitative expectations for each test case — statements that are objectively verifiable — and explain them to the user. If expectations already exist in `evals/evals.json`, review them and explain what they check.

Good expectations are discriminating: they pass when the skill genuinely succeeds and fail when it doesn't. "The output includes the name 'John Smith'" is weak (a hallucinated document that mentions the name also passes); "the extracted phone numbers match the input" is strong. Subjective skills (writing style, design) are better evaluated qualitatively — don't force expectations onto things that need human judgment.

Update the `eval_metadata.json` files and `evals/evals.json` once drafted, and explain to the user what they'll see in the viewer — both the qualitative outputs and the quantitative benchmark.

### Step 3: capture timing data (best effort)

If the harness reports metrics when a run completes (total tokens, duration), save them immediately to `timing.json` in the run directory:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

This data often comes through a task notification and isn't persisted elsewhere — capture it as each run finishes rather than batching. If the harness reports nothing, skip this; the aggregation script degrades gracefully without it.

### Step 4: grade, aggregate, analyze, and launch the viewer

Once all runs are done:

1. **Grade each run** — evaluate each expectation against the run's transcript and outputs, following `references/grading.md`. Save results to `grading.json` in each run directory. The expectations array must use the fields `text`, `passed`, and `evidence` (the viewer depends on these exact names). For expectations checkable programmatically, write and run a script rather than eyeballing it — scripts are faster, more reliable, and reusable across iterations. Grading can be done inline or, if the harness supports it, delegated to a fresh session for independence.

2. **Aggregate into a benchmark** — from the skill-creator directory, run:
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```
   This produces `benchmark.json` and `benchmark.md` with pass_rate, time, and tokens per configuration, as mean ± stddev plus the delta. `with_skill` appears before its baseline counterpart.

3. **Do an analysis pass** — read the benchmark data and surface patterns the aggregate stats hide. Follow the "Analyzing Benchmark Results" guidance in `references/analysis.md`: assertions that always pass regardless of skill (non-discriminating), high-variance evals (possibly flaky), time/token tradeoffs. Save notes into `benchmark.json` (the schema in `references/schemas.md` has the `notes` field).

4. **Generate the eval viewer** — do this BEFORE evaluating the outputs yourself. The user should see raw results before reading your interpretation:
   ```bash
   python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json
   ```
   For iteration 2+, also pass `--previous-workspace <workspace>/iteration-<N-1>`.

   If the harness has no display or browser access, use `--static <output_path>` to write a standalone HTML file instead of starting a server, and give the user the path. The "Submit All Reviews" button then downloads `feedback.json` instead of POSTing to the server; copy it into the workspace for the next iteration.

   Use `generate_review.py` as-is; there's no need to write custom HTML.

5. **Tell the user** something like: "I've opened the results in your browser. There are two tabs — 'Outputs' lets you click through each test case and leave feedback, 'Benchmark' shows the quantitative comparison. When you're done, come back and let me know."

### What the user sees in the viewer

The "Outputs" tab shows one test case at a time:

- **Prompt**: the task that was given
- **Output**: the files the skill produced, rendered inline where possible
- **Previous Output** (iteration 2+): collapsed section showing last iteration's output
- **Formal Grades** (if grading was run): collapsed section showing expectation pass/fail
- **Feedback**: a textbox that auto-saves as they type
- **Previous Feedback** (iteration 2+): their comments from last time, shown below the textbox

The "Benchmark" tab shows the stats summary: pass rates, timing, and token usage per configuration, with per-eval breakdowns and analysis notes.

Navigation is via prev/next buttons or arrow keys. When done, they click "Submit All Reviews" which saves all feedback to `feedback.json`.

### Step 5: read the feedback

When the user says they're done, read `feedback.json` from the workspace (or the downloaded file in static mode):

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback means the user thought it was fine. Focus improvements on the test cases with specific complaints.

If a viewer server is running, kill it when done:

```bash
kill $VIEWER_PID 2>/dev/null
```

## Improving the skill

This is the heart of the loop. You've run the test cases, the user has reviewed the results, and now you improve the skill based on their feedback.

### How to think about improvements

1. **Generalize from the feedback.** You're trying to create a skill that works across many different prompts. Here you and the user iterate on a few examples because it's fast — the user knows them in and out. But a skill that only works for those examples is useless. Rather than fiddly overfitted changes or oppressive constrictive MUSTs, if there's a stubborn issue, try branching out: different metaphors, different patterns of working. It's cheap to try and you might land on something great.

2. **Keep the prompt lean.** Remove things that aren't pulling their weight. Read the transcripts, not just the final outputs — if the skill makes the model waste time on unproductive detours, cut the parts causing that.

3. **Explain the why.** Transmit understanding, not just instructions. If the user's feedback is terse or frustrated, still work out what they actually meant and why, and encode that reasoning in the skill.

4. **Look for repeated work across test cases.** If the runs all independently wrote similar helper scripts or took the same multi-step approach, that's a strong signal the skill should bundle that script in `scripts/` and tell the skill to use it. This saves every future invocation from reinventing the wheel.

Take your time — write a draft revision, then reread it with fresh eyes and improve it again.

### The iteration loop

After improving the skill:

1. Apply your improvements to the skill
2. Rerun all test cases into a new `iteration-<N+1>/` directory, including baselines. For a new skill the baseline is always `without_skill`; for an improving skill, use your judgment between the original version and the previous iteration.
3. Generate the viewer with `--previous-workspace` pointing at the previous iteration
4. Wait for the user to review and tell you they're done
5. Read the new feedback, improve again, repeat

Keep going until the user says they're happy, the feedback is all empty, or you're not making meaningful progress.

## Advanced: blind comparison

For a more rigorous comparison between two versions of a skill (e.g. "is the new version actually better?"), give two outputs to an independent agent — a fresh session, if the harness supports it — without telling it which is which, and let it judge quality against a rubric it derives from the task. Then analyze why the winner won. This needs Mode A or B isolation and most users won't need it; the human review loop is usually sufficient.

## Description triggering

The description field in SKILL.md frontmatter is the primary mechanism that determines whether an agent invokes a skill. Two things are worth knowing:

- Skills appear in the agent's available-skills list with their name + description, and the agent decides whether to consult a skill based on that description. It only consults skills for tasks it can't easily handle on its own — simple one-step queries may not trigger a skill even when the description matches. This is why eval queries should be substantive.
- Undertriggering is the common failure mode, hence the "pushy description" guidance in "Writing the SKILL.md".

After creating or improving a skill, you can check triggering:

1. Draft ~20 realistic queries — a mix of should-trigger and should-not-trigger — covering different phrasings, casual speech, edge cases, and near-misses (queries sharing keywords with the skill but actually needing something else). Avoid obviously irrelevant negatives like "write a fibonacci function"; they don't test anything. Save as JSON: `[{"query": "...", "should_trigger": true}, ...]`.
2. Review the set with the user — bad queries lead to bad conclusions.
3. If the harness has a non-interactive mode (e.g. running the agent headless with a prompt), test each query in a fresh session and record whether the skill was consulted. Otherwise, reason through the queries with the user and refine the description manually.

## Packaging (optional)

To distribute a skill as a single `.skill` file (a zip), from the skill-creator directory:

```bash
python -m scripts.package_skill <path/to/skill-folder> [output-directory]
```

This validates the SKILL.md frontmatter first (`scripts/quick_validate.py`) and excludes workspace/eval cruft from the package. Useful when a skill written here will be installed into users' agents elsewhere.

## Reference files

Read these when you reach the relevant step:

- `references/schemas.md` — JSON structures for evals.json, grading.json, benchmark.json, etc.
- `references/grading.md` — how to grade expectations against outputs and critique the evals themselves
- `references/analysis.md` — how to analyze benchmark results for patterns the aggregates hide
- `eval-viewer/` — the human review tool (`generate_review.py` + `viewer.html`)

---

The core loop, one more time:

- Figure out what the skill is about
- Draft or edit the skill
- Run agent-with-access-to-the-skill on test prompts
- Evaluate with the user: eval viewer for qualitative review, aggregate benchmark for quantitative
- Repeat until you and the user are satisfied
- Package and hand off the final skill if requested

---

## Provenance

This skill is adapted from [skill-creator](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator/skills/skill-creator) (Apache-2.0, see `LICENSE.txt`). Changes for hammock:

- Removed harness-specific paths: the Claude Code/Cowork/Claude.ai sections, subagent-based workflows (run-instructions files under `agents/`), and the `claude -p`-driven description-optimization scripts (`run_eval.py`, `run_loop.py`, `improve_description.py`, `generate_report.py`, `assets/eval_review.html`). Test execution is now described via execution modes A/B/C with explicit fallbacks, per ARCHITECTURE.md's harness-agnostic rule.
- Kept everything that runs anywhere: `scripts/` (made stdlib-only — PyYAML dependency removed from `quick_validate.py`), `eval-viewer/` (with a `--static` fallback for display-less environments), and the JSON schema/reference docs.
- `agents/grader.md` and the benchmark-analysis half of `agents/analyzer.md` became harness-agnostic references (`references/grading.md`, `references/analysis.md`).
- Added hammock conventions: skills live in `.agents/skills/<name>/`, and skill authors must follow the same harness-agnostic rule.
