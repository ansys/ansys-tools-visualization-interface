# Copyright (C) 2024 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
.. _ref_remote_trame_view:

=============================
Use trame as a remote service
=============================

This example shows how to launch a trame service and use it as a remote service.

First, we need to launch the trame service. We can do this by running the following code::

    # import required libraries
    from ansys.tools.visualization_interface.backends.pyvista.trame_service import (
        TrameService,
    )

    # create a trame service, in whatever port is available in your system
    ts = TrameService(websocket_port=8765)

    # run the service
    ts.run()


Now, we can send meshes and plotter to the trame service. We can do this by running the following code in a separate terminal::

    # import required libraries
    import time

    import pyvista as pv

    from ansys.tools.visualization_interface.backends.pyvista.trame_remote import (
        send_mesh,
        send_pl,
    )

    # create an example plotter
    plotter = pv.Plotter()
    plotter.add_mesh(pv.Cube())

    # send some example meshes
    send_mesh(pv.Sphere())
    send_mesh(pv.Sphere(center=(3, 0, 0)))
    time.sleep(4)

    # if we send a plotter, the previous meshes will be deleted.
    send_pl(plotter)

"""