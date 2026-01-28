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
"""Provides a button to toggle the tree menu visibility."""

from vtk import vtkButtonWidget

from ansys.tools.visualization_interface.backends.pyvista.widgets.widget import PlotterWidget


class TreeMenuToggleButton(PlotterWidget):
    """Provides a button to show/hide the tree menu widget.

    This button toggles the visibility of the dynamic tree menu panel.

    Parameters
    ----------
    plotter : Plotter
        Plotter to draw the button on.
    dark_mode : bool, optional
        Whether to activate dark mode. Default is False.
    tree_menu : DynamicTreeMenuWidget, optional
        The tree menu widget to toggle. If None, will search for it in plotter widgets.

    """

    def __init__(self, plotter, dark_mode: bool = False, tree_menu=None) -> None:
        """Initialize the TreeMenuToggleButton."""
        super().__init__(plotter._pl.scene)
        self._plotter = plotter  # Store the backend
        self._dark_mode = dark_mode
        self._tree_menu = tree_menu
        self._menu_visible = True  # Menu starts visible

        # Create the checkbox button
        self._button: vtkButtonWidget = self._plotter._pl.scene.add_checkbox_button_widget(
            self.callback,
            value=True,  # Start checked (menu visible)
            position=(101, 130),  # Next to screenshot button at (69, 130)
            size=30,
            border_size=3
        )
        self.update()

    def update(self) -> None:
        """Assign the image that represents the button."""
        from pathlib import Path

        from vtk import vtkPNGReader

        if self._dark_mode:
            is_inv = "_inv"
        else:
            is_inv = ""

        button_repr = self._button.GetRepresentation()
        button_icon_path = Path(
            Path(__file__).parent / "_images", f"visibilityon{is_inv}.png"
        )
        button_icon = vtkPNGReader()
        button_icon.SetFileName(button_icon_path)
        button_icon.Update()
        image = button_icon.GetOutput()
        button_repr.SetButtonTexture(0, image)
        button_repr.SetButtonTexture(1, image)

    def callback(self, state: bool) -> None:
        """Toggle the tree menu visibility.

        Parameters
        ----------
        state : bool
            The state of the button (True = show menu, False = hide menu).

        """
        # Find the tree menu if not provided
        if self._tree_menu is None:
            from ansys.tools.visualization_interface.backends.pyvista.widgets.dynamic_tree_menu import (
                DynamicTreeMenuWidget,
            )
            if hasattr(self._plotter, '_widgets'):
                for widget in self._plotter._widgets:
                    if isinstance(widget, DynamicTreeMenuWidget):
                        self._tree_menu = widget
                        break

        if self._tree_menu is None:
            return

        # Toggle visibility based on button state
        if state:
            # Show menu
            self._tree_menu.show_menu()
        else:
            # Hide menu
            self._tree_menu.hide_menu()

        # Re-render the scene
        self._plotter._pl.scene.render()
