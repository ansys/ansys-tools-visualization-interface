# Task 1 Report: Update `pyproject.toml` — add `usd-core` dependency

## Summary

Task 1 completed successfully. The `pyproject.toml` file has been updated to include `usd-core >= 24.0` in the `[usd]` optional dependency group.

## Changes Made

### File: `pyproject.toml`

**Before:**
```toml
usd = [
    "ansys-tools-usdviewer >= 0.1.0,< 1"
]
```

**After:**
```toml
usd = [
    "ansys-tools-usdviewer >= 0.1.0,< 1",
    "usd-core >= 24.0"
]
```

## Verification Steps

✅ **Step 1: Edit `pyproject.toml`**
- Updated the `[usd]` optional dependency group to include `usd-core >= 24.0`

✅ **Step 2: Verify TOML syntax**
- Ran: `python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb')); print('OK')"`
- Result: **OK** — TOML file is syntactically valid

✅ **Step 3: Commit**
- Commit SHA: `2af9272`
- Commit message: `build: add usd-core to [usd] optional dependency`
- All pre-commit hooks passed (blacken-docs, codespell, merge conflicts, debug statements, yaml, whitespace, license headers, workflows, ruff)

## Result

- **Status:** DONE
- **Dependencies:** The `usd-core >= 24.0` package is now available when installing with `pip install ansys-tools-visualization-interface[usd]`
- **Branch:** feat/usd-html-converter
- **No concerns:** Pre-commit hooks all passed on first commit attempt, indicating no auto-fixes were needed
