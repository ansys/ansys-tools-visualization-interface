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

"""Animation support for PyVista backend."""

from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional, Union

import pyvista as pv

from ansys.tools.visualization_interface.utils.logger import logger

# Dark mode detection threshold (same as in pyvista.py)
DARK_MODE_THRESHOLD = 120


class AnimationState(Enum):
    """Animation playback states."""

    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


class FrameSequence(ABC):
    """Abstract interface for frame data sources.

    This class provides an abstraction for different frame storage strategies,
    allowing for in-memory, lazy-loaded, or computed frame sequences.
    """

    @abstractmethod
    def get_frame(self, index: int) -> Any:
        """Retrieve frame at given index.

        Parameters
        ----------
        index : int
            Frame index to retrieve.

        Returns
        -------
        Any
            Frame data (typically a PyVista mesh or MeshObjectPlot).
        """
        pass

    @abstractmethod
    def __len__(self) -> int:
        """Return total number of frames.

        Returns
        -------
        int
            Total frame count.
        """
        pass


class InMemoryFrameSequence(FrameSequence):
    """Frame sequence with all frames pre-loaded in memory.

    This is the simplest strategy, suitable for small to medium datasets
    where all frames can fit in memory.

    Parameters
    ----------
    frames : List[Any]
        List of frame objects (meshes or mesh objects).
    """

    def __init__(self, frames: List[Any]):
        """Initialize with pre-loaded frames."""
        if not frames:
            raise ValueError("Frame list cannot be empty")
        self._frames = frames

    def get_frame(self, index: int) -> Any:
        """Retrieve frame at given index."""
        return self._frames[index % len(self._frames)]

    def __len__(self) -> int:
        """Return total number of frames."""
        return len(self._frames)


