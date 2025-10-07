.. _ref_migration_guide:

Migration
#########

This section helps you migrate from PyVista plotters to the Ansys Tools Visualization Interface plotters.
It consists of two major topics:

- `Code migration`_
- `Documentation configuration migration`_

Code migration
==============
This topic explains how to migrate from PyVista plotters to the new Ansys Tools Visualization Interface plotters. Because cases vary greatly, it provides a few examples that cover the most common scenarios.

Replace PyVista plotter code with Ansys Tools Visualization Interface plotter code
----------------------------------------------------------------------------------
If you only need to plot simple PyVista meshes, you can directly replace your PyVista plotter code with the Ansys Tools Visualization Interface plotter code.
On top of common PyVista functionalities, the Ansys Tools Visualization Interface plotter provides additional interactivity such as view buttons and mesh slicing.

The following code shows how to do the plotter code replacement:

- PyVista code:

.. code-block:: python

    import pyvista as pv

    # Create a PyVista mesh
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

    # Create a PyVista mesh
    mesh = pv.Cube()

    # Create a plotter
    pl = Plotter()

    # Add the mesh to the plotter
    pl.plot(mesh)

    # Show the plotter
    pl.show()


Convert your custom meshes to objects usable by the Ansys Tools Visualization Interface plotter
-----------------------------------------------------------------------------------------------

Your custom object must have a method that returns a PyVista mesh and a method that exposes a ``name`` or ``id`` attribute of your object:

.. code-block:: python

    class CustomObject:
        def __init__(self):
            self.name = "CustomObject"
            self.mesh = pv.Cube(center=(1, 1, 0))

        def get_mesh(self):
            return self.mesh

        def name(self):
            return self.name


You then need to create a :class:`~ansys.tools.visualization_interface.types.mesh_object_plot.MeshObjectPlot` instance that relates the PyVista mesh with your custom object:

.. code-block:: python

    from ansys.tools.visualization_interface import MeshObjectPlot

    custom_object = CustomObject()
    mesh_object_plot = MeshObjectPlot(
        custom_object=custom_object,
        mesh=custom_object.get_mesh(),
    )

With this, you can use the Ansys Tools Visualization Interface plotter to visualize your custom object. It enables interactivity such as picking and hovering.


Customize the PyVista backend
-----------------------------

You can customize the backend of the Ansys Tools Visualization Interface plotter to enable or turn off certain functionalities. The following code shows how to enable picking:

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

If you want to customize the backend even more, you can create your own backend by inheriting from the :class:`~ansys.tools.visualization_interface.backends.pyvista.PyVistaBackendInterface` class
and implementing the required methods:

.. code-block:: python

    @abstractmethod
    def plot_iter(self, plottable_object: Any, name_filter: str = None, **plotting_options):
        """Plot one or more compatible objects to the plotter.

        Parameters
        ----------
        plottable_object : Any
            One or more objects plot.
        name_filter : str, default: None.
            Regular expression with the desired name or names to include in the plotter.
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
            Object to plot.
        name_filter : str
            Regular expression with the desired name or names to include in the plotter.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.

        """
        pass


The rest of the methods are implemented for you. This ensures that while you can customize what you need for plotting, 
the rest of the functionalities still work as expected. For more information, see the backend documentation. If you 
need to even go further, you can create your own plotter by inheriting from the :class:`~ansys.tools.visualization_interface.backends._base.BaseBackend` class and implementing the required methods,
although this may break existing features.

Customize the picker or hover behavior
--------------------------------------
You can customize the picker of the Ansys Tools Visualization Interface plotter to decide what happens when you pick or hover over an object.
For example, if you want to print the name of the picked object, you can do it as described in the :ref:`sphx_glr_examples_00-basic-pyvista-examples_custom_picker.py` example.

Use the PyVista Qt backend
--------------------------
You can use the PyVista Qt backend with the Ansys Tools Visualization Interface plotter. To do this, you must set the PyVista backend to Qt
before creating the plotter:

.. code-block:: python

   cube = pv.Cube()
   pv_backend = PyVistaBackend(use_qt=True, show_qt=True)
   pl = Plotter(backend=pv_backend)
   pl.plot(cube)
   pl.backend.enable_widgets()
   pv_backend.scene.show()

You can then integrate the plotter into a PyQt or PySide app by disabling the ``show_qt`` parameter.
For more information about this, see the `PyVista documentation <https://qtdocs.pyvista.org/>`_.


Documentation configuration migration
=====================================

This topic explains how to migrate from the PyVista documentation configuration to the new Ansys Tools Visualization Interface documentation configuration.

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