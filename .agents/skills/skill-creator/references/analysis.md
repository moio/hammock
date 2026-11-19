# Analyzing benchmark results

Run this analysis pass after aggregating benchmark data (Step 4 of the eval loop). Its purpose is to **surface patterns and anomalies** across multiple runs, not to suggest skill improvements — improvement comes in the next step, informed by both this analysis and the user's feedback.

This pass is done inline by the agent running the skill-creator workflow.

## Inputs

- **benchmark_data_path**: path to `benchmark.json` with all run results
- **skill_path**: path to the skill being benchmarked
- **output_path**: where to save the notes (JSON array of strings; this lands in the `notes` field of `benchmark.json` — see `references/schemas.md`)

## Process

### Step 1: read the benchmark data

1. Read `benchmark.json` containing all run results
2. Note the configurations tested (`with_skill`, `without_skill` / `old_skill`)
3. Understand the run_summary aggregates already calculated

### Step 2: analyze per-expectation patterns

For each expectation across all runs:
- Does it **always pass** in both configurations? (may not differentiate skill value)
- Does it **always fail** in both configurations? (may be broken or beyond capability)
- Does it **always pass with skill but fail without**? (skill clearly adds value here)
- Does it **always fail with skill but pass without**? (skill may be hurting)
- Is it **highly variable**? (flaky expectation or non-deterministic behavior)

### Step 3: analyze cross-eval patterns

- Are certain eval types consistently harder/easier?
- Do some evals show high variance while others are stable?
- Are there surprising results that contradict expectations?

### Step 4: analyze metrics patterns

Look at time_seconds, tokens, tool_calls:
- Does the skill significantly increase execution time?
- Is there high variance in resource usage?
- Are there outlier runs that skew the aggregates?

### Step 5: generate notes

Write freeform observations as a list of strings. Each note should:
- State a specific observation
- Be grounded in the data (not speculation)
- Help the user understand something the aggregate metrics don't show

Examples:
- "Expectation 'Output is a PDF file' passes 100% in both configurations — may not differentiate skill value"
- "Eval 3 shows high variance (50% ± 40%) — run 2 had an unusual failure that may be flaky"
- "Without-skill runs consistently fail on table extraction expectations (0% pass rate)"
- "Skill adds 13s average execution time but improves pass rate by 50%"
- "Token usage is 80% higher with skill, primarily due to script output parsing"
- "All 3 without-skill runs for eval 1 produced empty output"

### Step 6: write notes

Save the notes array to `{output_path}` as JSON:

```json
[
  "Expectation 'Output is a PDF file' passes 100% in both configurations — may not differentiate skill value",
  "Eval 3 shows high variance (50% ± 40%) — run 2 had an unusual failure",
  "Without-skill runs consistently fail on table extraction expectations",
  "Skill adds 13s average execution time but improves pass rate by 50%"
]
```

## Guidelines

**DO:**
- Report what you observe in the data
- Be specific about which evals, expectations, or runs you're referring to
- Note patterns that aggregate metrics would hide
- Provide context that helps interpret the numbers

**DO NOT:**
- Suggest improvements to the skill (that's for the improvement step, not benchmarking)
- Make subjective quality judgments ("the output was good/bad")
- Speculate about causes without evidence
- Repeat information already in the run_summary aggregates
