.. _ref_usd_viewer:

USD viewer usage
################

The Ansys Tools Visualization Interface provides a USD viewer that can be
used to visualize USD stages. The viewer is built on top of the ``python-usd-viewer`` package,
which provides a simple interface for visualizing USD stages.


USD viewer installation (live viewer)
-------------------------------------

The USD viewer provides an interactive 3D viewer for visualizing USD stages in real-time.

To use the live USD viewer, you need to install the optional dependencies with:

.. code-block:: bash

    pip install 'ansys-tools-visualization-interface[usd-live-viewer]'

This installs the ``python-usd-viewer`` package along with required dependencies.
For additional details, please refer to the
`USD viewer installation guide <https://usd-viewer.docs.pyansys.com/version/stable/getting_started/index.html>`_.


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
use :func:`~ansys.tools.visualization_interface.export_usd_to_html`.

The export pipeline works as follows:

1. The USD stage is traversed and its mesh primitives are converted to
   `GLB <https://www.khronos.org/gltf/>`_ format. GLB (GL Transmission Format
   Binary) is the binary container of the glTF standard—a compact, web-native
   3D format understood natively by Three.js without any additional plugins.
   It encodes mesh geometry (vertices, normals, indices), materials, and scene
   hierarchy in a single binary blob.
2. The GLB binary is base64-encoded so it can be stored as a plain string inside
   the HTML file, making the output completely self-contained—no separate model
   file is needed alongside the HTML.
3. The viewer decodes the string with the browser's built-in ``atob()`` function
   and passes the resulting binary buffer to ``GLTFLoader``, which renders it
   with WebGL.

The generated file requires only a CDN connection (for Three.js) to open in any
modern browser.

To use this feature, install the optional dependencies with:

.. code-block:: bash

    pip install 'ansys-tools-visualization-interface[usd]'

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

Time slider and color legend
----------------------------

:func:`~ansys.tools.visualization_interface.add_viewer_controls` adds a
Play/Pause button, a time slider, and a color legend to an HTML page that you
have already created with
:func:`~ansys.tools.visualization_interface.export_usd_to_html`.

Calling ``add_viewer_controls`` is optional. If you only call
``export_usd_to_html``, the page shows the model without a slider or a legend.

The time slider changes the mesh colors from one frame to the next, for
example to show a temperature field over solver iterations. The mesh shape is
the same in every frame.

.. warning::

    ``add_viewer_controls``, ``Legend``, and ``Frames`` are experimental and
    may change in a future release.

.. code-block:: python

    import numpy as np
    from ansys.tools.visualization_interface import add_viewer_controls, export_usd_to_html
    from ansys.tools.visualization_interface.backends.usd import Frames, Legend

    html_path = export_usd_to_html("my_model.usd", "my_model_viewer.html")
    add_viewer_controls(
        html_path,
        colormap,  # (256, 3) sRGB floats in [0, 1]
        legend=Legend(vmin=300.0, vmax=400.0, title="Temperature [K]"),
        frames=Frames(indices, times=[0, 10, 20], label="Iteration"),
    )

The arguments are:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Argument
     - Content
   * - ``colormap``
     - Array of shape ``(256, 3)`` with sRGB colors in [0, 1]. A ``(256, 4)``
       RGBA array is also accepted and alpha is ignored, so
       ``matplotlib.colormaps["coolwarm"](np.linspace(0, 1, 256))`` works.
   * - ``legend``
     - Optional
       :class:`~ansys.tools.visualization_interface.backends.usd.viewer_controls.Legend`.
       Shows the colormap with its title and value range in the top-right
       corner.
   * - ``frames``
     - Optional
       :class:`~ansys.tools.visualization_interface.backends.usd.viewer_controls.Frames`.
       ``indices`` is an integer array of shape ``(n_frames, n_vertices)``
       with values in [0, 255], each one a row of ``colormap``. ``times``
       holds one value per frame and is shown next to ``label`` (default
       ``"Time"``). ``fps`` sets the playback speed (default 20).

