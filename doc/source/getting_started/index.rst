.. _ref_getting_started:

Getting started
###############

This section will guide you through the process of installing this project and its basic usage.

Installation
============

You can use `pip <https://pypi.org/project/pip/>`_ to install PyAnsys Visualizer.

.. code:: bash

        pip install pyansys-visualizer

Also, you can install it from source code:

.. code:: bash

    git clone https://github.com/ansys/pyansys-visualizer
    cd pyansys-visualizer
    pip install .


Quick start
===========
The following example shows how to use PyAnsys Visualizer to visualize a mesh file.

Using PyVista only:


.. code:: python

    from ansys.visualizer import Plotter
    import pyvista as pv

    my_mesh = pv.Sphere()

    # Create a PyAnsys Visualizer object
    pl = Plotter()
    pl.add(my_mesh)

    # Plot the result
    pl.plot()

Using custom objects from your library:

.. code:: python

    from ansys.visualizer import Plotter, MeshObjectPlot

    my_custom_object = MyObject()
    my_mesh = my_custom_object.get_mesh()

    meshobject = MeshObjectPlot(my_custom_object, my_mesh)

    # Create a PyAnsys Visualizer object
    pl = Plotter()
    pl.add(meshobject)

    # Plot the result
    pl.plot()