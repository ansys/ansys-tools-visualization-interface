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

"""World-transform helpers for USD web export.

Three.js is Y-up, so points are baked into world space and Z-up stages are
rotated -90 degrees about X (``(x, y, z) -> (x, z, -y)``).
"""

from __future__ import annotations

from typing import Any

import numpy as np
from pxr import Usd, UsdGeom

# Row-vector convention (as in USD): p_out = p_in @ M.
_Z_UP_TO_Y_UP = np.array(
    [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, -1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]
)


def world_matrix(prim: Any) -> np.ndarray:
    """Return the 4x4 local-to-world matrix of *prim*, converted to Y-up.

    Parameters
    ----------
    prim : Any
        The USD prim.

    Returns
    -------
    np.ndarray
        A 4x4 matrix in USD row-vector convention (``p_out = p_in @ M``).
    """
    matrix = np.array(UsdGeom.Xformable(prim).ComputeLocalToWorldTransform(Usd.TimeCode.Default()), dtype=float)
    if UsdGeom.GetStageUpAxis(prim.GetStage()) == UsdGeom.Tokens.z:
        matrix = matrix @ _Z_UP_TO_Y_UP
    return matrix


def transform_points(points: Any, matrix: np.ndarray) -> np.ndarray:
    """Apply a 4x4 row-vector matrix to an ``(N, 3)`` array of points.

    Parameters
    ----------
    points : Any
        Points convertible to an ``(N, 3)`` float array.
    matrix : np.ndarray
        A 4x4 matrix in USD row-vector convention.

    Returns
    -------
    np.ndarray
        The transformed ``(N, 3)`` points.
    """
    pts = np.asarray(points, dtype=float).reshape(-1, 3)
    return pts @ matrix[:3, :3] + matrix[3, :3]


def flips_winding(matrix: np.ndarray) -> bool:
    """Return True when *matrix* mirrors geometry (negative determinant).

    Parameters
    ----------
    matrix : np.ndarray
        A 4x4 matrix in USD row-vector convention.

    Returns
    -------
    bool
        True if triangle winding must be reversed to keep faces front-facing.
    """
    return bool(np.linalg.det(matrix[:3, :3]) < 0)