Give a legend, frames, or both. ``Legend`` and ``Frames`` check their values
when you create them, for example that ``vmin`` is smaller than ``vmax`` and
that there is one time per frame.

The exported GLB has one vertex per triangle corner. For a triangle mesh, GLB
vertex ``k`` matches USD point ``faceVertexIndices[k]``, so reorder per-point
values with ``values[:, face_indices]`` before passing them to ``Frames``.

``add_viewer_controls`` checks its arguments before changing the file, and
calling it twice has the same effect as calling it once. See
:ref:`ref_usd_to_html_time_slider` for a complete example.

Custom HTML templates
---------------------

By default :func:`~ansys.tools.visualization_interface.export_usd_to_html` uses the
built-in ``glb_template.html`` viewer. Pass ``template_path`` to supply your own HTML
file instead—for example to match a house style or embed the viewer inside a larger
page.

Template variables
~~~~~~~~~~~~~~~~~~

Two placeholders are **always required**.  They are replaced with
JSON-encoded values at render time so that special characters are
escaped automatically.

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Placeholder
     - Replaced with
   * - ``__MODEL_NAME_JSON__``
     - A JSON string containing the source filename, for example ``"my_model.usd"``.
       Use it wherever you want to display the model name.
   * - ``__GLB_B64_JSON__``
     - A JSON string containing the base64-encoded GLB binary.
       GLB is the binary form of the glTF standard: it packs all mesh
       geometry (vertices, normals, indices), materials, and scene hierarchy
       into a single blob, which Three.js can parse directly with
       ``GLTFLoader``. Base64 encoding lets the binary data travel inside
       a plain HTML file without corruption. In JavaScript, assign it to a
       variable, decode it with ``atob()``, copy the result into a
       ``Uint8Array``, and pass the buffer to ``GLTFLoader.parse()``.

When ``show_mesh_lines=True``, or when you call
:func:`~ansys.tools.visualization_interface.add_viewer_controls` on the page,
two additional **anchor strings** must appear verbatim in the template. Code is
inserted around them by exact text match:

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Anchor string
     - What gets injected
   * - ``const binary = atob(glbBase64);``
     - Inserted immediately **before** this line: the edge-segment
       ``Float32Array`` and color/opacity constants for the wireframe, and the
       data for the viewer controls.
   * - ``scene.add(gltf.scene);``
     - Inserted immediately **after** this line: the ``THREE.LineSegments``
       wireframe object, and the code that builds the legend and frame player.


Using a custom template
~~~~~~~~~~~~~~~~~~~~~~~

Pass the path to your template file via the ``template_path`` parameter:

.. code-block:: python

    from ansys.tools.visualization_interface import export_usd_to_html

    html_path = export_usd_to_html(
        "my_model.usd",
        "my_model_viewer.html",
        template_path="my_custom_template.html",
    )

To use a custom template **with** the wireframe overlay, the template must
contain both anchor strings listed in the preceding table:

.. code-block:: python

    html_path = export_usd_to_html(
        "my_model.usd",
        "my_model_viewer.html",
        template_path="my_custom_template.html",
        show_mesh_lines=True,
        line_color="#00ffcc",
        line_opacity=0.7,
    )

Validation errors
~~~~~~~~~~~~~~~~~

:func:`~ansys.tools.visualization_interface.export_usd_to_html` validates
templates before writing any output, and
:func:`~ansys.tools.visualization_interface.add_viewer_controls` checks the
page for the anchors. A :class:`ValueError` is raised listing every missing
placeholder or anchor so you can fix all problems in one pass:

.. code-block:: text

    ValueError: Template is missing required placeholders: ['__GLB_B64_JSON__']

    ValueError: Template is missing required placeholders:
        ['const binary = atob(glbBase64);', 'scene.add(gltf.scene);']
