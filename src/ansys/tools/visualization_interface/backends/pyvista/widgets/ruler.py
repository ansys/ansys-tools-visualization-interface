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
"""Provides the ruler widget for the Visualization Interface Tool plotter."""

from pathlib import Path

from pyvista import Plotter

from ansys.tools.visualization_interface.backends.pyvista.widgets.widget import PlotterWidget


class Ruler(PlotterWidget):
    """Provides the ruler widget for the Visualization Interface Tool ``Plotter`` class.

    Parameters
    ----------
    plotter : ~pyvista.Plotter
        Provides the plotter to add the ruler widget to.
    dark_mode : bool, optional
        Whether to activate the dark mode or not.

    """

    def __init__(self, plotter: Plotter, dark_mode: bool = False) -> None:
        """Initialize the ``Ruler`` class."""
        from vtk import vtkActor, vtkButtonWidget
        # Call PlotterWidget ctor
        super().__init__(plotter)
        self._dark_mode = dark_mode
        # Initialize variables
        self._actor: vtkActor = None
        self._button: vtkButtonWidget = self.plotter.add_checkbox_button_widget(
            self.callback, position=(3, 88), size=30, border_size=3
        )
        self.update()

    def callback(self, state: bool) -> None:
        """Remove or add the ruler widget actor upon click.

        Parameters
        ----------
        state : bool
            Whether the state of the button, which is inherited from PyVista, is ``True``.

        Notes
        -----
        This method provides a callback function for the ruler widet.
        It is called every time the ruler widget is clicked.
        """
        if not state and self._actor:
            self.plotter.remove_actor(self._actor)
            self._actor = None
        else:
            self._actor = self.plotter.show_bounds(
                grid="front",
                location="outer",
                all_edges=False,
                show_xaxis=True,
                show_yaxis=True,
                show_zaxis=True,
                color="white" if self._dark_mode else "black",
                xtitle="X Axis [m]",
                ytitle="Y Axis [m]",
                ztitle="Z Axis [m]",
            )

    def update(self) -> None:
        """Define the configuration and representation of the ruler widget button."""
        from vtk import vtkPNGReader
        if self._dark_mode:
            is_inv = "_inv"
        else:
            is_inv = ""
        show_ruler_vr = self._button.GetRepresentation()
        show_ruler_icon_file = Path(Path(__file__).parent / "_images" / f"ruler{is_inv}.png")
        show_ruler_r = vtkPNGReader()
        show_ruler_r.SetFileName(show_ruler_icon_file)
        show_ruler_r.Update()
        image = show_ruler_r.GetOutput()
        show_ruler_vr.SetButtonTexture(0, image)
        show_ruler_vr.SetButtonTexture(1, image)
