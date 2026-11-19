# Grading expectations

Evaluate expectations against a run's transcript and outputs. Grading can be done inline by the agent running the skill-creator workflow, or — for more independence — delegated to a fresh session with this reference as instructions.

You have two jobs: grade the outputs, and critique the evals themselves. A passing grade on a weak expectation is worse than useless — it creates false confidence. When you notice an expectation that's trivially satisfied, or an important outcome that no expectation checks, say so.

## Inputs

- **expectations**: list of expectations to evaluate (strings)
- **transcript_path**: path to the execution transcript (markdown file), if one was captured
- **outputs_dir**: directory containing output files from execution

A transcript may not exist in every harness — when it doesn't, grade from the outputs alone and note that evidence is output-only.

## Process

### Step 1: read the transcript (if available)

1. Read the transcript file completely
2. Note the eval prompt, execution steps, and final result
3. Identify any issues or errors documented

### Step 2: examine output files

1. List files in `outputs_dir`
2. Read/examine each file relevant to the expectations. If outputs aren't plain text, inspect them with available tools — don't rely solely on what a transcript says the executor produced.
3. Note contents, structure, and quality

### Step 3: evaluate each expectation

For each expectation:

1. **Search for evidence** in the transcript and outputs
2. **Determine verdict**:
   - **PASS**: clear evidence the expectation is true AND the evidence reflects genuine task completion, not just surface-level compliance
   - **FAIL**: no evidence, or evidence contradicts the expectation, or the evidence is superficial (e.g. correct filename but empty/wrong content)
3. **Cite the evidence**: quote the specific text or describe what you found

### Step 4: extract and verify claims

Beyond the predefined expectations, extract implicit claims from the outputs and verify them:

1. **Extract claims** from the transcript and outputs:
   - Factual statements ("The form has 12 fields")
   - Process claims ("Used pypdf to fill the form")
   - Quality claims ("All fields were filled correctly")
2. **Verify each claim**:
   - **Factual claims**: check against the outputs or external sources
   - **Process claims**: verify from the transcript
   - **Quality claims**: evaluate whether the claim is justified
3. **Flag unverifiable claims**: note claims that cannot be verified with available information

This catches issues that predefined expectations might miss.

### Step 5: read user notes

If `{outputs_dir}/user_notes.md` exists:
1. Read it and note any uncertainties or issues flagged by the executor
2. Include relevant concerns in the grading output
3. These may reveal problems even when expectations pass

### Step 6: critique the evals

After grading, consider whether the evals themselves could be improved. Only surface suggestions when there's a clear gap.

Good expectations test meaningful outcomes — they're hard to satisfy without actually doing the work correctly. Suggestions worth raising:

- An expectation that passed but would also pass for a clearly wrong output (e.g. checking filename existence but not file content)
- An important outcome you observed — good or bad — that no expectation covers at all
- An expectation that can't actually be verified from the available outputs

Keep the bar high. Flag things the eval author would say "good catch" about, not nitpicks.

### Step 7: write grading results

Save results to `{outputs_dir}/../grading.json` (sibling to `outputs_dir`). The `expectations` array must use exactly the fields `text`, `passed`, `evidence` — the eval viewer depends on these names.

```json
{
  "expectations": [
    {
      "text": "The output includes the name 'John Smith'",
      "passed": true,
      "evidence": "Found in transcript Step 3: 'Extracted names: John Smith, Sarah Johnson'"
    },
    {
      "text": "The spreadsheet has a SUM formula in cell B10",
      "passed": false,
      "evidence": "No spreadsheet was created. The output was a text file."
    }
  ],
  "summary": {
    "passed": 1,
    "failed": 1,
    "total": 2,
    "pass_rate": 0.5
  },
  "claims": [
    {
      "claim": "The form has 12 fillable fields",
      "type": "factual",
      "verified": true,
      "evidence": "Counted 12 fields in field_info.json"
    }
  ],
  "user_notes_summary": {
    "uncertainties": ["Used 2023 data, may be stale"],
    "needs_review": [],
    "workarounds": ["Fell back to text overlay for non-fillable fields"]
  },
  "eval_feedback": {
    "suggestions": [
      {
        "assertion": "The output includes the name 'John Smith'",
        "reason": "A hallucinated document that mentions the name would also pass — consider checking it appears as the primary contact with matching phone and email from the input"
      }
    ],
    "overall": "Assertions check presence but not correctness. Consider adding content verification."
  }
}
```

All sections except `expectations` and `summary` are optional — omit what you couldn't collect rather than inventing it. If timing data was captured in `timing.json`, include it under a `timing` key; if the executor wrote `metrics.json` into `outputs_dir`, include it under `execution_metrics`.

### Grading criteria

**PASS when**:
- The transcript or outputs clearly demonstrate the expectation is true
- Specific evidence can be cited
- The evidence reflects genuine substance, not just surface compliance (a file exists AND contains correct content, not just the right filename)

**FAIL when**:
- No evidence found for the expectation
- Evidence contradicts the expectation
- The expectation cannot be verified from available information
- The evidence is superficial — technically satisfied but the underlying task outcome is wrong or incomplete
- The output appears to meet the expectation by coincidence rather than by actually doing the work

**When uncertain**: the burden of proof to pass is on the expectation.

## Guidelines

- **Be objective**: base verdicts on evidence, not assumptions
- **Be specific**: quote the exact text that supports your verdict
- **Be thorough**: check both transcript and output files
- **Be consistent**: apply the same standard to each expectation
- **Explain failures**: make it clear why evidence was insufficient
- **No partial credit**: each expectation is pass or fail
