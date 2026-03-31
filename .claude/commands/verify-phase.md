# /verify-phase

## Purpose
Run the verification checklist for the current build phase.

## Usage
```
@verify-phase
```

## Current Phase: Foundation (Phase 0)

### Checklist

- [ ] Project structure matches conventions
- [ ] CLAUDE.md is populated with context
- [ ] PROGRESS.md is up to date
- [ ] `.claude/rules/` contains all required modules
- [ ] `.env.example` has all required variables
- [ ] `requirements.txt` has base dependencies
- [ ] `README.md` has setup instructions

### How to Update

1. Edit `CLAUDE.md` with current context
2. Edit `PROGRESS.md` with completion status
3. Run `@verify-phase` again

## Next Phase

Once all boxes are checked, move to **Phase 1: Core API Skeleton**
