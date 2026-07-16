# Task 1 Brief: Update `pyproject.toml` — add `usd-core` dependency

## Task from Plan

### Task 1: Update `pyproject.toml` — add `usd-core` dependency

**Files:**
- Modify: `pyproject.toml`

**Interfaces:**
- Produces: `usd-core >= 24.0` available when `pip install ansys-tools-visualization-interface[usd]`

- [ ] **Step 1: Edit `pyproject.toml`**

  Change the `[usd]` entry from:
  ```toml
  usd = [
      "ansys-tools-usdviewer >= 0.1.0,< 1"
  ]
  ```
  to:
  ```toml
  usd = [
      "ansys-tools-usdviewer >= 0.1.0,< 1",
      "usd-core >= 24.0",
  ]
  ```

- [ ] **Step 2: Verify TOML syntax**

  ```powershell
  python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb')); print('OK')"
  ```
  Expected: `OK`

- [ ] **Step 3: Commit**

  ```bash
  git add pyproject.toml
  git commit -m "build: add usd-core to [usd] optional dependency"
  ```

## Global Constraints (for context)

- Python >= 3.10, < 4
- All new `.py` files under `src/` and `tests/` need the ANSYS MIT license header (pre-commit adds it automatically)
- `pxr` and `ansys.tools.usdviewer` imports must be lazy (inside function bodies only)
- `usd-core >= 24.0` added to the `[usd]` optional extra in `pyproject.toml`
- Ruff is the linter/formatter
