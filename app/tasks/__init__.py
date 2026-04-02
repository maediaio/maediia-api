"""ARQ background task functions.

All functions in this package are registered with the ARQ worker.
Each function receives `ctx` as its first argument — populated by WorkerSettings.on_startup.

ctx keys available to all tasks:
- ctx['db'] — AsyncSession factory (call async with ctx['db']() as session:)
"""
