.. _ref_user_guide:

==========
User guide
==========

This section provides a user guide for the PyAnsys Visualizer, explaining how to use the software in your examples,
as well as how to integrate the library into your own code.

PyAnsys Visualizer overview
============================

The PyAnsys Visualizer is a Python library that provides a simple user interface to visualize ANSYS data. The library
acts as an interface between PyAnsys libraries and other plotting libraries. Currently, only PyVista is supported.
The main features of this library are:

* Provides out of the box viewing, measurement and picking functionalities.
* An extensible class to add custom functionalities.
* An interface between PyAnsys and plotting libraries.



Default plotter usage
=====================

The PyAnsys Visualizer provides a default plotter that can be used out of the box. This provides the common
functionalities of the plotter without the need to create a custom plotter.

Usage with PyVista meshes
-------------------------

You can seize the plotter even when only plotting simple PyVista meshes. The following example shows how to use the
default plotter to visualize a simple PyVista mesh.

.. code:: python

    ## Usage example with pyvista meshes ##

    import pyvista as pv
    from ansys.visualizer import Plotter

    # Create a pyvista mesh
    mesh = pv.Cube()

    # Create a plotter
    pl = Plotter()

    # Add the mesh to the plotter
    pl.add(mesh)

    # Show the plotter
    pl.plot()


Usage with PyAnsys custom objects
---------------------------------

Another use case of the default plotter is to visualize PyAnsys custom objects. The only requirement is that the
custom object must have a method that returns a PyVista mesh, as well as a method that exposes a `name` or `id` attribute
of your object. To expose custom object, a `MeshObjectPlot` instance is used. This class relates PyVista meshes with
any object.

The following example shows how to use the default plotter to visualize a PyAnsys custom object.

.. code:: python

    ## Usage example with PyAnsys custom objects ##

    from ansys.visualizer import Plotter
    from ansys.visualizer import MeshObjectPlot


    # Create a custom object for this example
    class CustomObject:
        def __init__(self):
            self.name = "CustomObject"
            self.mesh = pv.Cube()

        def get_mesh(self):
            return self.mesh

        def name(self):
            return self.name


    custom_object = CustomObject()

    # Create a MeshObjectPlot instance
    mesh_object = MeshObjectPlot(custom_object, custom_object.get_mesh())

    # Create a plotter
    pl = Plotter()

    # Add the MeshObjectPlot instance to the plotter
    pl.add(mesh_object)

    # Show the plotter
    pl.plot()


Customizing your own plotter
============================
The PyAnsys Visualizer provides a base class to customize certain functions of the plotter. This class is called ``PlotterInterface``. This class
provides a set of methods that can be overridden so you can adapt the plotter to the specific need of your library.

To this end, the first thing you need to do is to create a new class that inherits from the ``PlotterInterface`` class. After that, you have two
main options to customize the plotter:

* | The most common need that you may have is to customize the way the objects you represent are shown in the plotter. To this end, you can override the
  | ``add`` and ``add_iter`` methods. These methods are called every time a new object is added to the plotter. The default implementation of this method is to add a PyVista mesh or a
  | ``MeshObjectPlot`` instance to the plotter. You can override this method to add your own meshes or objects to the plotter in a manner that fits the way you want to represent the meshes.

* | Another use case is the need of having custom button functionalities for your library, to, for example, hide or show certain objects. You can make use of the ``PlotterWidget`` class to
  | add custom buttons to the plotter. This class provides an implementable interface where you can add your own buttons to the plotter.


Some practical examples of how to use the ``PlotterInterface`` class are included in some PyAnsys libraries, such as `PyAnsys Geometry <https://github.com/ansys/pyansys-geometry/pull/959>_`.