class Animation:
    """Animation controller for PyVista visualizations.

    This class manages animation playback, providing play/pause/stop controls,
    frame stepping, timeline scrubbing, and export capabilities.

    Parameters
    ----------
    plotter : pv.Plotter
        PyVista plotter instance to animate.
    frames : FrameSequence or List[Any]
        Frame sequence or list of frame objects to animate.
    fps : int, optional
        Frames per second for playback (default: 30).
    loop : bool, optional
        Whether to loop animation continuously (default: False).
    scalar_bar_args : dict, optional
        Scalar bar and rendering arguments to apply. Supports:
        - ``clim`` : tuple - Fixed color scale (min, max) for all frames
        - ``title`` : str - Scalar bar title
        - ``color`` : str - Scalar bar text color
        - Other parameters accepted by PyVista's ``add_mesh`` method

    Examples
    --------
    Create and play a simple animation:

    >>> from ansys.tools.visualization_interface import Plotter
    >>> plotter = Plotter(backend='pyvista')
    >>> frames = [mesh1, mesh2, mesh3]
    >>> animation = plotter.animate(frames, fps=30, loop=True)
    >>> animation.play()
    """

    def __init__(
        self,
        plotter: pv.Plotter,
        frames: Union[FrameSequence, List[Any]],
        fps: int = 30,
        loop: bool = False,
        scalar_bar_args: Optional[dict] = None,
        **plot_kwargs,
    ):
        """Initialize animation controller.

        Parameters
        ----------
        plotter : pv.Plotter
            PyVista plotter instance.
        frames : Union[FrameSequence, List[Any]]
            Frame sequence or list of frames.
        fps : int, optional
            Frames per second. Default is 30.
        loop : bool, optional
            Whether to loop animation. Default is False.
        scalar_bar_args : dict, optional
            Scalar bar arguments.
        **plot_kwargs
            Additional keyword arguments passed to add_mesh (e.g., cmap, opacity).
        """
        self._plotter = plotter

        # Convert list to FrameSequence if needed
        if isinstance(frames, list):
            self._frames = InMemoryFrameSequence(frames)
        else:
            self._frames = frames

        if fps <= 0:
            raise ValueError("FPS must be positive")
        self._fps = fps

        self._loop = loop
        self._state = AnimationState.STOPPED
        self._current_frame = 0
        self._timer_id = None
        self._actors = []
        self._frame_slider = None
        self._is_playing = False

        # Store additional plot options (cmap, opacity, etc.)
        self._plot_kwargs = plot_kwargs

        # Store scalar bar arguments
        self._scalar_bar_args = {}
        self._clim = None

        if scalar_bar_args:
            if "clim" in scalar_bar_args:
                self._clim = scalar_bar_args["clim"]
                scalar_bar_args = {k: v for k, v in scalar_bar_args.items() if k != "clim"}
            self._scalar_bar_args = scalar_bar_args

        # Calculate global color scale if not provided
        if self._clim is None:
            self._calculate_global_color_scale()

        logger.info(
            f"Animation created with {len(self._frames)} frames at {fps} FPS"
        )

    def _calculate_global_color_scale(self):
        """Calculate global min/max for fixed color scale across frames."""
        try:
            first_frame = self._frames.get_frame(0)
            last_frame = self._frames.get_frame(len(self._frames) - 1)

            global_min = float("inf")
            global_max = float("-inf")

            for frame in [first_frame, last_frame]:
                mesh = frame.mesh if hasattr(frame, "mesh") else frame if isinstance(frame, pv.DataSet) else None
                if mesh and mesh.active_scalars is not None:
                    scalars = mesh.active_scalars
                    global_min = min(global_min, scalars.min())
                    global_max = max(global_max, scalars.max())

            if global_min != float("inf"):
                self._clim = (global_min, global_max)
                logger.info(f"Calculated global color scale: [{global_min:.6f}, {global_max:.6f}]")
        except Exception as e:
            logger.warning(f"Could not calculate global color scale: {e}")

    def _is_dark_mode(self) -> bool:
        """Detect if plotter is in dark mode based on background color."""
        try:
            bg_color = self._plotter.background_color
            if hasattr(bg_color, 'int_rgb'):
                return all(c < DARK_MODE_THRESHOLD for c in bg_color.int_rgb)
        except Exception as e:
            logger.debug(f"Could not detect dark mode from background color: {e}")
        return False

    @property
    def state(self) -> AnimationState:
        """Current animation state."""
        return self._state

    @property
    def current_frame(self) -> int:
        """Current frame index."""
        return self._current_frame

    @property
    def total_frames(self) -> int:
        """Total number of frames."""
        return len(self._frames)

    @property
    def fps(self) -> int:
        """Frames per second."""
        return self._fps

    @fps.setter
    def fps(self, value: int):
        """Set frames per second."""
        if value <= 0:
            raise ValueError("FPS must be positive")
        self._fps = value
        if self._state == AnimationState.PLAYING:
            self._restart_timer()

    def play(self):
        """Start or resume animation playback."""
        if self._state != AnimationState.PLAYING:
            logger.info("Starting animation playback")
            self._state = AnimationState.PLAYING
            self._start_timer()

    def pause(self):
        """Pause animation playback."""
        if self._state == AnimationState.PLAYING:
            logger.info("Pausing animation")
            self._state = AnimationState.PAUSED
            self._stop_timer()

    def stop(self):
        """Stop animation and reset to first frame."""
        logger.info("Stopping animation")
        self._stop_timer()
        self._current_frame = 0
        self._state = AnimationState.STOPPED
        self._update_display()

    def step_forward(self):
        """Advance one frame forward."""
        self._current_frame = (self._current_frame + 1) % len(self._frames)
        self._update_display()
        if self._frame_slider:
            self._frame_slider.GetRepresentation().SetValue(self._current_frame)

    def step_backward(self):
        """Rewind one frame backward."""
        self._current_frame = (self._current_frame - 1) % len(self._frames)
        self._update_display()
        if self._frame_slider:
            self._frame_slider.GetRepresentation().SetValue(self._current_frame)

    def seek(self, frame_index: int):
        """Jump to specific frame.

        Parameters
        ----------
        frame_index : int
            Target frame index.
        """
        if frame_index < 0 or frame_index >= len(self._frames):
            raise ValueError(
                f"Frame index {frame_index} out of range [0, {len(self._frames)})"
            )
        self._current_frame = frame_index
        self._update_display()
        logger.info(f"Seeked to frame {frame_index}")

    def _start_timer(self):
        """Start VTK timer for frame updates."""
        # This is intentionally a no-op - the actual timer is started by _start_animation_thread
        pass

    def _start_animation_thread(self):
        """Start animation playback using VTK timer."""
        if not hasattr(self._plotter, 'iren') or self._plotter.iren is None:
            logger.error("No interactor available for timer")
            return

        # Create timer callback
        def timer_callback(obj, event):
            """VTK timer callback - runs on main thread."""
            if not self._is_playing:
                return

            # Advance to next frame
            next_frame = (self._current_frame + 1) % self.total_frames

            # Check if we should loop
            if next_frame == 0 and not self._loop:
                self._is_playing = False
                return

            # Get frame
            frame = self._frames.get_frame(next_frame)
            mesh = self._extract_mesh(frame)
            if not mesh:
                return

            # Update actor's dataset
            if self._actors:
                for actor in self._actors:
                    if hasattr(actor, 'mapper') and hasattr(actor.mapper, 'dataset'):
                        actor.mapper.dataset = mesh.copy(deep=False)
                self._current_frame = next_frame

                # Update frame slider to show current position
                if self._frame_slider:
                    rep = self._frame_slider.GetRepresentation()
                    rep.SetValue(next_frame)

                self._plotter.render()

        # Add timer observer
        interval_ms = int(1000.0 / self._fps)
        self._timer_id = self._plotter.iren.add_observer('TimerEvent', timer_callback)
        self._plotter.iren.create_timer(interval_ms, repeating=True)

        logger.debug(f"VTK timer started: {interval_ms}ms interval")

    def _stop_timer(self):
        """Stop timer."""
        self._timer_id = None

    def _restart_timer(self):
        """Restart timer with updated interval."""
        if self._state == AnimationState.PLAYING:
            self._stop_timer()
            self._start_timer()

    def _on_timer(self):
        """Timer callback to advance frame."""
        # Check if we should still be playing
        if self._state != AnimationState.PLAYING:
            return

        self.step_forward()
        if self._current_frame == 0 and not self._loop:
            self.pause()

    def _extract_mesh(self, frame):
        """Extract PyVista mesh from frame object."""
        if hasattr(frame, "mesh"):
            return frame.mesh
        elif isinstance(frame, pv.DataSet):
            return frame
        return None

    def _update_display(self):
        """Update visualization for current frame."""
        try:
            frame = self._frames.get_frame(self._current_frame)
            mesh = self._extract_mesh(frame)
            if not mesh:
                logger.warning(f"Unknown frame type: {type(frame)}")
                return

            if not self._actors:
                plot_options = getattr(frame, "plot_options", {}).copy()
                plot_options.update(self._plot_kwargs)

                if self._clim is not None:
                    plot_options["clim"] = self._clim
                if self._scalar_bar_args:
                    plot_options["scalar_bar_args"] = self._scalar_bar_args

                actor = self._plotter.add_mesh(mesh, **plot_options)
                if actor:
                    self._actors = actor if isinstance(actor, list) else [actor]
            else:
                for actor in self._actors:
                    if hasattr(actor, 'mapper') and hasattr(actor.mapper, 'dataset'):
                        actor.mapper.dataset = mesh.copy(deep=False)

            self._plotter.render()
        except Exception as e:
            logger.error(f"Error updating frame {self._current_frame}: {e}")

    def save(
        self,
        filename: Union[str, Path],
        quality: int = 5,
        framerate: Optional[int] = None,
        close_plotter: bool = False,
    ):
        """Export animation to video file.

        Parameters
        ----------
        filename : str or Path
            Output filename (.mp4, .gif, .avi).
        quality : int, optional
            Video quality (1-10, higher is better). Default is 5.
        framerate : int, optional
            Output framerate. If None, uses animation fps.
        close_plotter : bool, optional
            If True, closes plotter after saving. Default is False.
        """
        filename = Path(filename)
        framerate = framerate or self._fps
        logger.info(f"Exporting animation to {filename} at {framerate} FPS")

        try:
            self._plotter.open_movie(str(filename), framerate=framerate, quality=quality)
            for i in range(len(self._frames)):
                self.seek(i)
                self._plotter.write_frame()

            if hasattr(self._plotter, 'mwriter') and self._plotter.mwriter is not None:
                self._plotter.mwriter.close()
                self._plotter.mwriter = None

            if close_plotter:
                self._plotter.close()

            logger.info(f"Animation exported successfully to {filename}")
        except Exception as e:
            logger.error(f"Failed to export animation: {e}")
            raise

    def _add_animation_controls(self):
        """Add interactive widgets for animation control."""
        from ansys.tools.visualization_interface.backends.pyvista.widgets.next_button import NextButton
        from ansys.tools.visualization_interface.backends.pyvista.widgets.play_pause_button import PlayPauseButton
        from ansys.tools.visualization_interface.backends.pyvista.widgets.previous_button import PreviousButton
        from ansys.tools.visualization_interface.backends.pyvista.widgets.save_gif_button import SaveGifButton
        from ansys.tools.visualization_interface.backends.pyvista.widgets.stop_button import StopButton

        dark_mode = self._is_dark_mode()

        # Create animation control buttons
        PlayPauseButton(self._plotter, self, dark_mode=dark_mode)
        StopButton(self._plotter, self, dark_mode=dark_mode)
        PreviousButton(self._plotter, self, dark_mode=dark_mode)
        NextButton(self._plotter, self, dark_mode=dark_mode)
        SaveGifButton(self._plotter, self, dark_mode=dark_mode)

        # Frame slider
        self._frame_slider = self._plotter.add_slider_widget(
            lambda value: self.seek(int(value)) if int(value) != self._current_frame else None,
            rng=[0, self.total_frames - 1],
            value=0,
            title="Frame",
            pointa=(0.25, 0.92),
            pointb=(0.75, 0.92),
            style='modern',
            fmt='%0.0f'
        )

        logger.info("Animation controls added")

    def show(self, show_controls: bool = True, **kwargs):
        """Display animation with the plotter.

        Parameters
        ----------
        show_controls : bool, optional
            If True, shows interactive controls. Default is True.
        **kwargs
            Additional arguments passed to plotter.show().
        """
        logger.info(f"Showing animation: {self.total_frames} frames at {self._fps} FPS")

        if not hasattr(self._plotter, 'iren') or self._plotter.iren is None:
            raise RuntimeError("Cannot show animation - plotter is closed")

        self.seek(0)

        if show_controls:
            self._add_animation_controls()
            self._plotter.show(**kwargs)
            if self._timer_id:
                try:
                    self._plotter.iren.remove_observer(self._timer_id)
                except Exception as e:
                    logger.debug(f"Could not remove timer observer: {e}")
        else:
            logger.info("Displaying first frame only (no controls)")
            self._plotter.show(**kwargs)
