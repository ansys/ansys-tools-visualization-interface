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

"""Low-level helpers to build GLB buffers and base glTF scene state."""

from __future__ import annotations

from typing import Any

import pygltflib


class GLBBuilder:
    """Utility for writing GLTF buffers and accessors.

    This class manages the binary buffer and associated glTF structures when
    converting USD assets to GLB format. It provides methods to append data
    to the shared buffer and create corresponding buffer views and accessors.

    Parameters
    ----------
    gltf : Any
        An initialized glTF document (e.g. pygltflib.GLTF2) to populate.
    """

    def __init__(self, gltf: Any):
        """Initialize the GLBBuilder with a GLTF document."""
        self.gltf = gltf
        self.binary_blob = bytearray()

    def _pad4(self) -> None:
        """Pad the binary buffer to the next 4-byte boundary."""
        while len(self.binary_blob) % 4:
            self.binary_blob.append(0)

    def add_buffer_view(self, data: bytes, target: int | None) -> int:
        """Append binary data to the shared buffer and return its buffer-view index.

        Parameters
        ----------
        data : bytes
            The binary data to append to the buffer.
        target : int | None
            The target type for the buffer view (e.g., pygltflib.ARRAY_BUFFER or pygltflib.ELEMENT_ARRAY_BUFFER).
        """
        self._pad4()
        offset = len(self.binary_blob)
        self.binary_blob.extend(data)
        buffer_view = pygltflib.BufferView(buffer=0, byteOffset=offset, byteLength=len(data))
        if target is not None:
            buffer_view.target = target
        self.gltf.bufferViews.append(buffer_view)
        return len(self.gltf.bufferViews) - 1

    def add_accessor(
        self,
        buffer_view_idx: int,
        component_type: int,
        count: int,
        accessor_type: str,
        min_values: list[float] | None = None,
        max_values: list[float] | None = None,
    ) -> int:
        """Create an accessor for an existing buffer view and return its index.

        Parameters
        ----------
        buffer_view_idx : int
            The index of the buffer view this accessor references.
        component_type : int
            The GLTF component type (e.g., pygltflib.FLOAT, pygltflib.UNSIGNED_SHORT).
        count : int
            The number of elements in the accessor.
        accessor_type : str
            The GLTF accessor type (e.g., "SCALAR", "VEC3", "MAT4").
        min_values : list[float] | None, optional
            Minimum values for the accessor (used for bounding boxes), by default None.
        max_values : list[float] | None, optional
            Maximum values for the accessor (used for bounding boxes), by default None.
        """
        accessor = pygltflib.Accessor(
            bufferView=buffer_view_idx,
            byteOffset=0,
            componentType=component_type,
            count=count,
            type=accessor_type,
        )
        if min_values is not None:
            accessor.min = min_values
        if max_values is not None:
            accessor.max = max_values
        self.gltf.accessors.append(accessor)
        return len(self.gltf.accessors) - 1

    def finalize(self) -> bytes:
        """Finalize the GLTF document and return the serialized GLB bytes.

        Returns
        -------
        bytes
            The complete GLB file as a byte string.
        """
        self.gltf.buffers.append(pygltflib.Buffer(byteLength=len(self.binary_blob)))
        self.gltf.set_binary_blob(bytes(self.binary_blob))
        data = self.gltf.save_to_bytes()
        return data if isinstance(data, bytes) else b"".join(data)


def create_gltf_scene() -> tuple[Any, Any]:
    """Create an initialized glTF document and default scene.

    Returns
    -------
    tuple[Any, Any]
        A tuple containing the glTF document and the default scene object.
    """
    gltf = pygltflib.GLTF2()
    gltf.asset = pygltflib.Asset(version="2.0")
    scene = pygltflib.Scene(nodes=[])
    gltf.scenes.append(scene)
    gltf.scene = 0
    return gltf, scene
