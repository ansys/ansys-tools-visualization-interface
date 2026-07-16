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

"""Material and texture conversion helpers for GLB export."""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any

from pxr import UsdGeom, UsdShade
import pygltflib

from .glb_builder import GLBBuilder


def _append_material_and_get_index(gltf: Any, material: Any) -> int:
    """Append a GLTF material and return its index.

    Parameters
    ----------
    gltf : Any
        The glTF document to modify.
    material : Any
        The material to append to the glTF document.

    Returns
    -------
    int
        The index of the newly appended material in the glTF document.
    """
    gltf.materials.append(material)
    return len(gltf.materials) - 1


def _build_material_from_shader(shader: Any, prim_name: str) -> Any:
    """Build a GLTF material from a UsdPreviewSurface shader.

    Parameters
    ----------
    shader : Any
        The UsdPreviewSurface shader to convert.
    prim_name : str
        The name of the primitive associated with the shader.

    Returns
    -------
    Any
        The resulting GLTF material.
    """
    # Match UsdPreviewSurface defaults to avoid glTF defaults (metallic=1)
    # when USD scalar inputs are texture-connected and return None.
    pbr = pygltflib.PbrMetallicRoughness(
        baseColorFactor=[1.0, 1.0, 1.0, 1.0],
        metallicFactor=0.0,
        roughnessFactor=0.5,
    )

    diffuse = shader.GetInput("diffuseColor")
    if diffuse and diffuse.Get() is not None:
        dc = diffuse.Get()
        pbr.baseColorFactor = [float(dc[0]), float(dc[1]), float(dc[2]), 1.0]

    metallic = shader.GetInput("metallic")
    if metallic and metallic.Get() is not None:
        pbr.metallicFactor = float(metallic.Get())

    roughness = shader.GetInput("roughness")
    if roughness and roughness.Get() is not None:
        pbr.roughnessFactor = float(roughness.Get())

    mat = pygltflib.Material(pbrMetallicRoughness=pbr, name=prim_name, doubleSided=True)

    emissive = shader.GetInput("emissiveColor")
    if emissive and emissive.Get() is not None:
        ec = emissive.Get()
        mat.emissiveFactor = [float(ec[0]), float(ec[1]), float(ec[2])]

    return mat


def _get_connected_shader_input(shader: Any, input_name: str) -> tuple[Any, str] | None:
    """Return connected shader and output name for a shader input.

    Parameters
    ----------
    shader : Any
        The shader containing the input to check.
    input_name : str
        The name of the shader input to check for a connection.

    Returns
    -------
    tuple[Any, str] | None
        A tuple containing the connected shader and output name, or None if no connection exists.
    """
    shader_input = shader.GetInput(input_name)
    if not shader_input:
        return None

    connected = shader_input.GetConnectedSource()
    if not connected:
        return None

    source_api, output_name, _ = connected
    source_prim = source_api.GetPrim()
    if not source_prim or not source_prim.IsValid():
        return None

    source_shader = UsdShade.Shader(source_prim)
    if not source_shader or not source_shader.GetPrim().IsValid():
        return None

    return source_shader, output_name


def _map_wrap_mode(wrap_mode: Any) -> int:
    """Map USD wrap token to glTF sampler wrap mode.

    Parameters
    ----------
    wrap_mode : Any
        The USD token representing the wrap mode (e.g., "repeat", "mirror", "clamp").

    Returns
    -------
    int
        The corresponding glTF wrap mode constant (e.g., pygltflib.REPEAT).
    """
    if wrap_mode == "repeat":
        return pygltflib.REPEAT
    if wrap_mode == "mirror":
        return pygltflib.MIRRORED_REPEAT
    return pygltflib.CLAMP_TO_EDGE


def _resolve_asset_file_path(asset_input: Any, shader_prim: Any) -> Path | None:
    """Resolve a USD asset path from an input to a file path.

    Parameters
    ----------
    asset_input : Any
        The USD asset input to resolve.
    shader_prim : Any
        The shader primitive associated with the asset input.

    Returns
    -------
    Path | None
        The resolved file path, or None if it cannot be resolved.
    """
    if not asset_input:
        return None

    asset_value = asset_input.Get()
    if asset_value is None:
        return None

    resolved = getattr(asset_value, "resolvedPath", None)
    if resolved:
        resolved_path = Path(str(resolved))
        if resolved_path.exists():
            return resolved_path

    authored = getattr(asset_value, "path", None)
    if not authored:
        return None

    authored_path = Path(str(authored))
    if authored_path.is_absolute() and authored_path.exists():
        return authored_path

    layer = shader_prim.GetStage().GetRootLayer()
    if not layer:
        return None
    layer_path = Path(layer.realPath)
    candidate = (layer_path.parent / authored_path).resolve()
    return candidate if candidate.exists() else None


