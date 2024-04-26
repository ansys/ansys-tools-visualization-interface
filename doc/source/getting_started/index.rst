.. _ref_getting_started:

Getting started
###############

This section describes how to install PyAnsys Visualizer in user mode and
quickly begin using it. If you are interested in contributing to PyAnsys Visualizer,
see :ref:`contribute` for information on installing in developer mode.

Installation
============

To use `pip <https://pypi.org/project/pip/>`_ to install PyAnsys Visualizer,
run this command:

.. code:: bash

        pip install ansys-tools-visualization-interface

Alternatively, to install the latest version from this library's
`GitHub repository <https://github.com/ansys-internal/ansys-tools-visualization-interface/>`_,
run these commands:

.. code:: bash

    git clone https://github.com/ansys/ansys-tools-visualization-interface
    cd ansys-tools-visualization-interface
    pip install .

Quick start
^^^^^^^^^^^

The following examples show how to use PyAnsys Visualizer to visualize a mesh file.

This code uses only a PyVista mesh:

.. code:: python

    from ansys.tools.visualization_interface import Plotter

    my_mesh = my_custom_object.get_mesh()

    # Create a PyAnsys Visualizer object
    pl = Plotter()
    pl.plot(my_mesh)

    # Plot the result
    pl.show()

This code uses objects from a PyAnsys library:

.. code:: python

    from ansys.tools.visualization_interface import Plotter, MeshObjectPlot

    my_custom_object = MyObject()
    my_mesh = my_custom_object.get_mesh()

    mesh_object = MeshObjectPlot(my_custom_object, my_mesh)

    # Create a PyAnsys Visualizer object
    pl = Plotter()
    pl.plot(mesh_object)

    # Plot the result
    pl.show()
