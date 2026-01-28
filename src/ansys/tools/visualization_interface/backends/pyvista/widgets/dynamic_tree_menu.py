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
"""Provides a dynamic tree menu widget with clickable buttons."""

from typing import Dict, List

from pyvista import Plotter

from ansys.tools.visualization_interface.backends.pyvista.widgets.widget import PlotterWidget
from ansys.tools.visualization_interface.types.mesh_object_plot import MeshObjectPlot


class DynamicTreeMenuWidget(PlotterWidget):
    """Provides a dynamic tree menu with clickable buttons for each object.

    This widget displays a hierarchical tree view of all plotted objects on the right
    side of the screen. Each object has a clickable checkbox button to toggle visibility.

    Parameters
    ----------
    plotter : ~pyvista.Plotter
        The plotter to add the tree menu widget to.
    position : tuple, optional
        The (x, y) position of the top-left corner of the menu. Default is (0.65, 0.95).
    button_size : int, optional
        Size of the checkbox buttons in pixels. Default is 20.
    spacing : int, optional
        Vertical spacing between items in pixels. Default is 30.
    font_size : int, optional
        Font size for the object labels. Default is 12.
    dark_mode : bool, optional
        Whether to use dark mode colors. Default is False.
        In light mode (False): text is black
        In dark mode (True): text is white

    Notes
    -----
    Each object gets a checkbox button that toggles visibility of the object and its subtree.
    The menu updates dynamically as objects are added or removed.

    """

    def __init__(
        self,
        plotter: Plotter,
        position: tuple = (0.82, 0.95),
        button_size: int = 20,
        spacing: int = 30,
        font_size: int = 6,
        dark_mode: bool = False
    ) -> None:
        """Initialize the DynamicTreeMenuWidget."""
        super().__init__(plotter)
        self._start_position = position
        self._button_size = button_size
        self._spacing = spacing
        self._font_size = font_size
        self._dark_mode = dark_mode
        self._buttons = []  # List of button widgets
        self._button = None  # Compatibility with other widgets (HideButton checks this)
        self._text_actors = []  # List of text actors
        self._button_to_object: Dict = {}  # Maps button to object
        self._tree_objects: List[MeshObjectPlot] = []  # Root objects
        self._menu_visible = True  # Track menu visibility state (starts True, will be hidden below)

        # Build initial menu
        self._rebuild_menu()

        # Hide menu by default
        self.hide_menu()

    def _collect_root_objects(self) -> List[MeshObjectPlot]:
        """Collect all root objects (objects without parents) from the plotter."""
        root_objects = []

        # Get all objects from the PyVistaInterface's object map
        object_map = None
        if hasattr(self.plotter, '_pl') and self.plotter._pl is not None:
            if hasattr(self.plotter._pl, '_object_to_actors_map'):
                object_map = self.plotter._pl._object_to_actors_map

        if object_map:
            # The map has actors as keys, objects as values
            for actor, obj in object_map.items():
                if isinstance(obj, MeshObjectPlot):
                    # Check if this object is a root (no parent or parent not in map)
                    is_root = obj._parent is None
                    if not is_root:
                        # Check if parent is also in the map
                        parent_found = any(v == obj._parent for v in object_map.values())
                        is_root = not parent_found

                    if is_root:
                        root_objects.append(obj)

        return root_objects

    def _make_toggle_callback(self, obj: MeshObjectPlot):
        """Create a callback for toggling object visibility."""
        def callback(state: bool):
            # Toggle visibility of object and its subtree
            has_pl = hasattr(self.plotter, '_pl')
            has_method = has_pl and hasattr(self.plotter._pl, 'toggle_subtree_visibility')
            if has_method:
                # Don't use the state parameter - just toggle current visibility
                self.plotter._pl.toggle_subtree_visibility(obj, include_root=True)
                self.plotter._pl.scene.render()
        return callback

    def _add_menu_item(
        self,
        obj: MeshObjectPlot,
        y_position: float,
        indent: int = 0
    ) -> float:
        """Add a menu item (button + label) for an object.

        Parameters
        ----------
        obj : MeshObjectPlot
            The object to add a menu item for.
        y_position : float
            The current y position in pixels.
        indent : int
            The indentation level (0 = root, 1 = child, etc.)

        Returns
        -------
        float
            The updated y position after adding this item.
        """
        from pathlib import Path

        from vtk import vtkPNGReader

        # Calculate positions
        button_x = self._start_position[0] * self.plotter._pl.scene.window_size[0]
        indent_offset = indent * 20  # 20 pixels per indent level
        button_x += indent_offset

        # Create button with PNG icon instead of checkbox
        callback = self._make_toggle_callback(obj)
        button = self.plotter._pl.scene.add_checkbox_button_widget(
            callback,
            value=obj.visible,
            position=(button_x, y_position),
            size=self._button_size,
            border_size=0  # No border to avoid square outline
        )

        # Apply PNG icon to replace checkbox appearance
        button_repr = button.GetRepresentation()
        is_inv = "_inv" if self._dark_mode else ""

        # Use visibility on/off icons
        icon_on_file = Path(Path(__file__).parent / "_images" / f"visibilityon{is_inv}.png")
        icon_off_file = Path(Path(__file__).parent / "_images" / f"visibilityoff{is_inv}.png")

        # Load "on" state icon
        reader_on = vtkPNGReader()
        reader_on.SetFileName(str(icon_on_file))
        reader_on.Update()
        image_on = reader_on.GetOutput()

        # Load "off" state icon
        reader_off = vtkPNGReader()
        reader_off.SetFileName(str(icon_off_file))
        reader_off.Update()
        image_off = reader_off.GetOutput()

        # Set textures: index 0 = off state, index 1 = on state
        button_repr.SetButtonTexture(0, image_off)
        button_repr.SetButtonTexture(1, image_on)

        self._buttons.append(button)
        self._button_to_object[id(button)] = obj

        # Add text label next to button (use pixel positioning to match button)
        label_x = button_x + self._button_size + 10
        label_y = y_position

        # Set text color based on theme
        text_color = 'white' if self._dark_mode else 'black'

        text_actor = self.plotter._pl.scene.add_text(
            obj.name,
            position=(label_x, label_y),
            font_size=self._font_size,
            color=text_color,
            viewport=False  # Use pixel positioning to match buttons
        )
        self._text_actors.append(text_actor)

        return y_position - self._spacing

    def _add_object_and_children(
        self,
        obj: MeshObjectPlot,
        y_position: float,
        indent: int = 0
    ) -> float:
        """Recursively add object and its children to the menu.

        Parameters
        ----------
        obj : MeshObjectPlot
            The object to add.
        y_position : float
            The current y position.
        indent : int
            The indentation level.

        Returns
        -------
        float
            The updated y position.
        """
        # Add this object
        y_position = self._add_menu_item(obj, y_position, indent)

        # Add children
        if obj._children:
            for child in obj._children:
                y_position = self._add_object_and_children(child, y_position, indent + 1)

        return y_position

    def _rebuild_menu(self):
        """Rebuild the entire menu."""
        # Remove existing buttons individually (don't use clear_button_widgets!)
        for button in self._buttons:
            try:
                button.Off()
                button.SetEnabled(False)
            except Exception:  # noqa: S110
                pass

        for actor in self._text_actors:
            try:
                self.plotter._pl.scene.remove_actor(actor)
            except Exception:  # noqa: S110
                pass

        self._buttons.clear()
        self._text_actors.clear()
        self._button_to_object.clear()

        # Collect root objects
        self._tree_objects = self._collect_root_objects()

        # Calculate starting position in pixels
        window_width = self.plotter._pl.scene.window_size[0]
        window_height = self.plotter._pl.scene.window_size[1]
        y_position = self._start_position[1] * window_height

        # Add title (use pixel positioning)
        title_x = self._start_position[0] * window_width
        title_y = y_position

        # Set colors based on theme
        title_color = 'cyan' if self._dark_mode else 'blue'

        title_actor = self.plotter._pl.scene.add_text(
            "=== Visibility Menu ===",
            position=(title_x, title_y),
            font_size=self._font_size + 2,
            color=title_color,
            viewport=False  # Use pixel positioning to match buttons
        )
        self._text_actors.append(title_actor)

        y_position -= self._spacing * 1.5  # Space after title

        # Add all objects
        for root in self._tree_objects:
            y_position = self._add_object_and_children(root, y_position, indent=0)

        if len(self._tree_objects) == 0:
            # No objects message (use pixel positioning)
            no_obj_x = self._start_position[0] * window_width
            no_obj_y = title_y - (self._spacing * 2)
            no_obj_actor = self.plotter._pl.scene.add_text(
                "(No objects)",
                position=(no_obj_x, no_obj_y),
                font_size=self._font_size,
                color='gray',
                viewport=False  # Use pixel positioning to match buttons
            )
            self._text_actors.append(no_obj_actor)

    def refresh(self):
        """Refresh the menu display."""
        self._rebuild_menu()

    def update(self):
        """Update the widget's appearance for current dark mode setting."""
        # If menu hasn't been built yet, skip
        if not self._buttons:
            return

        # Update button textures for all existing buttons
        from pathlib import Path

        from vtk import vtkPNGReader

        is_inv = "_inv" if self._dark_mode else ""

        # Update each button's textures
        for button in self._buttons:
            button_repr = button.GetRepresentation()

            # Load new textures
            icon_on_file = Path(Path(__file__).parent / "_images" / f"visibilityon{is_inv}.png")
            icon_off_file = Path(Path(__file__).parent / "_images" / f"visibilityoff{is_inv}.png")

            reader_on = vtkPNGReader()
            reader_on.SetFileName(str(icon_on_file))
            reader_on.Update()

            reader_off = vtkPNGReader()
            reader_off.SetFileName(str(icon_off_file))
            reader_off.Update()

            button_repr.SetButtonTexture(1, reader_on.GetOutput())
            button_repr.SetButtonTexture(0, reader_off.GetOutput())

        # Update text colors
        text_color = 'white' if self._dark_mode else 'black'
        title_color = 'cyan' if self._dark_mode else 'blue'

        for i, actor in enumerate(self._text_actors):
            if i == 0:  # Title
                actor.GetTextProperty().SetColor(
                    1.0 if title_color == 'cyan' else 0.0,
                    1.0 if title_color == 'cyan' else 0.0,
                    1.0
                )
            else:  # Regular text
                color_val = 1.0 if text_color == 'white' else 0.0
                actor.GetTextProperty().SetColor(color_val, color_val, color_val)

    def show_menu(self):
        """Show the menu by enabling all text actors and buttons."""
        for actor in self._text_actors:
            actor.SetVisibility(1)

        for button in self._buttons:
            # Match exactly what hide_buttons.py does - just On() and SetVisibility(1)
            button.On()
            button.GetRepresentation().SetVisibility(1)

        self._menu_visible = True
        self._plotter._pl.scene.render()

    def hide_menu(self):
        """Hide the menu by disabling all text actors and buttons."""
        for actor in self._text_actors:
            actor.SetVisibility(0)

        for button in self._buttons:
            # Match exactly what hide_buttons.py does - just Off() and SetVisibility(0)
            button.Off()
            button.GetRepresentation().SetVisibility(0)

        self._menu_visible = False

        self._plotter._pl.scene.render()

    def callback(self, state: bool) -> None:
        """Placeholder callback (not used for this widget)."""
        pass
