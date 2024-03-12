.. _ref_user_guide:

==========
User guide
==========

This section explains key concepts for implementing PyAnsys Visualizer in your workflow.
You can use PyAnsys Visualizer in your examples as well as integrate this library into
your own code.

Default plotter usage
=====================

PyAnsys Visualizer provides a default plotter that can be used out of the box. This default
plotter provides common functionalities so that you do not need to create a custom plotter.

Use with PyVista meshes
-----------------------

You can use the default plotter to plot simple PyVista meshes. This code shows how to
use it to visualize a simple PyVista mesh:

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


Use with PyAnsys custom objects
-------------------------------

You can also use the default plotter to visualize PyAnsys custom objects. The only requirement is that the
custom object must have a method that returns a PyVista mesh, as well as a method that exposes a ``name`` or
``id`` attribute of your object. To expose custom object, you use a ``MeshObjectPlot`` instance. This class
relates PyVista meshes with any object.

The following code shows how to use the default plotter to visualize a PyAnsys custom object:

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


Customize your own plotter
==========================

The PyAnsys Visualizer provides a base class, ``PlotterInterface``, for customizing certain functions
of the plotter. This class provides a set of methods that can be overridden so that you can adapt the
plotter to the specific need of your library.

The first thing you must do is to create a new class that inherits from the ``PlotterInterface``
class. After that, you have two main options for customizing the plotter:

* The most common use case is to customize the way that the objects you represent are shown in the plotter.
  To this end, you can override the ``add`` and ``add_iter`` methods. These methods are called every time
  a new object is added to the plotter. The default implementation of this method is to add a PyVista mesh
  or a  ``MeshObjectPlot`` instance to the plotter. You can override this method to add your own meshes or
  objects to the plotter in a manner that fits the way that you want to represent the meshes.

* Another use case is the need to have custom button functionalities for your library. For example, you many
  want buttons for hiding or showing certain objects. To add custom buttons to the plotter, you use the
  implementable interface provided by the ``PlotterWidget`` class.

Some practical examples of how to use the ``PlotterInterface`` class are included in some PyAnsys libraries,
such as `PyAnsys Geometry <https://github.com/ansys/pyansys-geometry/pull/959>_`.
