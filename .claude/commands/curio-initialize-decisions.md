# Initialize & Infer Decisions

Analyze this codebase thoroughly and create decision records for every significant architectural or design decision that is already reflected in the code. These are recorded as `implemented_inferred` so the team has a living record of decisions that were made — even if they were never formally documented.

## Step-by-step process

### 1. Verify project setup
- Call `get_project` to check if a project is already configured for this workspace.
- If no project exists, call `init_project` with a descriptive name for this codebase.

### 2. Explore the codebase
Systematically analyze the codebase to identify architectural and design decisions. Look at:
- **Languages & frameworks**: What languages, frameworks, and runtimes are used? (e.g., Python + Flask, React + Vite)
- **Database & storage**: What databases, caches, or storage systems are in use? (e.g., PostgreSQL, Redis, S3)
- **Architecture patterns**: Monolith vs microservices, REST vs GraphQL, MVC vs other patterns
- **Infrastructure & deployment**: Docker, Kubernetes, serverless, CI/CD pipelines
- **Authentication & security**: Auth mechanisms, encryption, access control patterns
- **API design**: REST conventions, versioning strategy, error handling patterns
- **Testing strategy**: Unit tests, integration tests, E2E tests, testing frameworks
- **Code organization**: Monorepo vs polyrepo, folder structure conventions, module boundaries
- **Dependencies**: Key libraries chosen (ORM, HTTP client, logging, etc.) and why those over alternatives
- **Configuration**: How config is managed (env vars, config files, secrets management)

Read key files like package.json, requirements.txt, Cargo.toml, Dockerfile, docker-compose.yml, CI configs, and entry points to understand what is in use.

### 3. Create decisions and records
For each significant decision identified:
1. Call `create_decision` with a clear, descriptive title (e.g., "Use PostgreSQL as primary database", "Adopt Flask for backend API").
2. Call `create_record` with `status="implemented_inferred"` and fill in as many fields as you can infer:

   - **decision_description**: A concise statement of what was decided.
   - **context**: Why this decision was likely made — the situation or pressures at the time. Even if you're inferring, reason about what would have motivated this choice.
   - **constraints**: Hard requirements the decision satisfies (e.g., "Must integrate with existing Python services", "Must support ACID transactions").
   - **rationale**: Why this option was chosen over alternatives, based on what you can observe in the code and ecosystem.
   - **assumptions**: What must remain true for this decision to stay valid (e.g., "Team has Python expertise", "Data model remains primarily relational").
   - **consequences**: Observable impacts — both positive (e.g., "Enables rapid prototyping") and negative (e.g., "Requires PostgreSQL expertise for operations").
   - **tradeoffs**: What was given up (e.g., "Traded NoSQL flexibility for relational guarantees").
   - **evidence**: Links to relevant docs, benchmarks, or the specific files/patterns that reveal this decision.
   - **options_considered**: Plausible alternatives that were likely evaluated (e.g., "MySQL — similar but fewer advanced features", "MongoDB — not suitable for relational data").

### 4. Create relationships
After creating all decisions, identify relationships between them:
- Use `manage_decision_relationship` to link related decisions.
- Common relationships: `depends_on` (one decision requires another), `related_to` (decisions are connected), `derived_from` (one builds on another).
- Example: "Use React for frontend" `related_to` "Use Vite as build tool".

### 5. Present summary
After completing all records, present a clear summary:
- Total number of decisions created
- For each: title, brief description, and which fields were populated
- Any relationships created
- Areas where you were uncertain or where the team should review and refine the inferred records

## Important guidelines
- **Be thorough**: Capture every significant decision, not just the obvious ones.
- **Be honest about uncertainty**: If you're inferring context or rationale, note that. The team can refine these later.
- **Quality over quantity for fields**: It's better to leave a field empty than to fill it with vague content.
- **Use implemented_inferred status**: This distinguishes decisions inferred from code vs. ones that went through a formal proposal process.
