# Copyright (C) 2024 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""Trame service module."""
import asyncio

# Pickle vulnerabilities are ignored, since we require to use pickle to send and receive data
# from the websocket. This is a trusted source, so we can ignore this vulnerability.
# Potentially, someone could send a malicious pickle object and execute arbitrary code.
import pickle  # nosec B403

import pyvista as pv
from pyvista.trame.ui import plotter_ui
from trame.app import get_server
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import vuetify3
from websockets import WebSocketServerProtocol
from websockets.server import serve


class TrameService:
    """Trame service class.

    Initializes a trame service where you can send meshes to plot in a trame webview plotter.

    Parameters
    ----------
    websocket_host : str, optional
        Host where the webserver will listen for new plotters and meshes, by default "localhost".
    websocket_port : int, optional
        Port where the webserver will listen for new plotters and meshes, by default 8765.
    """
    def __init__(self, websocket_host: str = "localhost", websocket_port: int=8765):
        """Initialize the trame service."""
        pv.OFF_SCREEN = True

        self._server = get_server()
        self._state, self._ctrl = self._server.state, self._server.controller
        self._websocket_port = websocket_port
        self._websocket_host = websocket_host
        # pyvista plotter, we treat it as a view i.e. created once but updated as we see fit.
        self._pl = pv.Plotter()

    def clear_plotter(self):
        """Clears the web view in the service."""
        self._pl.clear_actors()
        self._pl.reset_camera()


    async def _listener(self, websocket: WebSocketServerProtocol):
        """Listens for new meshes and plotters.

        Infinite loop where we wait for new messages from the client.
        If we get a list of meshes, we assume it's a scene and clear the previous meshes.

        Parameters
        ----------
        websocket : websockets.WebSocketServerProtocol
            Websocket where to listen.
        """
        async for message in websocket:
            obj = pickle.loads(message) # nosec B301

            if isinstance(obj, list):
                # if we get a list of meshes, assume it's a scene and clear previous meshes
                self.clear_plotter()
                for mesh in obj:
                    self._pl.add_mesh(mesh)
                    print(mesh)
            else:
                print(obj)
                self._pl.add_mesh(obj)
                self._pl.reset_camera()

    async def _webserver(self):
        """Starts the webserver for the trame service listener."""
        async with serve(self._listener, self._websocket_host, self._websocket_port):
            await asyncio.Future()  # run forever

    def set_scene(self):
        """Sets the web view scene for the trame service."""
        with SinglePageLayout(self._server) as layout:
            with layout.toolbar:
                with vuetify3.VBtn(icon=True, click=self.clear_plotter):
                    vuetify3.VIcon("mdi-trash-can")
                with vuetify3.VBtn(icon=True, click=self._ctrl.reset_camera):
                    vuetify3.VIcon("mdi-crop-free")

            # main view container
            with layout.content:
                with vuetify3.VContainer(
                    fluid=True, classes="pa-0 fill-height", style="position: relative;"
                ):
                    view = plotter_ui(self._pl)
                    # bind plotter methods to the controller method, this way we can
                    # attach UI elements on it. see buttons above
                    self._ctrl.view_update = view.update
                    self._ctrl.reset_camera = view.reset_camera


    async def _launch_trame_service(self):
        """Launches the trame service."""
        self.set_scene()
        trame_coroutine = self._server.start(exec_mode="coroutine")
        webserver_coroutine = asyncio.create_task(self._webserver())
        await asyncio.gather(trame_coroutine, webserver_coroutine)

    def run(self):
        """Start the trame web view and the websocket services."""
        asyncio.run(self._launch_trame_service())
