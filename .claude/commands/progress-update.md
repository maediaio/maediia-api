# /progress-update

## Purpose
Update PROGRESS.md with current build status.

## Usage
```
@progress-update

Just completed:
- Set up FastAPI app factory
- Added health check endpoint
- Configured database connection
```
```

## What It Does

1. Reads `PROGRESS.md`
2. Updates the current phase section
3. Moves items between Todo/In Progress/Done
4. Updates build stats

## Template

```markdown
## Phase X: [Name] [STATUS]

**Goal:** [One sentence]

### Completed
- [x] [Item]

### In Progress
- [ ] [Item]

### Blockers
- [Blocker description]

---
```

## Build Stats

Update these at end of each session:

| Metric | Value |
|--------|-------|
| Current Phase | [0-3] |
| Completion | [%] |
| Last Session | [YYYY-MM-DD] |
| Blockers | [count] |
