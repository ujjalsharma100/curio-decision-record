# Implement Decision

Take an accepted decision and implement it in the codebase, respecting all documented constraints, assumptions, and tradeoffs. After implementation, update the decision record status.

Decision to implement (title or leave blank to list all accepted decisions):
$ARGUMENTS

## Step-by-step process

### 1. Identify the decision to implement
If a decision title was specified above:
- Call `get_decision(decision_title="<the title>")` to retrieve the full decision with all records.
- Find the `accepted` record for this decision. If there is no accepted record, inform the user — only accepted decisions should be implemented.

If no title was specified:
- Call `list_decisions(status="accepted")` to show all decisions with accepted records ready for implementation.
- Present the list to the user and ask which one to implement.
- Once selected, call `get_decision(decision_title=...)` to retrieve full details.

### 2. Study the decision record thoroughly
Before writing any code, read and internalize every field of the accepted record:
- **decision_description**: This is exactly what needs to be implemented.
- **context**: Understand why this decision was made — it affects how you implement it.
- **constraints**: These are non-negotiable. Your implementation MUST satisfy every stated constraint.
- **rationale**: Understand the reasoning so your implementation aligns with the intent.
- **assumptions**: Verify these are still true before proceeding. If any assumption is no longer valid, STOP and inform the user — the decision may need to be re-evaluated before implementation.
- **tradeoffs**: Be aware of what was intentionally given up. Don't accidentally try to "fix" an intentional tradeoff.
- **options_considered**: Understand what was rejected and why, so you don't accidentally implement a rejected approach.
- **evidence**: Review any linked resources for implementation guidance.

Also check for related decisions:
- Call `list_decision_relationships` or `list_decision_record_relationships` to see dependencies.
- If this decision `depends_on` another, verify that dependency is implemented first.

### 3. Plan the implementation
Before coding:
- Identify which files need to be created or modified.
- Plan the changes in a logical order.
- Ensure the plan respects all constraints.
- Identify any tests that need to be written or updated.

### 4. Implement the changes
- Write clean, well-structured code that matches the codebase's existing patterns and conventions.
- Add appropriate comments referencing the decision where it helps future readers understand why something was done a certain way.
- Write or update tests as needed.
- Update any relevant documentation.

### 5. Verify the implementation
- Run existing tests to make sure nothing is broken.
- Verify that every stated constraint is satisfied.
- Confirm that the assumptions listed in the record still hold.
- Check that you haven't accidentally reintroduced something that was an intentional tradeoff.

### 6. Update the decision record
- Call `change_record_status` with `status="implemented"` and provide a descriptive reason summarizing what was done (e.g., "Implemented PostgreSQL migration: added models in backend/models.py, migration in migrations/001_initial.sql, updated docker-compose.yml").
- If the implementation required any deviations from the original proposal, call `update_decision_record` to update relevant fields (e.g., update constraints if new ones were discovered, update consequences if new impacts were found).

### 7. Present summary
Report what was done:
- Files created or modified
- Key implementation decisions made during coding
- Tests added or updated
- Any deviations from the original decision record (and why)
- The status change made

## Important guidelines
- **Constraints are non-negotiable**: If you cannot satisfy a stated constraint, stop and discuss with the user rather than silently violating it.
- **Check assumptions first**: If an assumption is no longer valid, the decision itself may be invalid. Don't implement a decision built on false assumptions.
- **Respect tradeoffs**: The decision record may explicitly say "we give up X for Y." Don't try to have both unless you're proposing a new decision.
- **One decision at a time**: Focus on implementing the single specified decision. If you discover other decisions are needed, note them but don't scope-creep.
- **Update the record**: The implementation is not complete until the status is updated. This closes the loop.
