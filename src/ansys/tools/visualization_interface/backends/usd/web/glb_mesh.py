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

"""Mesh geometry conversion helpers for GLB export."""

from __future__ import annotations

import struct
from typing import Any

from pxr import UsdGeom
import pygltflib

from .glb_builder import GLBBuilder
from .glb_materials import get_material_index


def triangulate_faces(indices: list[int], counts: list[int]) -> list[int]:
    """Convert polygon faces to triangles using fan triangulation.

    Parameters
    ----------
    indices : list[int]
        The list of vertex indices for all faces, as defined by USD's faceVertexIndices.
    counts : list[int]
        The list of vertex counts for each face, as defined by USD's faceVertexCounts.

    Returns
    -------
    list[int]
        The list of triangle indices.
    """
    result = []
    idx = 0
    for count in counts:
        face = indices[idx : idx + count]
        for i in range(1, count - 1):
            result.extend([face[0], face[i], face[i + 1]])
        idx += count
    return result


def _add_position_attribute(points: list[Any], builder: GLBBuilder) -> int:
    """Write position data and return the POSITION accessor index.

    Parameters
    ----------
    points : list[Any]
        The list of vertex positions.
    builder : GLBBuilder
        The GLBBuilder instance managing the binary buffer.

    Returns
    -------
    int
        The index of the POSITION accessor.
    """
    pos_data = struct.pack(f"{len(points) * 3}f", *[c for p in points for c in (float(p[0]), float(p[1]), float(p[2]))])
    xs = [float(p[0]) for p in points]
    ys = [float(p[1]) for p in points]
    zs = [float(p[2]) for p in points]
    pos_buffer_view = builder.add_buffer_view(pos_data, pygltflib.ARRAY_BUFFER)
    return builder.add_accessor(
        pos_buffer_view,
        pygltflib.FLOAT,
        len(points),
        pygltflib.VEC3,
        min_values=[min(xs), min(ys), min(zs)],
        max_values=[max(xs), max(ys), max(zs)],
    )


def _add_index_accessor(triangle_indices: list[int], builder: GLBBuilder) -> int:
    """Write triangle index data and return the index accessor.

    Parameters
    ----------
    triangle_indices : list[int]
        The list of triangle indices.
    builder : GLBBuilder
        The GLBBuilder instance managing the binary buffer.

    Returns
    -------
    int
        The index of the triangle index accessor.
    """
    idx_data = struct.pack(f"{len(triangle_indices)}I", *triangle_indices)
    idx_buffer_view = builder.add_buffer_view(idx_data, pygltflib.ELEMENT_ARRAY_BUFFER)
    return builder.add_accessor(idx_buffer_view, pygltflib.UNSIGNED_INT, len(triangle_indices), pygltflib.SCALAR)


def _add_uv_attribute(
    attributes: Any,
    uv_values: list[tuple[float, float]] | None,
    builder: GLBBuilder,
) -> None:
    """Attach TEXCOORD_0 accessor when matching UV data exists.

    Parameters
    ----------
    attributes : Any
        The attributes object to modify.
    uv_values : list[tuple[float, float]] | None
        The list of UV coordinates.
    builder : GLBBuilder
        The GLBBuilder instance managing the binary buffer.
    """
    if not uv_values:
        return

    uv_data = struct.pack(f"{len(uv_values) * 2}f", *[c for uv in uv_values for c in (float(uv[0]), float(uv[1]))])
    uv_buffer_view = builder.add_buffer_view(uv_data, pygltflib.ARRAY_BUFFER)
    attributes.TEXCOORD_0 = builder.add_accessor(uv_buffer_view, pygltflib.FLOAT, len(uv_values), pygltflib.VEC2)


def _get_display_colors(usd_mesh: Any) -> tuple[Any, Any]:
    """Return display colors and interpolation token from USD mesh.

    Parameters
    ----------
     usd_mesh : Any
         The USD mesh prim to query for display color information.

    Returns
    -------
    tuple[Any, Any]
        A tuple containing the display colors and the interpolation token.
    """
    display_color_primvar = usd_mesh.GetDisplayColorPrimvar()
    colors = display_color_primvar.Get() if display_color_primvar else usd_mesh.GetDisplayColorAttr().Get()
    interpolation = display_color_primvar.GetInterpolation() if display_color_primvar else None
    return colors, interpolation


