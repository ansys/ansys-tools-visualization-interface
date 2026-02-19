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
"""Provides the play/pause button widget for animation control."""

from enum import Enum
from pathlib import Path

from pyvista import Plotter

from ansys.tools.visualization_interface.backends.pyvista.widgets.button import Button
from ansys.tools.visualization_interface.utils.logger import logger


class PlayPauseButtonConfig(Enum):
    """Provides configuration for the play/pause button."""

    PLAY_PAUSE = 0, "play", (10, 10)


class PlayPauseButton(Button):
    """Provides play/pause toggle control for animations.

    This button switches between play and pause icons dynamically based on
    the animation state.

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
        """Initialize the ``PlayPauseButton`` class."""
        self._animation = animation
        super().__init__(plotter, PlayPauseButtonConfig.PLAY_PAUSE, dark_mode)
        self.update()

    def callback(self, state: bool) -> None:
        """Toggle between play and pause.

        Parameters
        ----------
        state : bool
            Whether the button is active (playing).
        """
        self._animation._is_playing = state

        if state:
            logger.debug("Play button pressed - starting animation")
            self._update_icon("pause")
            if not self._animation._timer_id:
                self._animation._start_animation_thread()
        else:
            logger.debug("Pause button pressed")
            self._update_icon("play")

    def _update_icon(self, icon_name: str) -> None:
        """Update button icon between play and pause.

        Parameters
        ----------
        icon_name : str
            Icon name ("play" or "pause").
        """
        from vtk import vtkPNGReader

        if self._dark_mode:
            is_inv = "_inv"
        else:
            is_inv = ""
        button_repr = self._button.GetRepresentation()
        button_icon_path = Path(
            Path(__file__).parent / "_images", f"{icon_name}{is_inv}.png"
        )
        button_icon = vtkPNGReader()
        button_icon.SetFileName(button_icon_path)
        button_icon.Update()
        image = button_icon.GetOutput()
        button_repr.SetButtonTexture(0, image)
        button_repr.SetButtonTexture(1, image)
