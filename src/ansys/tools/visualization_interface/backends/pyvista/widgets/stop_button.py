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
"""Provides the stop button widget for animation control."""

from enum import Enum

from pyvista import Plotter

from ansys.tools.visualization_interface.backends.pyvista.widgets.button import Button
from ansys.tools.visualization_interface.utils.logger import logger


class StopButtonConfig(Enum):
    """Provides configuration for the stop button."""

    STOP = 0, "stop", (60, 10)


class StopButton(Button):
    """Provides stop control for animations.

    This button stops the animation and resets to the first frame.

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
        """Initialize the ``StopButton`` class."""
        self._animation = animation
        super().__init__(plotter, StopButtonConfig.STOP, dark_mode)
        self.update()

    def callback(self, state: bool) -> None:
        """Stop animation and reset to first frame.

        Parameters
        ----------
        state : bool
            Whether the button is active.
        """
        if state:
            logger.debug("Stop button pressed")
            self._animation._is_playing = False

            # Update play/pause button to play state
            if hasattr(self._animation, '_play_pause_button') and self._animation._play_pause_button:
                rep = self._animation._play_pause_button._button.GetRepresentation()
                rep.SetState(0)
                self._animation._play_pause_button._update_icon("play")

            # Reset to first frame
            self._animation.seek(0)

            # Update slider
            if self._animation._frame_slider:
                rep = self._animation._frame_slider.GetRepresentation()
                rep.SetValue(0)

            # Reset this button state (momentary button behavior)
            rep = self._button.GetRepresentation()
            rep.SetState(0)
