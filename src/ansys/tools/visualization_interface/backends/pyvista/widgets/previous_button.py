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
"""Provides the previous button widget for animation control."""

from enum import Enum

from pyvista import Plotter

from ansys.tools.visualization_interface.backends.pyvista.widgets.button import Button


class PreviousButtonConfig(Enum):
    """Provides configuration for the previous button."""

    PREVIOUS = 0, "previous", (110, 10)


class PreviousButton(Button):
    """Provides previous frame control for animations.

    This button steps backward one frame.

    Parameters
    ----------
    plotter : Plotter
        Plotter to draw the button on.
    animation : Animation
        Animation instance to control.
    dark_mode : bool, optional
        Whether to activate the dark mode or not.
    """

    def __init__(self, plotter: Plotter, animation, dark_mode: bool = False) -> None:
        """Initialize the ``PreviousButton`` class."""
        self._animation = animation
        super().__init__(plotter, PreviousButtonConfig.PREVIOUS, dark_mode)
        self.update()

    def callback(self, state: bool) -> None:
        """Step to previous frame.

        Parameters
        ----------
        state : bool
            Whether the button is active.
        """
        if state:
            self._animation.step_backward()
            # Reset button state (momentary button behavior)
            rep = self._button.GetRepresentation()
            rep.SetState(0)