def _get_texture_index_from_usd_uv_texture(
    source_shader: Any,
    gltf: Any,
    builder: GLBBuilder,
    texture_cache: dict[tuple[str, str, str], int],
    image_cache: dict[str, int],
    sampler_cache: dict[tuple[int, int], int],
) -> int | None:
    """Create or reuse a glTF texture index from a UsdUVTexture shader.

    Parameters
    ----------
    source_shader : Any
        The UsdUVTexture shader to convert.
    gltf : Any
        The glTF document to modify.
    builder : GLBBuilder
        The GLBBuilder instance managing the binary buffer.
    texture_cache : dict[tuple[str, str, str], int]
        Cache mapping (file_path, wrap_s, wrap_t) to glTF texture indices.
    image_cache : dict[str, int]
        Cache mapping file paths to glTF image indices.
    sampler_cache : dict[tuple[int, int], int]
        Cache mapping (wrap_s, wrap_t) to glTF sampler indices.

    Returns
    -------
    int | None
        The index of the corresponding glTF texture, or None if the shader is not a
        UsdUVTexture or lacks a valid file input.
    """
    shader_id = source_shader.GetIdAttr().Get()
    if shader_id != "UsdUVTexture":
        return None

    file_path = _resolve_asset_file_path(source_shader.GetInput("file"), source_shader.GetPrim())
    if file_path is None:
        return None

    wrap_s = _map_wrap_mode(source_shader.GetInput("wrapS").Get() if source_shader.GetInput("wrapS") else None)
    wrap_t = _map_wrap_mode(source_shader.GetInput("wrapT").Get() if source_shader.GetInput("wrapT") else None)

    texture_key = (str(file_path), str(wrap_s), str(wrap_t))
    cached_texture = texture_cache.get(texture_key)
    if cached_texture is not None:
        return cached_texture

    image_key = str(file_path)
    image_index = image_cache.get(image_key)
    if image_index is None:
        image_bytes = file_path.read_bytes()
        image_buffer_view = builder.add_buffer_view(image_bytes, None)
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type is None:
            mime_type = "image/png"
        gltf.images.append(pygltflib.Image(bufferView=image_buffer_view, mimeType=mime_type, name=file_path.name))
        image_index = len(gltf.images) - 1
        image_cache[image_key] = image_index

    sampler_key = (wrap_s, wrap_t)
    sampler_index = sampler_cache.get(sampler_key)
    if sampler_index is None:
        gltf.samplers.append(pygltflib.Sampler(wrapS=wrap_s, wrapT=wrap_t))
        sampler_index = len(gltf.samplers) - 1
        sampler_cache[sampler_key] = sampler_index

    gltf.textures.append(pygltflib.Texture(source=image_index, sampler=sampler_index))
    texture_index = len(gltf.textures) - 1
    texture_cache[texture_key] = texture_index
    return texture_index


def _apply_preview_surface_textures(
    shader: Any,
    material: Any,
    gltf: Any,
    builder: GLBBuilder,
    texture_cache: dict[tuple[str, str, str], int],
    image_cache: dict[str, int],
    sampler_cache: dict[tuple[int, int], int],
) -> None:
    """Apply supported UsdPreviewSurface texture connections to a GLTF material.

    Parameters
    ----------
    shader : Any
        The UsdPreviewSurface shader to check for texture connections.
    material : Any
        The GLTF material to modify with texture references.
    gltf : Any
        The glTF document to modify with new textures, images, and samplers as needed.
    builder : GLBBuilder
        The GLBBuilder instance managing the binary buffer.
    texture_cache : dict[tuple[str, str, str], int]
        Cache mapping (file_path, wrap_s, wrap_t) to glTF texture indices.
    image_cache : dict[str, int]
        Cache mapping file paths to glTF image indices.
    sampler_cache : dict[tuple[int, int], int]
        Cache mapping (wrap_s, wrap_t) to glTF sampler indices.
    """
    pbr = material.pbrMetallicRoughness

    diffuse_connection = _get_connected_shader_input(shader, "diffuseColor")
    if diffuse_connection is not None:
        diffuse_shader, _ = diffuse_connection
        tex_index = _get_texture_index_from_usd_uv_texture(
            diffuse_shader,
            gltf,
            builder,
            texture_cache,
            image_cache,
            sampler_cache,
        )
        if tex_index is not None:
            pbr.baseColorTexture = pygltflib.TextureInfo(index=tex_index)

    normal_connection = _get_connected_shader_input(shader, "normal")
    if normal_connection is not None:
        normal_shader, _ = normal_connection
        tex_index = _get_texture_index_from_usd_uv_texture(
            normal_shader,
            gltf,
            builder,
            texture_cache,
            image_cache,
            sampler_cache,
        )
        if tex_index is not None:
            material.normalTexture = pygltflib.NormalMaterialTexture(index=tex_index)

    emissive_connection = _get_connected_shader_input(shader, "emissiveColor")
    if emissive_connection is not None:
        emissive_shader, _ = emissive_connection
        tex_index = _get_texture_index_from_usd_uv_texture(
            emissive_shader,
            gltf,
            builder,
            texture_cache,
            image_cache,
            sampler_cache,
        )
        if tex_index is not None:
            material.emissiveTexture = pygltflib.TextureInfo(index=tex_index)

    opacity_input = shader.GetInput("opacity")
    opacity_threshold_input = shader.GetInput("opacityThreshold")
    opacity_threshold = float(opacity_threshold_input.Get()) if opacity_threshold_input else 0.0
    has_connected_opacity = _get_connected_shader_input(shader, "opacity") is not None
    opacity_value = float(opacity_input.Get()) if opacity_input and opacity_input.Get() is not None else 1.0

    if has_connected_opacity or opacity_value < 1.0:
        material.alphaMode = "MASK" if opacity_threshold > 0.0 else "BLEND"
        if opacity_threshold > 0.0:
            material.alphaCutoff = opacity_threshold


