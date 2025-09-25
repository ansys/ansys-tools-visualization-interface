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
"""Provides the measure widget for the PyAnsys plotter."""
from pathlib import Path
from typing import TYPE_CHECKING

from vtk import vtkActor, vtkButtonWidget, vtkPNGReader

from ansys.tools.visualization_interface.backends.pyvista.widgets.widget import PlotterWidget

if TYPE_CHECKING:
    from ansys.tools.visualization_interface.backends.pyvista.pyvista import Plotter


class PickRotCenterButton(PlotterWidget):
    """Provides the pick rotation center widget for the Visualization Interface Tool ``Plotter`` class.

    Parameters
    ----------
    plotter_helper : PlotterHelper
        Plotter to add the pick rotation center widget to.
    dark_mode : bool, optional
        Whether to activate the dark mode or not.

    """

    def __init__(self, plotter_helper: "Plotter", dark_mode: bool = False) -> None:
        """Initialize the ``PickRotCenterWidget`` class."""
        # Call PlotterWidget ctor
        super().__init__(plotter_helper._pl.scene)
        self._dark_mode = dark_mode
        # Initialize variables
        self._actor: vtkActor = None
        self.plotter_helper = plotter_helper
        self._button: vtkButtonWidget = self.plotter_helper._pl.scene.add_checkbox_button_widget(
            self.callback, position=(45, 10), size=30, border_size=3
        )
        self.update()

    def callback(self, state: bool) -> None:
        """Remove or add the pick rotation center widget actor upon click.

        Parameters
        ----------
        state : bool
            Whether the state of the button, which is inherited from PyVista, is active.

        """
        # This implementation uses direct calls to VTK due to limitations
        # in PyVista. If there are improvements in the compatibility between
        # the PyVista picker and the pick rotation center widget, this should be reviewed.

        # Lazy import to avoid circular import
        if not state:
            self._text_actor.SetVisibility(0)
            self.plotter_helper.disable_center_focus()
            if self.plotter_helper._allow_picking:
                self.plotter_helper.enable_picking()
            elif self.plotter_helper._allow_hovering:
                self.plotter_helper.enable_hover()
        else:
            if self.plotter_helper._allow_picking:
                self.plotter_helper.disable_picking()
            elif self.plotter_helper._allow_hovering:
                self.plotter_helper.disable_hover()
            self.plotter_helper.enable_set_focus_center()
            self._text_actor = self.plotter_helper.scene.add_text(
                "Select a point to set the rotation center with right click",
                position="upper_edge",   # options: 'upper_edge', 'lower_edge', 'left_edge', etc.
                font_size=14,
                color="grey",
                shadow=True
            )


    def update(self) -> None:
        """Define the measurement widget button parameters."""
        if self._dark_mode:
            is_inv = "_inv"
        else:
            is_inv = ""
        show_measure_vr = self._button.GetRepresentation()
        show_measure_icon_file = Path(
            Path(__file__).parent / "_images" / f"center_pick{is_inv}.png"
        )
        show_measure_r = vtkPNGReader()
        show_measure_r.SetFileName(show_measure_icon_file)
        show_measure_r.Update()
        image = show_measure_r.GetOutput()
        show_measure_vr.SetButtonTexture(0, image)
        show_measure_vr.SetButtonTexture(1, image)
