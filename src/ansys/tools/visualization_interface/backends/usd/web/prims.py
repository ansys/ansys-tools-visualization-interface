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

"""Stage traversal shared by the GLB export and the mesh-edge overlay."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from pxr import UsdGeom


def iter_visible_prims(stage: Any) -> Iterator[Any]:
    """Yield the imageable prims a viewer would draw.

    Prims that are invisible, or whose purpose is ``guide`` or ``proxy``, are
    skipped. Visibility and purpose are inherited, so hiding a parent hides
    its children too.

    Parameters
    ----------
    stage : Any
        The USD stage to traverse.

    Yields
    ------
    Any
        Each drawable ``Usd.Prim``.
    """
    hidden_purposes = {UsdGeom.Tokens.guide, UsdGeom.Tokens.proxy}
    for prim in stage.Traverse():
        imageable = UsdGeom.Imageable(prim)
        if not imageable:
            continue
        if imageable.ComputeVisibility() == UsdGeom.Tokens.invisible:
            continue
        if imageable.ComputePurpose() in hidden_purposes:
            continue
        yield prim
