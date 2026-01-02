# Copyright (C) 2024 - 2026 ANSYS, Inc. and/or its affiliates.
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
"""Provides the ``ClipPlane`` class."""

from typing import Tuple


class ClipPlane:
    """Provides the clipping plane for clipping meshes in the plotter.

    The clipping plane is defined by both normal and origin vectors.

    Parameters
    ----------
    normal : Tuple[float, float, float], default: (1, 0, 0)
        Normal of the plane.
    origin : Tuple[float, float, float], default: (0, 0, 0)
        Origin point of the plane.

    """

    def __init__(
        self,
        normal: Tuple[float, float, float] = (1, 0, 0),
        origin: Tuple[float, float, float] = (0, 0, 0),
    ):
        """Initialize the ``ClipPlane`` class."""
        self._normal = normal
        self._origin = origin

    @property
    def normal(self) -> Tuple[float, float, float]:
        """Normal of the plane.

        Returns
        -------
        Tuple[float, float, float]
            Normal of the plane.

        """
        return self._normal

    @normal.setter
    def normal(self, value: Tuple[float, float, float]) -> None:
        """Set the normal of the plane.

        Parameters
        ----------
        value : Tuple[float, float, float]
            Normal of the plane.

        """
        self._normal = value

    @property
    def origin(self) -> Tuple[float, float, float]:
        """Origin of the plane.

        Returns
        -------
        Tuple[float, float, float]
            Origin of the plane.

        """
        return self._origin

    @origin.setter
    def origin(self, value: Tuple[float, float, float]) -> None:
        """Set the origin of the plane.

        Parameters
        ----------
        value : Tuple[float, float, float]
            Origin of the plane.

        """
        self._origin = value
