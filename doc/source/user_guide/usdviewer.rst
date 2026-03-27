.. _ref_usd_viewer:

USD viewer usage
################

The Ansys Tools Visualization Interface provides a USD viewer that can be
used to visualize USD stages. The viewer is built on top of the python-usd-viewer package,
which provides a simple interface for visualizing USD stages.


USD viewer installation
-----------------------

To use the USD viewer, you need to install the python-usd-viewer package. Please refer
to the `USD viewer installation guide`_ for detailed instructions on how to install the package.

.. _USD viewer installation guide: https://github.com/ansys/python-usd-viewer

..


USD viewer usage
----------------

Once you have the USD viewer installed, you can use it to visualize USD stages.
The Ansys Tools Visualization Interface provides a `USDInterface` class that serves
as a bridge between the USD viewer and the Ansys Tools Visualization Interface plotter.

Here's a simple example of how to use the USD viewer through the Ansys Tools Visualization Interface:

.. code-block:: python

    from ansys.tools.visualization_interface import Plotter
    from ansys.tools.visualization_interface.usd_interface import USDInterface

    pl = Plotter(backend=USDInterface())

    mesh = pv.Sphere()

    pl.plot(mesh)

    pl.show()