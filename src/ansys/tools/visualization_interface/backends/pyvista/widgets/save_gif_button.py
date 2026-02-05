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
"""Provides the save GIF button widget for animation control."""

import datetime
from enum import Enum

from pyvista import Plotter

from ansys.tools.visualization_interface.backends.pyvista.widgets.button import Button
from ansys.tools.visualization_interface.utils.logger import logger


class SaveGifButtonConfig(Enum):
    """Provides configuration for the save GIF button."""

    SAVE_GIF = 0, "save", (210, 10)


class SaveGifButton(Button):
    """Provides GIF export control for animations.

    This button exports the animation as a timestamped GIF file.

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
        """Initialize the ``SaveGifButton`` class."""
        self._animation = animation
        super().__init__(plotter, SaveGifButtonConfig.SAVE_GIF, dark_mode)
        self.update()

    def callback(self, state: bool) -> None:
        """Export animation as GIF file.

        Parameters
        ----------
        state : bool
            Whether the button is active.
        """
        if state:
            logger.debug("Save GIF button pressed")

            # Check for imageio
            import importlib.util
            if importlib.util.find_spec("imageio") is None:
                logger.error("imageio package required for GIF export. Install with: pip install imageio")
                rep = self._button.GetRepresentation()
                rep.SetState(0)
                return

            # Generate timestamped filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"animation_{timestamp}.gif"

            # Pause if playing
            was_playing = self._animation._is_playing
            if was_playing:
                self._animation._is_playing = False

            # Remember current frame
            original_frame = self._animation._current_frame

            try:
                # Save animation
                self._animation.save(filename, quality=8, close_plotter=False)
                logger.info(f"Animation saved to {filename}")

                # Return to original frame
                self._animation.seek(original_frame)
                if self._animation._frame_slider:
                    rep = self._animation._frame_slider.GetRepresentation()
                    rep.SetValue(original_frame)

            except Exception as e:
                logger.error(f"Failed to save animation: {e}")

            # Resume if was playing
            if was_playing:
                self._animation._is_playing = True

            # Reset button state (momentary button behavior)
            rep = self._button.GetRepresentation()
            rep.SetState(0)
