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

"""HTML template rendering helpers for web viewer export."""

from __future__ import annotations

import json
from pathlib import Path

_GLB_TEMPLATE_FILE = "glb_template.html"

_REQUIRED_PLACEHOLDERS: list[str] = ["__GLB_B64_JSON__", "__MODEL_NAME_JSON__"]


def validate_template(template: str, required: list[str]) -> None:
    """Raise ``ValueError`` if any string in *required* is absent from *template*.

    Parameters
    ----------
    template : str
        Template source text to validate.
    required : list[str]
        Strings that must all appear verbatim in *template*.

    Raises
    ------
    ValueError
        If one or more required strings are absent.
    """
    missing = [v for v in required if v not in template]
    if missing:
        raise ValueError(f"Template is missing required placeholders: {missing!r}")


def build_viewer_html_glb(
    glb_b64: str, model_name: str, template_path: Path | None = None
) -> str:
    """Build a self-contained HTML viewer that renders a base64-encoded GLB.

    The template is validated with :func:`validate_template` before substitution.
    Both ``__GLB_B64_JSON__`` and ``__MODEL_NAME_JSON__`` must appear verbatim
    in the template source; they are replaced with ``json.dumps``-encoded values
    so that special characters are escaped automatically.

    Parameters
    ----------
    glb_b64 : str
        Base64-encoded GLB binary.
    model_name : str
        Display name shown in the viewer (replaces ``__MODEL_NAME_JSON__``).
    template_path : Path | None, default: None
        Path to a custom HTML template. When ``None``, the built-in
        ``glb_template.html`` is used. See the *Custom HTML templates* section
        of the user guide for the required placeholder contract.

    Raises
    ------
    FileNotFoundError
        If *template_path* is given but the file does not exist.
    ValueError
        If the template is missing one or both required placeholders.
    """
    if template_path is not None:
        path = Path(template_path)
        if not path.exists():
            raise FileNotFoundError(f"Template file not found: {path}")
        template = path.read_text(encoding="utf-8")
    else:
        template = _load_template(_GLB_TEMPLATE_FILE)

    validate_template(template, _REQUIRED_PLACEHOLDERS)

    return template.replace("__MODEL_NAME_JSON__", json.dumps(model_name)).replace(
        "__GLB_B64_JSON__", json.dumps(glb_b64)
    )


def _load_template(template_name: str) -> str:
    """Load a viewer HTML template from the package directory."""
    template_path = Path(__file__).with_name(template_name)
    if not template_path.exists():
        raise RuntimeError(f"Viewer template not found: {template_path}")
    return template_path.read_text(encoding="utf-8")