def _build_display_color_material(display_colors: Any, prim_name: str) -> Any:
    """Build a fallback GLTF material from the first displayColor value.

    Parameters
    ----------
    display_colors : Any
        The displayColor values to use for the material.
    prim_name : str
        The name of the prim to use for the material name.

    Returns
    -------
    Any
        The constructed GLTF material.
    """
    c = display_colors[0]
    pbr = pygltflib.PbrMetallicRoughness(baseColorFactor=[float(c[0]), float(c[1]), float(c[2]), 1.0])
    return pygltflib.Material(pbrMetallicRoughness=pbr, name=f"{prim_name}_displayColor", doubleSided=True)


def get_material_index(
    prim: Any,
    display_colors: Any,
    color_interpolation: Any,
    gltf: Any,
    builder: GLBBuilder,
    texture_cache: dict[tuple[str, str, str], int],
    image_cache: dict[str, int],
    sampler_cache: dict[tuple[int, int], int],
) -> int | None:
    """Resolve GLTF material index from USD bindings or displayColor fallback.

    Parameters
    ----------
    prim : Any
        The USD prim to get the material for.
    display_colors : Any
        The displayColor values to use for the material.
    color_interpolation : Any
        The interpolation method for the display colors.
    gltf : Any
        The glTF document to modify with new textures, images, and samplers as needed.
    builder : GLBBuilder
        The GLBBuilder instance managing the binary buffer.
    texture_cache : dict[tuple[str, str, str], int]
        Cache mapping (file_path, wrap_s, wrap_t) to glTF texture indices.
    image_cache : dict[str, int]
        Cache mapping file paths to glTF image indices.
    sampler_cache : dict[tuple[int, int], int]
        Cache mapping (wrap_s, wrap_t) to glTF sampler indices.

    Returns
    -------
    int | None
        The index of the resolved GLTF material, or None if no material is found.
    """
    mat_index = None
    binding = UsdShade.MaterialBindingAPI(prim).GetDirectBinding()
    if binding:
        material = binding.GetMaterial()
        if material:
            surface_source = material.ComputeSurfaceSource()
            shader = surface_source[0] if surface_source else None
            if shader and shader.GetPrim().IsValid():
                mat = _build_material_from_shader(shader, prim.GetName())
                _apply_preview_surface_textures(
                    shader,
                    mat,
                    gltf,
                    builder,
                    texture_cache,
                    image_cache,
                    sampler_cache,
                )
                mat_index = _append_material_and_get_index(gltf, mat)

    vertex_interp = {UsdGeom.Tokens.vertex, UsdGeom.Tokens.varying}
    if mat_index is None and display_colors:
        if color_interpolation in vertex_interp:
            # Create a white material to properly use vertex colors (COLOR_0)
            pbr = pygltflib.PbrMetallicRoughness(baseColorFactor=[1.0, 1.0, 1.0, 1.0])
            mat = pygltflib.Material(pbrMetallicRoughness=pbr, name=f"{prim.GetName()}_vertexColor", doubleSided=True)
            mat_index = _append_material_and_get_index(gltf, mat)
        else:
            # Use the first color value as a uniform material
            mat = _build_display_color_material(display_colors, prim.GetName())
            mat_index = _append_material_and_get_index(gltf, mat)

    return mat_index
