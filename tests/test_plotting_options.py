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
"""Tests for the ``PlottingOptions`` dataclass."""

from ansys.tools.visualization_interface.utils.clip_plane import ClipPlane
from ansys.tools.visualization_interface.utils.plotting_options import PlottingOptions


def test_default_construction():
    """All fields default to None / empty dict."""
    opts = PlottingOptions()
    assert opts.name_filter is None
    assert opts.clipping_plane is None
    assert opts.extra == {}


def test_explicit_construction():
    """Fields can be set directly on the dataclass."""
    plane = ClipPlane()
    opts = PlottingOptions(name_filter="wheel", clipping_plane=plane, extra={"color": "red"})
    assert opts.name_filter == "wheel"
    assert opts.clipping_plane is plane
    assert opts.extra == {"color": "red"}


def test_from_kwargs_name_filter():
    """name_filter is parsed into its typed field."""
    kwargs = {"name_filter": "^Wheel"}
    opts = PlottingOptions.from_kwargs(kwargs)
    assert opts.name_filter == "^Wheel"


def test_from_kwargs_clipping_plane():
    """clipping_plane is parsed into its typed field."""
    plane = ClipPlane(normal=(0, 1, 0), origin=(0, 0.5, 0))
    kwargs = {"clipping_plane": plane}
    opts = PlottingOptions.from_kwargs(kwargs)
    assert opts.clipping_plane is plane


def test_from_kwargs_both_framework_fields():
    """Both framework fields are parsed together."""
    plane = ClipPlane()
    kwargs = {"name_filter": "body", "clipping_plane": plane}
    opts = PlottingOptions.from_kwargs(kwargs)
    assert opts.name_filter == "body"
    assert opts.clipping_plane is plane




def test_from_kwargs_renderer_options_go_to_extra():
    """Unknown keys are collected into extra."""
    kwargs = {"color": "blue", "opacity": 0.5, "smooth_shading": True}
    opts = PlottingOptions.from_kwargs(kwargs)
    assert opts.name_filter is None
    assert opts.clipping_plane is None
    assert opts.extra == {"color": "blue", "opacity": 0.5, "smooth_shading": True}


def test_from_kwargs_mixed_fields_and_renderer_options():
    """Framework fields land in their attributes; the rest goes to extra."""
    plane = ClipPlane()
    kwargs = {
        "name_filter": "sphere",
        "clipping_plane": plane,
        "color": "green",
        "show_edges": True,
    }
    opts = PlottingOptions.from_kwargs(kwargs)
    assert opts.name_filter == "sphere"
    assert opts.clipping_plane is plane
    assert opts.extra == {"color": "green", "show_edges": True}


def test_from_kwargs_clears_original_dict():
    """The original kwargs dict is empty after from_kwargs."""
    kwargs = {"name_filter": "cube", "color": "red"}
    PlottingOptions.from_kwargs(kwargs)
    assert kwargs == {}
