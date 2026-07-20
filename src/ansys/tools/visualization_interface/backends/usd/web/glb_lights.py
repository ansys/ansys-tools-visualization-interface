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

"""USD-to-glTF light conversion helpers."""

from __future__ import annotations

from typing import Any

from pxr import Usd, UsdGeom, UsdLux
import pygltflib


def _ensure_lights_extension(gltf: Any) -> list[dict[str, Any]]:
    """Ensure KHR_lights_punctual is declared and return its light list.

    Parameters
    ----------
    gltf : Any
        The glTF document to check and modify.

    Returns
    -------
    list[dict[str, Any]]
        The list of lights in the KHR_lights_punctual extension, which may be newly created.
    """
    if gltf.extensionsUsed is None:
        gltf.extensionsUsed = []
    if "KHR_lights_punctual" not in gltf.extensionsUsed:
        gltf.extensionsUsed.append("KHR_lights_punctual")

    if gltf.extensions is None:
        gltf.extensions = {}

    lights_ext = gltf.extensions.get("KHR_lights_punctual")
    if lights_ext is None:
        lights_ext = {"lights": []}
        gltf.extensions["KHR_lights_punctual"] = lights_ext

    lights = lights_ext.get("lights")
    if lights is None:
        lights = []
        lights_ext["lights"] = lights

    return lights


def _get_light_schema_and_type(prim: Any) -> tuple[Any, str] | None:
    """Map a USD light prim to a KHR_lights_punctual-compatible type.

    Parameters
    ----------
    prim : Any
        The USD light prim to map.

    Returns
    -------
    tuple[Any, str] | None
        A tuple containing the USD light schema and the corresponding glTF light type,
        or None if the prim is not a supported light type.
    """
    if prim.IsA(UsdLux.DistantLight):
        return UsdLux.DistantLight(prim), "directional"

    if prim.IsA(UsdLux.SphereLight):
        return UsdLux.SphereLight(prim), "point"

    if prim.IsA(UsdLux.DiskLight):
        return UsdLux.DiskLight(prim), "point"

    return None


def _make_gltf_light(prim: Any) -> dict[str, Any] | None:
    """Build one glTF punctual light description from a USD light prim.

    Parameters
    ----------
    prim : Any
        The USD light prim to convert.

    Returns
    -------
    dict[str, Any] | None
        A dictionary representing the glTF light, or None if the prim is not a supported light type.
    """
    schema_and_type = _get_light_schema_and_type(prim)
    if schema_and_type is None:
        return None

    light_schema, light_type = schema_and_type
    color_value = light_schema.GetColorAttr().Get()
    intensity_value = light_schema.GetIntensityAttr().Get()
    exposure_value = light_schema.GetExposureAttr().Get()

    if intensity_value is None:
        intensity_value = 1.0
    intensity = float(intensity_value)
    if exposure_value is not None:
        intensity *= 2.0 ** float(exposure_value)

    # USD light intensity conventions vary across renderers and can be orders
    # of magnitude larger than typical WebGL values.
    if light_type == "directional":
        intensity /= 50000.0
    else:
        intensity /= 500.0
    intensity = max(0.0, min(intensity, 20.0))

    if color_value is None:
        color = [1.0, 1.0, 1.0]
    else:
        color = [float(color_value[0]), float(color_value[1]), float(color_value[2])]

    light: dict[str, Any] = {
        "type": light_type,
        "color": color,
        "intensity": intensity,
        "name": prim.GetName(),
    }
    return light


def append_usd_lights_to_scene(stage: Any, gltf: Any, scene: Any) -> None:
    """Convert supported USD lights into glTF KHR_lights_punctual lights.

    Parameters
    ----------
    stage : Any
        The USD stage containing the lights.
    gltf : Any
        The glTF document to modify.
    scene : Any
        The glTF scene to which the lights will be added.
    """
    lights = _ensure_lights_extension(gltf)

    for prim in stage.Traverse():
        gltf_light = _make_gltf_light(prim)
        if gltf_light is None:
            continue

        light_index = len(lights)
        lights.append(gltf_light)

        node = pygltflib.Node(
            name=prim.GetName(),
            extensions={"KHR_lights_punctual": {"light": light_index}},
        )

        xformable = UsdGeom.Xformable(prim)
        if xformable:
            world = xformable.ComputeLocalToWorldTransform(Usd.TimeCode.Default())
            translation = world.ExtractTranslation()
            node.translation = [float(translation[0]), float(translation[1]), float(translation[2])]

        gltf.nodes.append(node)
        scene.nodes.append(len(gltf.nodes) - 1)