def _add_display_color_attribute(
    points: list[Any],
    source_point_indices: list[int],
    display_colors: Any,
    color_interpolation: Any,
    attributes: Any,
    builder: GLBBuilder,
) -> None:
    """Attach COLOR_0 when displayColor is vertex-compatible.

    Parameters
    ----------
    points : list[Any]
        The list of points in the mesh.
    source_point_indices : list[int]
        The list of source point indices.
    display_colors : Any
        The displayColor values to use for the attribute.
    color_interpolation : Any
        The interpolation method for the display colors.
    attributes : Any
        The attributes object to modify.
    builder : GLBBuilder
        The GLBBuilder instance managing the binary buffer.
    """
    if not (display_colors and color_interpolation in {UsdGeom.Tokens.vertex, UsdGeom.Tokens.varying}):
        return

    if len(display_colors) == len(points):
        expanded_colors = display_colors
    elif source_point_indices and len(display_colors) > 0:
        if any(index < 0 or index >= len(display_colors) for index in source_point_indices):
            return
        expanded_colors = [display_colors[index] for index in source_point_indices]
    else:
        return

    color_data = struct.pack(
        f"{len(expanded_colors) * 3}f",
        *[c for color in expanded_colors for c in (float(color[0]), float(color[1]), float(color[2]))],
    )
    color_buffer_view = builder.add_buffer_view(color_data, pygltflib.ARRAY_BUFFER)
    attributes.COLOR_0 = builder.add_accessor(color_buffer_view, pygltflib.FLOAT, len(expanded_colors), pygltflib.VEC3)


def _append_mesh_to_scene(
    prim: Any,
    attributes: Any,
    idx_acc: int,
    mat_index: int | None,
    gltf: Any,
    scene: Any,
) -> None:
    """Append one mesh primitive and its node to the active scene.

    Parameters
    ----------
    prim : Any
        The USD mesh prim being converted.
    attributes : Any
        The attributes object for the mesh primitive.
    idx_acc : int
        The index accessor for the mesh primitive.
    mat_index : int | None
        The material index for the mesh primitive.
    gltf : Any
        The glTF object to which the mesh primitive will be added.
    scene : Any
        The scene object to which the mesh node will be added.
    """
    primitive = pygltflib.Primitive(attributes=attributes, indices=idx_acc, material=mat_index)
    gltf_mesh = pygltflib.Mesh(primitives=[primitive], name=prim.GetName())
    gltf.meshes.append(gltf_mesh)

    node = pygltflib.Node(mesh=len(gltf.meshes) - 1, name=prim.GetName())
    gltf.nodes.append(node)
    scene.nodes.append(len(gltf.nodes) - 1)


def _build_attributes_for_mesh(
    prim: Any,
    usd_mesh: Any,
    builder: GLBBuilder,
) -> tuple[Any, int, Any, Any]:
    """Build geometric attributes and index accessor for one mesh.

    Parameters
    ----------
    prim : Any
        The USD mesh prim being converted.
    usd_mesh : Any
        The USD mesh object.
    builder : GLBBuilder
        The GLBBuilder instance managing the binary buffer.

    Returns
    -------
    tuple[Any, int, Any, Any]
        A tuple containing the attributes object, index accessor, display colors, and color interpolation.
    """
    triangle_positions, triangle_indices, triangle_uvs, triangle_point_indices = _build_triangle_mesh_data(
        prim, usd_mesh
    )
    pos_acc = _add_position_attribute(triangle_positions, builder)
    idx_acc = _add_index_accessor(triangle_indices, builder)

    attributes = pygltflib.Attributes(POSITION=pos_acc)
    _add_uv_attribute(attributes, triangle_uvs, builder)

    display_colors, color_interpolation = _get_display_colors(usd_mesh)
    _add_display_color_attribute(
        triangle_positions,
        triangle_point_indices,
        display_colors,
        color_interpolation,
        attributes,
        builder,
    )
    return attributes, idx_acc, display_colors, color_interpolation


def _resolve_primvar_element_index(
    interpolation: Any,
    face_index: int,
    corner_index: int,
    point_index: int,
) -> int | None:
    """Resolve primvar element index by interpolation for one face corner.

    Parameters
    ----------
    interpolation : Any
        The interpolation token for the primvar (e.g., vertex, faceVarying).
    face_index : int
        The index of the face being processed.
    corner_index : int
        The index of the corner being processed.
    point_index : int
        The index of the point being processed.

    Returns
    -------
    int | None
        The resolved element index for the primvar, or None if the interpolation type is unsupported.
    """
    if interpolation in {UsdGeom.Tokens.vertex, UsdGeom.Tokens.varying}:
        return point_index
    if interpolation == UsdGeom.Tokens.faceVarying:
        return corner_index
    if interpolation == UsdGeom.Tokens.uniform:
        return face_index
    if interpolation == UsdGeom.Tokens.constant:
        return 0
    return None


def _build_corner_uvs(
    prim: Any,
    face_vertex_indices: list[int],
    face_vertex_counts: list[int],
) -> list[tuple[float, float]] | None:
    """Build one UV coordinate per face corner, honoring indexed primvars.

    Parameters
    ----------
    prim : Any
        The USD mesh prim to query for UV information.
    face_vertex_indices : list[int]
        The indices of the vertices for each face.
    face_vertex_counts : list[int]
        The number of vertices for each face.

    Returns
    -------
    list[tuple[float, float]] | None
        A list of UV coordinates for each corner, or None if no UVs are defined.
    """
    st_primvar = UsdGeom.PrimvarsAPI(prim).GetPrimvar("st")
    if not st_primvar or not st_primvar.IsDefined():
        return None

    st_values = st_primvar.Get()
    if not st_values:
        return None

    st_indices = st_primvar.GetIndices() or []
    interpolation = st_primvar.GetInterpolation() or UsdGeom.Tokens.faceVarying

    corner_uvs: list[tuple[float, float]] = []
    corner_offset = 0
    for face_index, count in enumerate(face_vertex_counts):
        for local_corner in range(count):
            corner_index = corner_offset + local_corner
            point_index = face_vertex_indices[corner_index]
            element_index = _resolve_primvar_element_index(interpolation, face_index, corner_index, point_index)
            if element_index is None:
                corner_uvs.append((0.0, 0.0))
                continue

            if st_indices and element_index < len(st_indices):
                element_index = st_indices[element_index]

            if element_index is None or element_index < 0 or element_index >= len(st_values):
                corner_uvs.append((0.0, 0.0))
                continue

            uv = st_values[element_index]
            # USD uses OpenGL UV convention (V=0 at bottom); glTF uses V=0 at top.
            corner_uvs.append((float(uv[0]), 1.0 - float(uv[1])))

        corner_offset += count

    return corner_uvs


