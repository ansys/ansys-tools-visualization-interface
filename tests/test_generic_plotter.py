import pytest
import pyvista as pv

from ansys.visualizer import ClipPlane, MeshObjectPlot, Plotter


class CustomTestClass():
    """Mock custom class for testing MeshObjectPlot."""
    def __init__(self, name) -> None:
        self.name = name

def test_plotter_add_pd():
    """Adds polydata to the plotter."""
    pl = Plotter()
    sphere = pv.Sphere()
    pl.add(sphere)
    pl.plot()

def test_plotter_add_mb():
    """Adds multiblock to the plotter."""
    pl = Plotter()
    sphere = pv.Sphere()
    mb = pv.MultiBlock()
    mb.append(sphere)
    pl.add(mb)
    pl.plot()

def test_plotter_add_custom():
    """Adds a MeshObjectPlot object to the plotter."""
    sphere = pv.Sphere()
    custom = MeshObjectPlot(CustomTestClass("myname"), sphere)
    pl = Plotter()
    pl.add(custom)
    pl.plot()

def test_plotter_filter():
    """Test regex filter usage."""
    sphere = pv.Sphere(center=(1, 4, 0))
    cube = pv.Cube(center=(-1, 0, 3))
    custom_sphere = MeshObjectPlot(CustomTestClass("sphere"), sphere)
    custom_cube = MeshObjectPlot(CustomTestClass("cube"), cube)

    pl = Plotter()
    pl.add([custom_sphere, custom_cube], filter="cube")
    pl.plot()

def test_clipping_plane():
    """Test clipping plane usage."""
    sphere = pv.Sphere()
    pl = Plotter()
    clipping_plane = ClipPlane()
    pl.add(sphere, clipping_plane=clipping_plane)
    pl.plot()

def test_plotter_add_list():
    """Adds a list to the plotter."""
    pl = Plotter()
    sphere = pv.Sphere(center=(1, 4, 0))
    cube = pv.Cube(center=(-1, 0, 3))
    polydata_list = [sphere, cube]
    pl.add(polydata_list)
    pl.plot()
    


