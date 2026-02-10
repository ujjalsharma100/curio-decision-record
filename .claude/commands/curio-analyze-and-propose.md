# Analyze & Propose Decisions

Analyze this codebase alongside all existing decision records, consider the provided context, then propose new decisions or records where gaps exist or improvements are needed.

User-provided context (resources, goals, or areas of focus):
$ARGUMENTS

## Step-by-step process

### 1. Gather current state
- Call `get_project` to confirm the workspace project.
- Call `list_decisions` to retrieve ALL existing decisions and their records.
- For each decision that looks relevant, call `get_decision` to see full record details.
- Review the existing decisions carefully — understand what has already been decided, what's proposed, what's accepted, and what's implemented.

### 2. Analyze the codebase
- Explore the codebase structure, architecture, and implementation patterns.
- Look for areas where:
  - Significant decisions exist in code but have no corresponding decision record
  - Existing decisions may need new alternative records (e.g., a better approach has emerged)
  - Architectural gaps or risks are not captured in any decision
  - Implemented decisions have drifted from their documented intent

### 3. Incorporate resources and intent
If the user provided resources (URLs, papers, docs, RFCs) above:
- Read and analyze each resource thoroughly.
- Understand what they propose, recommend, or demonstrate.
- Consider how they relate to the current codebase and existing decisions.
- Use insights from these resources to inform your proposals.

If the user stated goals or intent above:
- Prioritize your analysis and proposals around those goals.
- Ensure every proposal clearly ties back to how it supports or relates to the stated intent.

If no context was provided, perform a broad analysis looking for missing decisions, improvement opportunities, and risks.

### 4. Propose new decisions and records
For each gap or improvement identified:
1. If a new decision topic is needed, call `create_decision` with a clear title.
2. Call `create_record` with `status="proposed"` and fill ALL fields thoroughly — this is a proposal, quality matters:

   - **decision_description**: A precise statement of what is being proposed.
   - **context**: Why this decision needs to be made now. What situation, pressure, or trigger necessitates it? Be specific about the current state.
   - **constraints**: What hard requirements must be met? What limitations exist in the current system?
   - **rationale**: Why you are recommending this specific approach over alternatives. Be detailed and persuasive.
   - **assumptions**: What must be true for this proposal to be valid. Be explicit — these are the conditions under which someone should revisit this decision.
   - **consequences**: What will happen downstream if this is adopted, both good and bad. Be honest about costs.
   - **tradeoffs**: What is explicitly being given up. Every decision has costs — name them.
   - **evidence**: Any references that support this proposal — papers, benchmarks, docs, blog posts, or patterns observed in the codebase.
   - **options_considered**: List every alternative you evaluated and why it was not recommended. This prevents future teams from re-proposing rejected ideas.

3. Use `manage_decision_relationship` to link new proposals to existing decisions where relevant (e.g., `related_to`, `supersedes`, `depends_on`).

### 5. Present proposals
For each proposal, present:
- The decision title and proposed record description
- A brief summary of why this proposal matters
- Key assumptions that would need to hold
- Relationship to existing decisions

## Important guidelines
- **Don't duplicate**: Check existing decisions before proposing. If a decision already covers a topic, consider whether a new record for that decision is more appropriate than a new decision entirely.
- **Be opinionated but honest**: Propose what you believe is best, but make tradeoffs visible. Don't hide costs.
- **Assumptions are critical**: The most valuable part of a proposal is often the assumptions — they tell reviewers exactly when this decision should be revisited.
- **Link everything**: Decisions rarely exist in isolation. Create relationships to show how proposals connect to the existing decision landscape.
