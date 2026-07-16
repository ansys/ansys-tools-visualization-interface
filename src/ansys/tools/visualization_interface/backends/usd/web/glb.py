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

"""GLB conversion entrypoint for USD web viewer export."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pxr import Usd

from .glb_builder import GLBBuilder, create_gltf_scene
from .glb_lights import append_usd_lights_to_scene
from .glb_mesh import convert_mesh_prim_to_gltf, iter_usd_mesh_prims


def _open_stage_for_glb(path: Path) -> Any:
    """Open a USD stage for GLB conversion.

    Parameters
    ----------
    path : Path
        Path to the USD file to open.

    Returns
    -------
    Any
        The opened USD stage.
    """
    stage = Usd.Stage.Open(str(path))
    if not stage:
        raise RuntimeError(f"Failed to open USD stage: {path}")
    return stage


def convert_usd_to_glb(path: Path) -> bytes:
    """Convert a USD stage to a self-contained GLB binary.

    Parameters
    ----------
    path : Path
        Path to the USD file to convert.

    Returns
    -------
    bytes
        The GLB binary data.
    """
    stage = _open_stage_for_glb(path)
    gltf, scene = create_gltf_scene()
    builder = GLBBuilder(gltf)
    texture_cache: dict[tuple[str, str, str], int] = {}
    image_cache: dict[str, int] = {}
    sampler_cache: dict[tuple[int, int], int] = {}

    append_usd_lights_to_scene(stage, gltf, scene)

    for prim in iter_usd_mesh_prims(stage):
        convert_mesh_prim_to_gltf(
            prim,
            gltf,
            scene,
            builder,
            texture_cache,
            image_cache,
            sampler_cache,
        )

    return builder.finalize()
