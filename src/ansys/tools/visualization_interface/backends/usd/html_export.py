# Copyright (C) 2024 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
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

"""USD-to-HTML export utility for ansys-tools-visualization-interface."""

from __future__ import annotations

from pathlib import Path
import tempfile

_USDVIEWER_IMPORT_ERROR = (
    "The 'ansys-tools-usdviewer' package is required for HTML export. "
    "Install it with: pip install 'ansys-tools-visualization-interface[usd]'"
)

_USD_CORE_IMPORT_ERROR = (
    "The 'usd-core' package is required for mesh-line injection. "
    "Install it with: pip install 'ansys-tools-visualization-interface[usd]'"
)

_CONFIG_ANCHOR = "const binary = atob(glbBase64);"
_SCENE_ANCHOR = "scene.add(gltf.scene);"
_INJECTION_MARKER = "// ansysEdgesInjected"


def _is_usd_stage(obj: object) -> bool:
    """Return True if *obj* duck-types as a ``pxr.Usd.Stage``."""
    return (
        hasattr(obj, "Traverse")
        and hasattr(obj, "GetPrimAtPath")
        and hasattr(obj, "Export")
    )


def _stage_to_temp_usd(stage: object) -> Path:
    """Export *stage* to a temporary ``.usda`` file and return its path."""
    tmp = tempfile.NamedTemporaryFile(suffix=".usda", delete=False)
    tmp.close()
    tmp_path = Path(tmp.name)
    stage.Export(str(tmp_path))  # type: ignore[union-attr]
    return tmp_path


def _open_stage(usd_path: Path) -> object:
    """Open *usd_path* as a ``pxr.Usd.Stage`` (lazy import)."""
    try:
        from pxr import Usd
    except ImportError as exc:
        raise ImportError(_USD_CORE_IMPORT_ERROR) from exc
    return Usd.Stage.Open(str(usd_path))


def _inject_mesh_lines(
    html_path: Path,
    stage: object,
    line_color: str,
    line_opacity: float,
) -> None:
    """Inject Three.js LineSegments derived from UsdGeomMesh prims into *html_path*.

    Parameters
    ----------
    html_path : Path
        Path to the viewer HTML file to patch in place.
    stage : pxr.Usd.Stage
        USD stage whose UsdGeomMesh prims are traversed for edge extraction.
    line_color : str
        CSS hex colour string (e.g. ``"#ffffff"``).
    line_opacity : float
        Opacity in ``[0.0, 1.0]``.
    """
    import json

    try:
        from pxr import UsdGeom
    except ImportError as exc:
        raise ImportError(_USD_CORE_IMPORT_ERROR) from exc

    html_text = html_path.read_text(encoding="utf-8")

    if _INJECTION_MARKER in html_text:
        return  # idempotent

    if _CONFIG_ANCHOR not in html_text or _SCENE_ANCHOR not in html_text:
        # Template incompatible — skip gracefully rather than corrupt the file.
        return

    segments: list[float] = []
    for prim in stage.Traverse():  # type: ignore[union-attr]
        mesh = UsdGeom.Mesh(prim)
        if not mesh:
            continue

        pts = mesh.GetPointsAttr().Get()
        counts = mesh.GetFaceVertexCountsAttr().Get()
        indices = mesh.GetFaceVertexIndicesAttr().Get()

        if not pts or not counts or not indices:
            continue

        seen: set[tuple[int, int]] = set()
        cursor = 0
        for n in counts:
            face_verts = indices[cursor : cursor + n]
            for i in range(n):
                a = int(face_verts[i])
                b = int(face_verts[(i + 1) % n])
                key = (min(a, b), max(a, b))
                if key not in seen:
                    seen.add(key)
                    pa = pts[a]
                    pb = pts[b]
                    segments.extend([float(pa[0]), float(pa[1]), float(pa[2])])
                    segments.extend([float(pb[0]), float(pb[1]), float(pb[2])])
            cursor += n

    segs_json = json.dumps([round(v, 6) for v in segments], separators=(",", ":"))

    config_block = (
        f"      const ansysEdgeSegs = new Float32Array({segs_json});\n"
        f'      const ansysEdgeLineColor = new THREE.Color("{line_color}");\n'
        f"      const ansysEdgeLineOpacity = {line_opacity};\n"
        f"      {_INJECTION_MARKER}\n\n"
        "      "
    )
    html_text = html_text.replace(_CONFIG_ANCHOR, config_block + _CONFIG_ANCHOR, 1)

    edge_js = (
        f"{_SCENE_ANCHOR}\n"
        "        if (ansysEdgeSegs.length >= 6) {\n"
        "          const geo = new THREE.BufferGeometry();\n"
        '          geo.setAttribute("position", new THREE.BufferAttribute(ansysEdgeSegs, 3));\n'
        "          const mat = new THREE.LineBasicMaterial({\n"
        "            color: ansysEdgeLineColor,\n"
        "            transparent: ansysEdgeLineOpacity < 1.0,\n"
        "            opacity: ansysEdgeLineOpacity,\n"
        "          });\n"
        "          const lines = new THREE.LineSegments(geo, mat);\n"
        '          lines.name = "AnsysEdges";\n'
        "          lines.frustumCulled = false;\n"
        "          lines.renderOrder = 1;\n"
        "          scene.add(lines);\n"
        "        }"
    )
    html_text = html_text.replace(_SCENE_ANCHOR, edge_js, 1)
    html_path.write_text(html_text, encoding="utf-8")


