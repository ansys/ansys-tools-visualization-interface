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


def build_viewer_html_glb(glb_b64: str, model_name: str) -> str:
    """Build a self-contained HTML viewer that renders a base64-encoded GLB."""
    template = _load_template(_GLB_TEMPLATE_FILE)
    return template.replace("__MODEL_NAME_JSON__", json.dumps(model_name)).replace(
        "__GLB_B64_JSON__", json.dumps(glb_b64)
    )


def _load_template(template_name: str) -> str:
    """Load a viewer HTML template from the package directory."""
    template_path = Path(__file__).with_name(template_name)
    if not template_path.exists():
        raise RuntimeError(f"Viewer template not found: {template_path}")
    return template_path.read_text(encoding="utf-8")
