# Task 4 Brief: Expose `export_usd_to_html` at top level + update docs

## Task from Plan

**Files:**
- Modify: `src/ansys/tools/visualization_interface/backends/usd/__init__.py`
- Modify: `src/ansys/tools/visualization_interface/__init__.py`
- Modify: `doc/source/user_guide/usdviewer.rst`
- Modify: `tests/test_usd_html_export.py` — append top-level import test

**Interfaces consumed** (from Task 2):
- `export_usd_to_html` from `ansys.tools.visualization_interface.backends.usd.html_export`

---

## TDD Workflow (REQUIRED)

1. **RED** — Append the top-level import test to `tests/test_usd_html_export.py`. Run it:
   ```
   pytest tests/test_usd_html_export.py::test_export_usd_to_html_importable_from_top_level -v
   ```
   It MUST fail with `ImportError` (the name isn't exported yet). Record the output.

2. **GREEN** — Update the `__init__.py` files. Run the test again — it MUST pass. Record output.

3. Commit.

Your report MUST include TDD evidence.

---

## Changes Required

### 1. Append failing test to `tests/test_usd_html_export.py`

Add this at the very bottom of the file (after all existing classes):

```python
def test_export_usd_to_html_importable_from_top_level():
    """export_usd_to_html is accessible directly from the package root."""
    from ansys.tools.visualization_interface import export_usd_to_html as _fn

    assert callable(_fn)
```

### 2. Update `src/ansys/tools/visualization_interface/backends/usd/__init__.py`

Replace entire file content with:

```python
# Copyright (C) 2024 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""USD backend initialization."""

from ansys.tools.visualization_interface.backends.usd.html_export import (  # noqa: F401
    export_usd_to_html,
)
```

### 3. Add import to `src/ansys/tools/visualization_interface/__init__.py`

Append this line after the existing `Color` import (keep the license header and all existing content unchanged):

```python
from ansys.tools.visualization_interface.backends.usd.html_export import (  # noqa: F401, E402
    export_usd_to_html,
)
```

The full imports block should look like:

```python
from ansys.tools.visualization_interface.plotter import Plotter  # noqa: F401, E402
from ansys.tools.visualization_interface.types.edge_plot import (
    EdgePlot,
)  # noqa: F401, E402
from ansys.tools.visualization_interface.types.mesh_object_plot import (  # noqa: F401, E402
    MeshObjectPlot,
)
from ansys.tools.visualization_interface.utils.clip_plane import (
    ClipPlane,
)  # noqa: F401, E402
from ansys.tools.visualization_interface.utils.color import Color  # noqa: F401, E402
from ansys.tools.visualization_interface.backends.usd.html_export import (  # noqa: F401, E402
    export_usd_to_html,
)
```

### 4. Update `doc/source/user_guide/usdviewer.rst`

Append this section to the END of the existing file:

```rst
USD to HTML export
------------------

To convert a USD file to a self-contained HTML viewer page (backed by Three.js),
use :func:`~ansys.tools.visualization_interface.export_usd_to_html`. The
generated file embeds all geometry as a base64-encoded GLB and requires only a
CDN connection to render.

.. code-block:: python

    from ansys.tools.visualization_interface import export_usd_to_html

    # From a file path
    html_path = export_usd_to_html("my_model.usd", "my_model_viewer.html")

    # From an in-memory pxr.Usd.Stage (no .usd file needed)
    from pxr import Gf, Usd, UsdGeom

    stage = Usd.Stage.CreateInMemory()
    mesh = UsdGeom.Mesh.Define(stage, "/Box")
    stage.SetDefaultPrim(mesh.GetPrim())
    mesh.GetPointsAttr().Set([Gf.Vec3f(0, 0, 0), Gf.Vec3f(1, 0, 0), Gf.Vec3f(0, 1, 0)])
    mesh.GetFaceVertexCountsAttr().Set([3])
    mesh.GetFaceVertexIndicesAttr().Set([0, 1, 2])

    html_path = export_usd_to_html(stage, "triangle_viewer.html")

The optional ``show_mesh_lines``, ``line_color``, and ``line_opacity`` parameters
control a wireframe edge overlay injected directly into the HTML:

.. code-block:: python

    html_path = export_usd_to_html(
        "my_model.usd",
        show_mesh_lines=True,
        line_color="#00ffcc",
        line_opacity=0.7,
    )

.. note::

    This feature requires the ``[usd]`` optional dependencies:
    ``pip install ansys-tools-visualization-interface[usd]``
```

---

## Commit

```bash
git add src/ansys/tools/visualization_interface/backends/usd/__init__.py \
        src/ansys/tools/visualization_interface/__init__.py \
        doc/source/user_guide/usdviewer.rst \
        tests/test_usd_html_export.py
git commit -m "feat(usd): expose export_usd_to_html at top level and update docs"
```

## Final test run

After committing, run the full test suite:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_usd_html_export.py -v
```

Expected: all 22 tests PASS (21 existing + 1 new top-level import test).

## Global Constraints

- Python >= 3.10, < 4
- License header on all modified `.py` files (pre-commit manages it)
- `pxr` and `ansys.tools.usdviewer` imports MUST remain lazy in `html_export.py` (do not add top-level imports there)
- The `__init__.py` import of `export_usd_to_html` is a regular (non-lazy) import — this is intentional and correct
- Ruff is the linter/formatter
