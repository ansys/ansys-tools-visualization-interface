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

"""Tests for animation functionality."""

import numpy as np
import pytest
import pyvista as pv

from ansys.tools.visualization_interface import Plotter
from ansys.tools.visualization_interface.backends.pyvista import (
    Animation,
    AnimationState,
    InMemoryFrameSequence,
)


@pytest.fixture
def sample_frames():
    """Create sample mesh frames for testing."""
    frames = []
    for i in range(5):
        sphere = pv.Sphere(radius=1.0 + i * 0.1)
        sphere["data"] = np.ones(sphere.n_points) * i
        frames.append(sphere)
    return frames


class TestFrameSequence:
    """Tests for FrameSequence classes."""

    def test_in_memory_frame_sequence(self, sample_frames):
        """Test InMemoryFrameSequence."""
        seq = InMemoryFrameSequence(sample_frames)

        assert len(seq) == 5
        assert seq.get_frame(0) is sample_frames[0]
        assert seq.get_frame(4) is sample_frames[4]

        # Test wrapping
        assert seq.get_frame(5) is sample_frames[0]

    def test_empty_frame_sequence_raises(self):
        """Test that empty frame list raises ValueError."""
        with pytest.raises(ValueError, match="Frame list cannot be empty"):
            InMemoryFrameSequence([])


class TestAnimation:
    """Tests for Animation class."""

    def test_animation_creation(self, sample_frames):
        """Test basic animation creation."""
        plotter = pv.Plotter(off_screen=True)
        animation = Animation(plotter, sample_frames, fps=30, loop=True)

        assert animation.total_frames == 5
        assert animation.fps == 30
        assert animation.state == AnimationState.STOPPED
        assert animation.current_frame == 0

    def test_animation_with_frame_sequence(self, sample_frames):
        """Test animation with FrameSequence."""
        plotter = pv.Plotter(off_screen=True)
        seq = InMemoryFrameSequence(sample_frames)
        animation = Animation(plotter, seq, fps=20)

        assert animation.total_frames == 5
        assert animation.fps == 20

    def test_invalid_fps_raises(self, sample_frames):
        """Test that invalid FPS raises ValueError."""
        plotter = pv.Plotter(off_screen=True)

        with pytest.raises(ValueError, match="FPS must be positive"):
            Animation(plotter, sample_frames, fps=0)

        with pytest.raises(ValueError, match="FPS must be positive"):
            Animation(plotter, sample_frames, fps=-10)

    def test_state_transitions(self, sample_frames):
        """Test animation state machine."""
        plotter = pv.Plotter(off_screen=True)
        animation = Animation(plotter, sample_frames, fps=30)

        # Initial state
        assert animation.state == AnimationState.STOPPED

        # Note: play() won't work in off_screen mode without interactor
        # So we manually test state changes
        animation._state = AnimationState.PLAYING
        assert animation.state == AnimationState.PLAYING

        # Test pause
        animation._state = AnimationState.PAUSED
        assert animation.state == AnimationState.PAUSED

        # Test stop
        animation.stop()
        assert animation.state == AnimationState.STOPPED
        assert animation.current_frame == 0

    def test_step_forward(self, sample_frames):
        """Test stepping forward through frames."""
        plotter = pv.Plotter(off_screen=True)
        animation = Animation(plotter, sample_frames, fps=30)

        assert animation.current_frame == 0

        animation.step_forward()
        assert animation.current_frame == 1

        animation.step_forward()
        assert animation.current_frame == 2

        # Test wrapping
        animation.seek(4)
        animation.step_forward()
        assert animation.current_frame == 0

    def test_step_backward(self, sample_frames):
        """Test stepping backward through frames."""
        plotter = pv.Plotter(off_screen=True)
        animation = Animation(plotter, sample_frames, fps=30)

        animation.seek(2)
        assert animation.current_frame == 2

        animation.step_backward()
        assert animation.current_frame == 1

        animation.step_backward()
        assert animation.current_frame == 0

        # Test wrapping
        animation.step_backward()
        assert animation.current_frame == 4

    def test_seek(self, sample_frames):
        """Test seeking to specific frame."""
        plotter = pv.Plotter(off_screen=True)
        animation = Animation(plotter, sample_frames, fps=30)

        animation.seek(3)
        assert animation.current_frame == 3

        animation.seek(0)
        assert animation.current_frame == 0

        # Test out of range
        with pytest.raises(ValueError, match="out of range"):
            animation.seek(10)

        with pytest.raises(ValueError, match="out of range"):
            animation.seek(-1)

    def test_fps_update(self, sample_frames):
        """Test changing FPS dynamically."""
        plotter = pv.Plotter(off_screen=True)
        animation = Animation(plotter, sample_frames, fps=30)

        assert animation.fps == 30

        animation.fps = 60
        assert animation.fps == 60

        with pytest.raises(ValueError, match="FPS must be positive"):
            animation.fps = 0


class TestPlotterAnimation:
    """Tests for Plotter.animate() method."""

    def test_plotter_animate_basic(self, sample_frames):
        """Test basic animation creation via Plotter."""
        plotter = Plotter()
        animation = plotter.animate(sample_frames, fps=20, loop=True)

        assert isinstance(animation, Animation)
        assert animation.total_frames == 5
        assert animation.fps == 20

    def test_plotter_animate_with_scalar_bar_args(self, sample_frames):
        """Test animation with scalar bar arguments."""
        plotter = Plotter()
        animation = plotter.animate(
            sample_frames,
            fps=30,
            scalar_bar_args={"clim": (0, 5), "title": "Test"}
        )

        assert animation is not None
        assert animation.total_frames == 5

    def test_plotter_animate_empty_frames_raises(self):
        """Test that empty frames list raises ValueError."""
        plotter = Plotter()

        with pytest.raises(ValueError, match="Frame list cannot be empty"):
            plotter.animate([], fps=30)


class TestBackendIntegration:
    """Tests for backend integration."""

    def test_backend_create_animation(self, sample_frames):
        """Test backend.create_animation() method."""
        plotter = Plotter()
        animation = plotter.backend.create_animation(
            sample_frames,
            fps=25,
            loop=True
        )

        assert isinstance(animation, Animation)
        assert animation.total_frames == 5
        assert animation.fps == 25

    def test_backend_with_frame_sequence(self, sample_frames):
        """Test backend with custom FrameSequence."""
        plotter = Plotter()
        seq = InMemoryFrameSequence(sample_frames)

        animation = plotter.backend.create_animation(seq, fps=30)

        assert animation.total_frames == 5
