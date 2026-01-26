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
"""Provides the toggle subtree visibility widget for the Visualization Interface Tool plotter."""

from pathlib import Path

from pyvista import Plotter

from ansys.tools.visualization_interface.backends.pyvista.widgets.widget import PlotterWidget


class ToggleSubtreeButton(PlotterWidget):
    """Toggle visibility of picked object's entire subtree.

    This widget provides a button that toggles the visibility of the currently
    picked object and all its children in the tree hierarchy. When activated,
    if the object is visible, it and all descendants are hidden. If hidden,
    they are all shown.

    Parameters
    ----------
    plotter : ~pyvista.Plotter
        Provides the plotter to add the toggle subtree widget to.
    dark_mode : bool, optional
        Whether to activate the dark mode or not.
    include_root : bool, optional
        Whether to toggle the root object itself or just its children.
        Default is True.

    Examples
    --------
    Create a plotter with picking and add the toggle subtree button:

    >>> from ansys.tools.visualization_interface import Plotter
    >>> from ansys.tools.visualization_interface.backends.pyvista import PyVistaBackend
    >>> backend = PyVistaBackend(allow_picking=True)
    >>> pl = Plotter(backend=backend)
    >>> pl.plot(assembly, plot_children=True)
    >>> pl.show()

    """

    def __init__(self, plotter: Plotter, dark_mode: bool = False, include_root: bool = True) -> None:
        """Initialize the ``ToggleSubtreeButton`` class."""
        from vtk import vtkActor, vtkButtonWidget

        # Call PlotterWidget ctor
        super().__init__(plotter)
        self._dark_mode = dark_mode
        self._include_root = include_root

        # Track objects that have been hidden by this widget
        self._hidden_objects = []

        # Initialize variables
        self._actor: vtkActor = None
        self._button: vtkButtonWidget = self.plotter._pl.scene.add_checkbox_button_widget(
            self.callback, position=(300, 130), size=30, border_size=3
        )
        self.update()

    def callback(self, state: bool) -> None:
        """Toggle subtree visibility for all picked objects.

        Parameters
        ----------
        state : bool
            Whether the state of the button, which is inherited from PyVista, is ``True``.

        Notes
        -----
        This method provides a callback function for the toggle subtree widget.
        It is called every time the widget button is clicked. It toggles the
        visibility of all currently picked objects and their entire subtrees.

        When hiding trees, all picked objects are automatically unpicked after hiding.
        When showing previously hidden trees, they are simply shown without unpicking.

        """
        # If we have hidden objects, show them all regardless of what's picked
        if self._hidden_objects:
            for obj in self._hidden_objects:
                self.plotter._pl.toggle_subtree_visibility(obj, include_root=self._include_root)
            self._hidden_objects.clear()
            self.plotter._pl.scene.render()
            return

        # Otherwise, hide all currently picked objects
        if not self.plotter._custom_picker._picked_dict:
            print("No objects picked. Pick an object first to toggle its subtree visibility.")
            return

        # Store all picked objects and hide them
        objects_to_hide = list(self.plotter._custom_picker._picked_dict.values())
        for element in objects_to_hide:
            self.plotter._pl.toggle_subtree_visibility(element, include_root=self._include_root)
            self._hidden_objects.append(element)

        # Unpick all objects after hiding their trees
        for obj in objects_to_hide:
            self.plotter._custom_picker.pick_unselect_object(obj, restore_visibility=False)

        # Force render to update the scene
        self.plotter._pl.scene.render()

    def update(self) -> None:
        """Define the configuration and representation of the toggle subtree button."""
        from vtk import vtkPNGReader

        if self._dark_mode:
            is_inv = "_inv"
        else:
            is_inv = ""

        show_vr = self._button.GetRepresentation()
        # Use eye icon for visibility toggle
        show_icon_file = Path(Path(__file__).parent / "_images" / f"visibilityoff{is_inv}.png")
        show_r = vtkPNGReader()
        show_r.SetFileName(show_icon_file)
        show_r.Update()
        image = show_r.GetOutput()
        show_vr.SetButtonTexture(0, image)
        show_vr.SetButtonTexture(1, image)
