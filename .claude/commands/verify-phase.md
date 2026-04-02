# /verify-phase

Run the verification checklist for the current build phase.

## Instructions

1. Read @PROGRESS.md to determine current phase
2. Read @docs/BUILD_CHECKLISTS.md for the relevant checklist
3. Run through each checklist item:
   - Check if the file/table/endpoint exists
   - Run tests if applicable
   - Report pass or fail for each item
4. Output a summary: total items, passed, failed, items needing attention

## Output Format

Phase: [current phase name]
Total items: X
Passed: X
Failed: X

Failing items:
- [item] — [what's needed to fix it]

## Notes

- Check actual files on disk, don't assume
- Run pytest for test-related items
- For DB items, check models/__init__.py and alembic migrations
- For endpoint items, check routers are registered in app/api/__init__.py
