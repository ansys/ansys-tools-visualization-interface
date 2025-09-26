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
"""Test module for interactables in the picker."""
from pathlib import Path

import pytest
import pyvista as pv

from ansys.tools.visualization_interface import MeshObjectPlot, Plotter
from ansys.tools.visualization_interface.backends.pyvista import PyVistaBackend


class CustomObject:
    """Mock object for testing picking functionality."""
    def __init__(self):
        """Initialize the custom object."""
        self.name = "CustomObject"
        self.mesh = pv.Cube(center=(1, 1, 0))
    def get_mesh(self):
        """Return the mesh of the custom object."""
        return self.mesh
    def name(self):
        """Return the name of the custom object."""
        return self.name

def test_picking():
    """Adds multiblock to the plotter."""
    pv_backend = PyVistaBackend(allow_picking=True, plot_picked_names=True)

    pl = Plotter(backend=pv_backend)

    # Create custom sphere
    custom_sphere = CustomObject()
    custom_sphere.mesh = pv.Sphere(center=(0, 0, 5))
    custom_sphere.name = "CustomSphere"
    mesh_object_sphere = MeshObjectPlot(custom_sphere, custom_sphere.get_mesh())

    pl.plot(mesh_object_sphere)


    # Run the plotter and simulate a click
    pl.show(auto_close=False)

    raw_plotter = pl.backend.scene
    width, height = raw_plotter.window_size
    raw_plotter.iren._mouse_right_button_press(width//2, height//2)
    raw_plotter.iren._mouse_right_button_release(width//2, height//2)
    raw_plotter.close()
    picked = pl.backend._picked_dict
    assert "CustomSphere" in picked

# TODO: View and displace arrows tests do not give expected results, PyVista issue?
view = [
    (5, 220), # XYPLUS
    (5, 251), # XYMINUS
    (5, 282), # XZPLUS
    (5, 313), # XZMINUS
    (5, 344), # YZPLUS
    (5, 375), # YZMINUS
    (5, 406)  # ISOMETRIC

]

@pytest.mark.parametrize("view", view)
def test_view_buttons(view):
    """Test view buttons."""
    pv_backend = PyVistaBackend()

    pl = Plotter(backend=pv_backend)

    # Create custom sphere
    custom_sphere = CustomObject()
    custom_sphere.mesh = pv.Sphere(center=(0, 0, 5))
    custom_sphere.name = "CustomSphere"
    mesh_object_sphere = MeshObjectPlot(custom_sphere, custom_sphere.get_mesh())

    pl.plot(mesh_object_sphere)


    # Run the plotter and simulate a click
    pl.show(auto_close=False)

    raw_plotter = pl.backend.scene
    width, height = raw_plotter.window_size

    raw_plotter.iren._mouse_left_button_press(view)
    raw_plotter.iren._mouse_left_button_release(view)
    raw_plotter.close()

displace_arrow = [
    (5, 170), # XUP
    (5, 130), # XDOWN
    (35, 170), # YUP
    (35, 130), # YDOWN
    (65, 170), # ZUP
    (65, 130)  # ZDOWN
]

@pytest.mark.parametrize("displace_arrow", displace_arrow)
def test_displace_arrow(displace_arrow):
    """Test view buttons."""
    pv_backend = PyVistaBackend()

    pl = Plotter(backend=pv_backend)

    # Create custom sphere
    custom_sphere = CustomObject()
    custom_sphere.mesh = pv.Sphere(center=(0, 0, 5))
    custom_sphere.name = "CustomSphere"
    mesh_object_sphere = MeshObjectPlot(custom_sphere, custom_sphere.get_mesh())

    pl.plot(mesh_object_sphere)

    # Run the plotter and simulate a click
    pl.show(auto_close=False)

    raw_plotter = pl.backend.scene
    width, height = raw_plotter.window_size

    raw_plotter.iren._mouse_left_button_click(displace_arrow)
    raw_plotter.close()


def test_ruler_button():
    """Test ruler button interaction."""
    pv_backend = PyVistaBackend()

    pl = Plotter(backend=pv_backend)

    # Create custom sphere
    custom_sphere = CustomObject()
    custom_sphere.mesh = pv.Sphere(center=(0, 0, 5))
    custom_sphere.name = "CustomSphere"
    mesh_object_sphere = MeshObjectPlot(custom_sphere, custom_sphere.get_mesh())

    pl.plot(mesh_object_sphere)

    # Run the plotter and simulate a click
    pl.show(auto_close=False)

    raw_plotter = pl.backend.scene
    width, height = raw_plotter.window_size

    raw_plotter.iren._mouse_left_button_click(10, 100)
    raw_plotter.close()


def test_measure_tool():
    """Test measure tool interaction."""
    pv_backend = PyVistaBackend()

    pl = Plotter(backend=pv_backend)

    # Create custom sphere
    custom_sphere = CustomObject()
    custom_sphere.mesh = pv.Sphere(center=(0, 0, 5))
    custom_sphere.name = "CustomSphere"
    mesh_object_sphere = MeshObjectPlot(custom_sphere, custom_sphere.get_mesh())

    pl.plot(mesh_object_sphere)

    # Run the plotter and simulate a click
    pl.show(auto_close=False)

    raw_plotter = pl.backend.scene
    width, height = raw_plotter.window_size

    raw_plotter.iren._mouse_left_button_click(10, 60)
    raw_plotter.iren._mouse_left_button_click(200, 200)
    raw_plotter.iren._mouse_left_button_click(300, 300)
    raw_plotter.close()


def test_measure_tool_close():
    """Test measure tool interaction and closing."""
    pv_backend = PyVistaBackend()

    pl = Plotter(backend=pv_backend)

    # Create custom sphere
    custom_sphere = CustomObject()
    custom_sphere.mesh = pv.Sphere(center=(0, 0, 5))
    custom_sphere.name = "CustomSphere"
    mesh_object_sphere = MeshObjectPlot(custom_sphere, custom_sphere.get_mesh())

    pl.plot(mesh_object_sphere)

    # Run the plotter and simulate a click
    pl.show(auto_close=False)

    raw_plotter = pl.backend.scene
    width, height = raw_plotter.window_size

    raw_plotter.iren._mouse_left_button_click(10, 60)
    raw_plotter.iren._mouse_left_button_click(200, 200)
    raw_plotter.iren._mouse_left_button_click(300, 300)
    raw_plotter.iren._mouse_left_button_click(10, 60)

    raw_plotter.close()


def test_screenshot_button():
    """Test screenshot button interaction."""
    pv_backend = PyVistaBackend()

    pl = Plotter(backend=pv_backend)

    # Create custom sphere
    custom_sphere = CustomObject()
    custom_sphere.mesh = pv.Sphere(center=(0, 0, 5))
    custom_sphere.name = "CustomSphere"
    mesh_object_sphere = MeshObjectPlot(custom_sphere, custom_sphere.get_mesh())

    pl.plot(mesh_object_sphere)

    # Run the plotter and simulate a click
    pl.show(auto_close=False)

    raw_plotter = pl.backend.scene
    width, height = raw_plotter.window_size

    raw_plotter.iren._mouse_left_button_click(45, 100)

    raw_plotter.close()
    assert Path("screenshot.png").exists()
    Path("screenshot.png").unlink()
    assert not Path("screenshot.png").exists()


def test_hide_button():
    """Test hide button interaction."""
    pv_backend = PyVistaBackend()

    pl = Plotter(backend=pv_backend)

    # Create custom sphere
    custom_sphere = CustomObject()
    custom_sphere.mesh = pv.Sphere(center=(0, 0, 5))
    custom_sphere.name = "CustomSphere"
    mesh_object_sphere = MeshObjectPlot(custom_sphere, custom_sphere.get_mesh())

    pl.plot(mesh_object_sphere)

    # Run the plotter and simulate a click
    pl.show(auto_close=False)

    raw_plotter = pl.backend.scene
    width, height = raw_plotter.window_size

    raw_plotter.iren._mouse_left_button_click(10, 10)

    raw_plotter.close()


def test_hide_button_unclick():
    """Test hide button interaction."""
    pv_backend = PyVistaBackend()

    pl = Plotter(backend=pv_backend)

    # Create custom sphere
    custom_sphere = CustomObject()
    custom_sphere.mesh = pv.Sphere(center=(0, 0, 5))
    custom_sphere.name = "CustomSphere"
    mesh_object_sphere = MeshObjectPlot(custom_sphere, custom_sphere.get_mesh())

    pl.plot(mesh_object_sphere)

    # Run the plotter and simulate a click
    pl.show(auto_close=False)

    raw_plotter = pl.backend.scene
    width, height = raw_plotter.window_size

    raw_plotter.iren._mouse_left_button_click(10, 10)
    raw_plotter.iren._mouse_left_button_click(10, 10)

    raw_plotter.close()


def test_slicing_tool():
    """Test slicing tool interaction."""
    pv_backend = PyVistaBackend()

    pl = Plotter(backend=pv_backend)

    # Create custom sphere
    custom_sphere = CustomObject()
    custom_sphere.mesh = pv.Sphere(center=(0, 0, 5))
    custom_sphere.name = "CustomSphere"
    mesh_object_sphere = MeshObjectPlot(custom_sphere, custom_sphere.get_mesh())

    pl.plot(mesh_object_sphere)

    # Run the plotter and simulate a click
    pl.show(auto_close=False)

    raw_plotter = pl.backend.scene
    width, height = raw_plotter.window_size

    raw_plotter.iren._mouse_left_button_click(45, 60)
    raw_plotter.close()

def test_pick_rotation_center():
    """Test pick rotation center tool interaction."""
    pv_backend = PyVistaBackend()

    pl = Plotter(backend=pv_backend)

    # Create custom sphere
    custom_sphere = CustomObject()
    custom_sphere.mesh = pv.Sphere(center=(0, 0, 5))
    custom_sphere.name = "CustomSphere"
    mesh_object_sphere = MeshObjectPlot(custom_sphere, custom_sphere.get_mesh())

    pl.plot(mesh_object_sphere)

    # Run the plotter and simulate a click
    pl.show(auto_close=False)

    raw_plotter = pl.backend.scene
    width, height = raw_plotter.window_size

    raw_plotter.iren._mouse_left_button_click(45, 10)
    raw_plotter.iren._mouse_right_button_press(width//2, height//2)
    raw_plotter.iren._mouse_right_button_release(width//2, height//2)
    raw_plotter.close()