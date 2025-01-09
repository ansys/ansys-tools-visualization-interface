# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
"""Provides the measure widget for the PyAnsys plotter."""
from pathlib import Path
from typing import TYPE_CHECKING

import pyvista as pv
from vtk import vtkActor, vtkButtonWidget, vtkPNGReader

from ansys.tools.visualization_interface.backends.pyvista.widgets.widget import PlotterWidget

if TYPE_CHECKING:
    from ansys.tools.visualization_interface.backends.pyvista.pyvista import Plotter

class MeshSliderWidget(PlotterWidget):
    """Provides the mesh slider widget for the Visualization Interface Tool ``Plotter`` class.

    Parameters
    ----------
    plotter_helper : PlotterHelper
        Plotter to add the mesh slider widget to.

    """

    def __init__(self, plotter_helper: "Plotter") -> None:
        """Initialize the ``MeshSliderWidget`` class."""
        # Call PlotterWidget ctor
        super().__init__(plotter_helper._pl.scene)

        # Initialize variables
        self._widget_actor: vtkActor = None
        self.plotter_helper = plotter_helper
        self._button: vtkButtonWidget = self.plotter_helper._pl.scene.add_checkbox_button_widget(
            self.callback, position=(45, 60), size=30, border_size=3
        )
        self._mb = None
        self._mesh_actor_list = []
        self.update()

    @property
    def _meshes(self):
        """Return all the meshes which have dataset from the underlying plotter."""
        # This method is patching #208
        # until pyvista fix this upstream.
        actors = self.plotter_helper._pl.scene.actors.values()
        meshes = []
        for actor in actors:
            if hasattr(actor, 'mapper') and hasattr(actor.mapper, "dataset"):
                meshes.append(actor.mapper.dataset)
        return meshes

    def callback(self, state: bool) -> None:
        """Remove or add the mesh slider widget actor upon click.

        Parameters
        ----------
        state : bool
            Whether the state of the button, which is inherited from PyVista, is active.

        """
        if not state:
            self.plotter_helper._pl.scene.clear_actors()
            self.plotter_helper._pl.scene.clear_plane_widgets()
            for actor in self._mesh_actor_list:
                self.plotter_helper._pl.scene.add_actor(actor)
        else:
            self._mb = pv.MultiBlock(self.plotter_helper._pl.scene.meshes).combine()
            self._widget_actor = self.plotter_helper._pl.scene.add_mesh_clip_plane(
                self._mb, show_edges=self.plotter_helper._pl._show_edges
            )
            for mesh in self._meshes:
                if isinstance(mesh, pv.PolyData):
                    mesh_id = "PolyData(" + mesh.memory_address + ")"
                elif isinstance(mesh, pv.UnstructuredGrid):
                    mesh_id = "UnstructuredGrid(" + mesh.memory_address + ")"
                elif isinstance(mesh, pv.MultiBlock):
                    mesh_id = "MultiBlock(" + mesh.memory_address + ")"
                elif isinstance(mesh, pv.StructuredGrid):
                    mesh_id = "StructuredGrid(" + mesh.memory_address + ")"
                self._mesh_actor_list.append(self.plotter_helper._pl.scene.actors[mesh_id])
                self.plotter_helper._pl.scene.remove_actor(mesh_id)

    def update(self) -> None:
        """Define the mesh slider widget button parameters."""
        show_measure_vr = self._button.GetRepresentation()
        show_measure_icon_file = Path(
            Path(__file__).parent / "_images"/ "planecut.png"
        )
        show_measure_r = vtkPNGReader()
        show_measure_r.SetFileName(show_measure_icon_file)
        show_measure_r.Update()
        image = show_measure_r.GetOutput()
        show_measure_vr.SetButtonTexture(0, image)
        show_measure_vr.SetButtonTexture(1, image)