def export_usd_to_html(
    source: "str | Path",
    output_path: "str | Path | None" = None,
    *,
    show_mesh_lines: bool = True,
    line_color: str = "#ffffff",
    line_opacity: float = 0.9,
) -> Path:
    """Convert a USD asset to a self-contained Three.js HTML viewer.

    Parameters
    ----------
    source : str | Path | pxr.Usd.Stage
        USD file path (.usd / .usda / .usdc / .usdz) or an in-memory USD stage.
    output_path : str | Path | None, default: None
        Destination for the HTML file. When None, placed alongside the source
        as ``{stem}_viewer.html``.
    show_mesh_lines : bool, default: True
        When True, injects Three.js LineSegments derived from polygon edges of
        all UsdGeomMesh prims in the stage for a wireframe overlay.
    line_color : str, default: "#ffffff"
        CSS hex color for the mesh-edge overlay.
    line_opacity : float, default: 0.9
        Opacity of the mesh-edge overlay (0.0 - 1.0).

    Returns
    -------
    pathlib.Path
        Absolute path to the written HTML file.

    Raises
    ------
    ImportError
        If ``ansys-tools-usdviewer`` or ``usd-core`` is not installed.
    FileNotFoundError
        If a file path is given but does not exist on disk.
    ValueError
        If ``line_opacity`` is outside [0.0, 1.0].
    """
    try:
        from ansys.tools.usdviewer.web.html_export import (
            export_viewer_html as _export_viewer_html,
        )
    except ImportError as exc:
        raise ImportError(_USDVIEWER_IMPORT_ERROR) from exc

    if not (0.0 <= line_opacity <= 1.0):
        raise ValueError(
            f"line_opacity must be between 0.0 and 1.0, got {line_opacity!r}."
        )

    tmp_path: Path | None = None
    stage: object | None = None

    try:
        if _is_usd_stage(source):
            stage = source
            tmp_path = _stage_to_temp_usd(stage)
            usd_path = tmp_path
        else:
            usd_path = Path(source).expanduser().resolve()  # type: ignore[arg-type]
            if not usd_path.exists():
                raise FileNotFoundError(f"USD file not found: {usd_path}")

        html_path = _export_viewer_html(usd_path, output_path)

        if show_mesh_lines:
            if stage is None:
                stage = _open_stage(usd_path)
            _inject_mesh_lines(html_path, stage, line_color, line_opacity)

        return html_path

    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)
