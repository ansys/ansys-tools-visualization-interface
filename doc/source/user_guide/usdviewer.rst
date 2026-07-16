.. _ref_usd_viewer:

USD viewer usage
################

The Ansys Tools Visualization Interface provides a USD viewer that can be
used to visualize USD stages. The viewer is built on top of the ``python-usd-viewer`` package,
which provides a simple interface for visualizing USD stages.


USD viewer installation
-----------------------

To use the USD viewer, you need to install the ``python-usd-viewer`` package. Please refer
to the `USD viewer installation guide <https://usd-viewer.docs.pyansys.com/version/stable/getting_started/index.html>`_
for detailed instructions on how to install the package.


USD viewer usage
----------------

Once you have the USD viewer installed, you can use it to visualize USD stages.
The Ansys Tools Visualization Interface provides a `USDInterface` class that serves
as a bridge between the USD viewer and the Ansys Tools Visualization Interface plotter.

Here is a simple example of how to use the USD viewer through the Ansys Tools Visualization Interface:

.. code-block:: python

    from ansys.tools.visualization_interface import Plotter
    from ansys.tools.visualization_interface.usd_interface import USDInterface

    pl = Plotter(backend=USDInterface())

    mesh = pv.Sphere()

    pl.plot(mesh)

    pl.show()

USD to HTML export
------------------

To convert a USD file to a self-contained HTML viewer page (backed by Three.js),
use :func:`~ansys.tools.visualization_interface.export_usd_to_html`. The
generated file embeds all geometry as a base64-encoded GLB and requires only a
CDN connection to render.

.. code-block:: python

    from ansys.tools.visualization_interface import export_usd_to_html

    # From a file path
    html_path = export_usd_to_html("my_model.usd", "my_model_viewer.html")

    # From an in-memory pxr.Usd.Stage (no .usd file needed)
    from pxr import Gf, Usd, UsdGeom

    stage = Usd.Stage.CreateInMemory()
    mesh = UsdGeom.Mesh.Define(stage, "/Box")
    stage.SetDefaultPrim(mesh.GetPrim())
    mesh.GetPointsAttr().Set([Gf.Vec3f(0, 0, 0), Gf.Vec3f(1, 0, 0), Gf.Vec3f(0, 1, 0)])
    mesh.GetFaceVertexCountsAttr().Set([3])
    mesh.GetFaceVertexIndicesAttr().Set([0, 1, 2])

    html_path = export_usd_to_html(stage, "triangle_viewer.html")

The optional ``show_mesh_lines``, ``line_color``, and ``line_opacity`` parameters
control a wireframe edge overlay injected directly into the HTML:

.. code-block:: python

    html_path = export_usd_to_html(
        "my_model.usd",
        show_mesh_lines=True,
        line_color="#00ffcc",
        line_opacity=0.7,
    )

.. note::

    This feature requires the ``[usd]`` optional dependencies:
    ``pip install ansys-tools-visualization-interface[usd]``
