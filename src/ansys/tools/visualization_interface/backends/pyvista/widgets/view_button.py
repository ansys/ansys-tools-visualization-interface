# Copyright (C) 2024 - 2025 ANSYS, Inc. and/or its affiliates.
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
"""Provides the view button widget for changing the camera view."""

from enum import Enum

from pyvista import Plotter

from ansys.tools.visualization_interface.backends.pyvista.widgets.button import Button


class ViewDirection(Enum):
    """Provides an enum with the available views."""

    XYPLUS = 0, "+xy", (5, 220)
    XYMINUS = 1, "-xy", (5, 251)
    XZPLUS = 2, "+xz", (5, 282)
    XZMINUS = 3, "-xz", (5, 313)
    YZPLUS = 4, "+yz", (5, 344)
    YZMINUS = 5, "-yz", (5, 375)
    ISOMETRIC = 6, "isometric", (5, 406)


class ViewButton(Button):
    """Provides for changing the view.

    Parameters
    ----------
    plotter : Plotter
        Plotter to draw the buttons on.
    direction : ViewDirection
        Direction of the view.

    """

    def __init__(self, plotter: Plotter, direction: tuple, dark_mode: bool = False) -> None:
        """Initialize the ``ViewButton`` class."""
        super().__init__(plotter, direction, dark_mode)
        self.direction = direction
        self.update()

    def callback(self, state: bool) -> None:
        """Change the view depending on button interaction.

        Parameters
        ----------
        state : bool
            Whether the state of the button, which is inherited from PyVista, is ``True``.

        Raises
        ------
        NotImplementedError
            Raised if the specified direction is not implemented.

        """
        if self.direction == ViewDirection.XYPLUS:
            self.plotter.view_xy()
        elif self.direction == ViewDirection.XYMINUS:
            self.plotter.view_yx()
        elif self.direction == ViewDirection.XZPLUS:
            self.plotter.view_xz()
        elif self.direction == ViewDirection.XZMINUS:
            self.plotter.view_zx()
        elif self.direction == ViewDirection.YZPLUS:
            self.plotter.view_yz()
        elif self.direction == ViewDirection.YZMINUS:
            self.plotter.view_zy()
        elif self.direction == ViewDirection.ISOMETRIC:
            self.plotter.view_isometric()
        else:  # pragma: no cover
            raise NotImplementedError(
                f"ViewDirection {self.direction.name} is not implemented as a widget."
            )