def _build_triangle_mesh_data(
    prim: Any,
    usd_mesh: Any,
) -> tuple[list[Any], list[int], list[tuple[float, float]] | None, list[int]]:
    """Build triangle-ready vertex data, including expanded UVs for face-varying primvars.

    Parameters
    ----------
    prim : Any
        The USD mesh prim being converted.
    usd_mesh : Any
        The USD mesh object.

    Returns
    -------
    tuple[list[Any], list[int], list[tuple[float, float]] | None, list[int]]
        A tuple containing the triangle positions, triangle indices, triangle UVs, and triangle point indices.
    """
    points = usd_mesh.GetPointsAttr().Get() or []
    face_vertex_indices = list(usd_mesh.GetFaceVertexIndicesAttr().Get() or [])
    face_vertex_counts = list(usd_mesh.GetFaceVertexCountsAttr().Get() or [])

    if not points or not face_vertex_indices or not face_vertex_counts:
        return points, list(range(len(points))), None, list(range(len(points)))

    corner_uvs = _build_corner_uvs(prim, face_vertex_indices, face_vertex_counts)

    triangle_positions: list[Any] = []
    triangle_indices: list[int] = []
    triangle_uvs: list[tuple[float, float]] | None = [] if corner_uvs is not None else None
    triangle_point_indices: list[int] = []

    corner_offset = 0
    for count in face_vertex_counts:
        if count < 3:
            corner_offset += count
            continue

        for tri_step in range(1, count - 1):
            tri_corners = (0, tri_step, tri_step + 1)
            for local_corner in tri_corners:
                corner_index = corner_offset + local_corner
                point_index = face_vertex_indices[corner_index]
                if point_index < 0 or point_index >= len(points):
                    continue

                point = points[point_index]
                triangle_positions.append(point)
                triangle_indices.append(len(triangle_positions) - 1)
                triangle_point_indices.append(point_index)

                if triangle_uvs is not None and corner_uvs is not None:
                    triangle_uvs.append(corner_uvs[corner_index])

        corner_offset += count

    return triangle_positions, triangle_indices, triangle_uvs, triangle_point_indices


def iter_usd_mesh_prims(stage: Any) -> list[Any]:
    """Collect mesh prims from a USD stage.

    Parameters
    ----------
    stage : Any
        The USD stage to traverse for mesh prims.

    Returns
    -------
    list[Any]
        A list of USD mesh prims found in the stage.
    """
    mesh_prims = []
    for prim in stage.Traverse():
        if prim.IsA(UsdGeom.Mesh):
            mesh_prims.append(prim)
    return mesh_prims


def convert_mesh_prim_to_gltf(
    prim: Any,
    gltf: Any,
    scene: Any,
    builder: GLBBuilder,
    texture_cache: dict[tuple[str, str, str], int],
    image_cache: dict[str, int],
    sampler_cache: dict[tuple[int, int], int],
) -> None:
    """Convert one USD mesh prim into GLTF mesh/node entries.

    Parameters
    ----------
    prim : Any
        The USD mesh prim to convert.
    gltf : Any
        The GLTF object to which the mesh will be added.
    scene : Any
        The GLTF scene to which the mesh node will be added.
    builder : GLBBuilder
        The GLBBuilder instance used for constructing the GLTF.
    texture_cache : dict[tuple[str, str, str], int]
        A cache mapping texture identifiers to GLTF texture indices.
    image_cache : dict[str, int]
        A cache mapping image file paths to GLTF image indices.
    sampler_cache : dict[tuple[int, int], int]
        A cache mapping sampler settings to GLTF sampler indices.
    """
    usd_mesh = UsdGeom.Mesh(prim)
    points = usd_mesh.GetPointsAttr().Get()
    if not points:
        return

    attributes, idx_acc, display_colors, color_interpolation = _build_attributes_for_mesh(
        prim,
        usd_mesh,
        builder,
    )
    mat_index = get_material_index(
        prim,
        display_colors,
        color_interpolation,
        gltf,
        builder,
        texture_cache,
        image_cache,
        sampler_cache,
    )
    _append_mesh_to_scene(prim, attributes, idx_acc, mat_index, gltf, scene)
