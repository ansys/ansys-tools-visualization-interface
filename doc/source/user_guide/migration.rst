.. _ref_migration_guide:

Migration
#########

In this section two guides are provided to help you migrate from PyVista plotters to the Ansys Tools Visualization Interface plotters.
The first one addresses code migration, and the second one addresses documentation migration.

Code migration guide
====================

This guide intends to help users transition from PyVista plotters to the new Ansys Tools Visualization Interface plotters. Since cases are very different
from each other, a few examples are provided to cover the most common scenarios.

From simple PyVista mesh plotting to the Ansys visualization interface plotter
------------------------------------------------------------------------------
If you only need to plot simple PyVista meshes, you can directly replace your PyVista plotter code with the Ansys Tools Visualization Interface plotter code.
On top of common PyVista functionalities, the Ansys Tools Visualization Interface plotter provides additional interactivity such as view buttons, mesh slicing, etc.
Here is an example of how to do this:

- PyVista code:

.. code-block:: python

    import pyvista as pv

    # Create a pyvista mesh
    mesh = pv.Cube()

    # Create a plotter
    pl = pv.Plotter()

    # Add the mesh to the plotter
    pl.add_mesh(mesh)

    # Show the plotter
    pl.show()

- Ansys Tools Visualization Interface code:

.. code-block:: python

    import pyvista as pv
    from ansys.tools.visualization_interface import Plotter

    # Create a pyvista mesh
    mesh = pv.Cube()

    # Create a plotter
    pl = Plotter()

    # Add the mesh to the plotter
    pl.plot(mesh)

    # Show the plotter
    pl.show()


Convert your custom meshes to MeshObjectPlot and use the Ansys visualization interface plotter
----------------------------------------------------------------------------------------------

Your custom object must have a method that returns a PyVista mesh and a method that exposes a ``name`` or ``id`` attribute of your object.

.. code-block:: python

    class CustomObject:
        def __init__(self):
            self.name = "CustomObject"
            self.mesh = pv.Cube(center=(1, 1, 0))

        def get_mesh(self):
            return self.mesh

        def name(self):
            return self.name


Then you need to create a ``MeshObjectPlot`` instance that relates the PyVista mesh with your custom object.

.. code-block:: python

    from ansys.tools.visualization_interface import MeshObjectPlot

    custom_object = CustomObject()
    mesh_object_plot = MeshObjectPlot(
        custom_object=custom_object,
        mesh=custom_object.get_mesh(),
    )

With this, you can use the Ansys Tools Visualization Interface plotter to visualize your custom object. It will enable interactivity such as picking and hovering.


Customizing the PyVista backend
-------------------------------

You can customize the backend of the Ansys Tools Visualization Interface plotter to enable or disable certain functionalities. For example,
if you want to enable picking, you can do it as follows:

.. code-block:: python

    from ansys.tools.visualization_interface import Plotter
    from ansys.tools.visualization_interface.backends import PyVistaBackend

    backend = PyVistaBackend(allow_picking=True)

    # Create a plotter
    pl = Plotter(backend=backend)

    # Add the MeshObjectPlot instance to the plotter
    pl.plot(mesh_object_plot)

    # Show the plotter
    pl.show()

If you want to go further and customize the backend even more, you can create your own backend by inheriting from the ``PyVistaBackendInterface`` class
and implementing the required methods. You can find more information about this in the backend documentation:

.. code-block:: python

    @abstractmethod
    def plot_iter(self, plottable_object: Any, name_filter: str = None, **plotting_options):
        """Plot one or more compatible objects to the plotter.

        Parameters
        ----------
        plottable_object : Any
            One or more objects to add.
        name_filter : str, default: None.
            Regular expression with the desired name or names  to include in the plotter.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.

        """
        pass


    @abstractmethod
    def plot(self, plottable_object: Any, name_filter: str = None, **plotting_options):
        """Plot a single object to the plotter.

        Parameters
        ----------
        plottable_object : Any
            Object to add.
        name_filter : str
            Regular expression with the desired name or names to include in the plotter.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.

        """
        pass


The rest of the methods are implemented for you. This ensures that while you can customize what you need for plotting, the rest of the functionalities will work as expected.
If you need to even go further, you can also create your own plotter by inheriting from the ``BaseBackend`` class and implementing the required methods,
although this may break existing functionality. You can find more information about this in the plotter documentation.

Customize the picker or hover behavior
--------------------------------------
You can customize the picker of the Ansys Tools Visualization Interface plotter to decide what happens when an object is picked or hovered.
For example, if you want to print the name of the picked object, you can do it as described in the custom picker example.

Using PyVista Qt backend
------------------------
You can use the PyVista Qt backend with the Ansys Tools Visualization Interface plotter. To do this, you need to set the PyVista backend to Qt
before creating the plotter. Here is an example of how to do this:

.. code-block:: python

   cube = pv.Cube()
   pv_backend = PyVistaBackend(use_qt=True, show_qt=True)
   pl = Plotter(backend=pv_backend)
   pl.plot(cube)
   pl.backend.enable_widgets()
   pv_backend.scene.show()

With this, you can integrate the plotter into a PyQt or PySide application by disabling ``show_qt`` parameter.
You can find more information about this in the `PyVista documentation <https://qtdocs.pyvista.org/>`_.


Documentation migration guide
=============================

This guide is intended to help users transition from PyVista documentation configuration to the new Ansys Tools Visualization Interface documentation configuration.

1. Add environment variables for documentation:

.. code-block:: python

    os.environ["PYANSYS_VISUALIZER_DOC_MODE"] = "true"
    os.environ["PYANSYS_VISUALIZER_HTML_BACKEND"] = "true"

2. Use PyVista DynamicScraper:

.. code-block:: python

    from pyvista.plotting.utilities.sphinx_gallery import DynamicScraper

    sphinx_gallery_conf = {
        "image_scrapers": (DynamicScraper()),
    }

3. Add PyVista viewer directive to extensions:

.. code-block:: python

    extensions = ["pyvista.ext.viewer_directive"]

4. Make sure you are executing the notebook cells:

.. code-block:: python

    nbsphinx_execute = "always"