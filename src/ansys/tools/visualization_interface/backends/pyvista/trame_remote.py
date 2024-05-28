# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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
"""Module for trame websocket client functions."""
import pickle  # nosec B403

from beartype.typing import Union
import pyvista as pv
from websockets.sync.client import connect


def send_pl(plotter: pv.Plotter, host: str = "localhost", port: int = 8765):
    """Send the plotter meshes to a remote trame service.

    Since plotter can't be pickled, we send the meshes list instead.

    Parameters
    ----------
    plotter : pv.Plotter
        Plotter to send.
    host : str, optional
        Websocket host to connect to, by default "localhost".
    port : int, optional
        Websocket port to connect to, by default 8765.
    """
    with connect("ws://" + host + ":" + str(port)) as websocket:
        # Plotter can't be pickled, so we send the meshes list instead
        meshes_list_pk = pickle.dumps(plotter.meshes)  # nosec B403
        websocket.send(meshes_list_pk)

def send_mesh(mesh: Union[pv.PolyData, pv.MultiBlock], host: str = "localhost", port: int = 8765):
    """Send a mesh to a remote trame service.

    Parameters
    ----------
    mesh : Union[pv.PolyData, pv.MultiBlock]
        Mesh to send.
    host : str, optional
        Websocket host to connect to, by default "localhost".
    port : int, optional
        Websocket port to connect to, by default 8765.
    """
    with connect("ws://" + host + ":" + str(port)) as websocket:
        mesh_pk = pickle.dumps(mesh)  # nosec B403
        websocket.send(mesh_pk)
