# Evaluate Decisions

Audit the codebase against all existing decision records and update statuses where appropriate. This includes promoting accepted decisions that have been implemented, deprecating decisions no longer reflected in code, and flagging assumptions that may have been invalidated.

## Step-by-step process

### 1. Gather all decisions
- Call `get_project` to confirm the workspace project.
- Call `list_decisions` to get ALL decisions.
- For each decision, call `get_decision` to retrieve full record details including all fields.

### 2. Evaluate accepted records — should any be marked implemented?
For each record with status `accepted`:
- Read the decision_description, constraints, and rationale carefully.
- Search the codebase for evidence that this decision has been implemented.
- Look for: relevant code files, configuration, dependencies, tests, documentation that match what was decided.
- **If the decision is clearly implemented in code**: Call `change_record_status` with `status="implemented"` and provide a reason explaining what evidence you found (e.g., "Found PostgreSQL configuration in docker-compose.yml and SQLAlchemy models in backend/models.py").
- **If partially implemented**: Do NOT change status. Instead, note what is done and what remains.

### 3. Evaluate proposed records — any already implemented?
For each record with status `proposed`:
- Check if the proposed change has already been implemented (perhaps by someone who didn't update the record).
- **If implemented**: Call `change_record_status` to first move to `accepted` then to `implemented`, or note that the workflow requires acceptance first.
- **If clearly not going to happen**: Consider whether it should be `rejected` and flag it for team review.

### 4. Evaluate implemented records — should any be deprecated?
For each record with status `implemented` or `implemented_inferred`:
- Check if the decision is still reflected in the current codebase.
- Look for: Has the technology been replaced? Has the pattern been abandoned? Has the configuration changed?
- **If the decision is no longer reflected in code**: Call `change_record_status` with `status="deprecated"` and provide a reason explaining what changed (e.g., "Flask backend has been replaced with FastAPI — see backend/main.py").
- **If still valid**: Leave as is.

### 5. Evaluate assumptions — are any invalidated?
This is the most critical evaluation step. For EVERY record (regardless of status):
- Read the `assumptions` field carefully.
- For each assumption stated, evaluate whether it still holds true:
  - Check the codebase for evidence
  - Consider the current technology landscape
  - Look for changes that may have invalidated assumptions
- **If assumptions are invalidated**: Flag the decision prominently. This does not automatically change status, but it means the decision should be reviewed. Use `update_decision_record` to add a note in the context or use the relationship tools to flag it.

### 6. Present evaluation report
Present a clear, structured report:

**Status Changes Made:**
- List each status change with the decision title, record description, old status, new status, and reason.

**Assumptions Flagged:**
- List each decision where assumptions may be invalidated, with the specific assumption and why you believe it may no longer hold.

**No Changes Needed:**
- Briefly note decisions that were evaluated and found to be current and valid.

**Recommendations:**
- Any decisions that need team attention but where you couldn't make a definitive status change.

## Important guidelines
- **Be conservative with status changes**: Only change status when you have clear evidence. When in doubt, flag for human review rather than making the change.
- **Assumptions are the highest-value check**: A decision can have the right status but invalid assumptions — that's a ticking time bomb. Always evaluate assumptions thoroughly.
- **Provide evidence**: Every status change should include specific evidence (file paths, code patterns, configuration) that justifies the change.
- **Don't skip any decisions**: Every decision and record should be evaluated, even if it seems obviously current.
