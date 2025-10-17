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
"""Module for button management."""
from typing import Any, List

import plotly.graph_objects as go


class ButtonManager:
    """Class to manage buttons in a Plotly figure.

    This class allows adding buttons to a Plotly figure for various functionalities
    such as toggling visibility of traces, resetting the view, and custom actions.

    Parameters
    ----------
    fig : go.Figure
        The Plotly figure to which buttons will be added.
    """

    def __init__(self, fig: go.Figure):
        """Initialize ButtonManager."""
        self._fig = fig
        self._buttons = []

    def add_button(self,
                    label: str,
                    x: float,
                    y: float,
                    xanchor: str = "left",
                    yanchor: str = "bottom",
                    method: str = "restyle",
                    args: List[Any] = None,
                    args2: List[Any] = None,
            ) -> None:
            """Add a button to the Plotly figure.

            Parameters
            ----------
            label : str
                The text to display on the button.
            x : float
                X position of the button (0-1).
            y : float
                Y position of the button (0-1).
            xanchor : str, optional
                X anchor point for the button, by default "left".
            yanchor : str, optional
                Y anchor point for the button, by default "bottom".
            method : str, optional
                The method to call when the button is clicked. Options include:
                'restyle', 'relayout', 'update', 'animate', by default 'restyle'.
            args : List[Any], optional
                Arguments to pass to the method when the button is clicked, by default None.
            args2 : List[Any], optional
                Secondary arguments for toggle functionality, by default None.

            """
            if args is None:
                args = [{}]

            button_config = {
                "label": label,
                "method": method,
                "args": args
            }

            if args2 is not None:
                button_config["args2"] = args2

            self._buttons.append({
                "button": button_config,
                "x": x,
                "y": y,
                "xanchor": xanchor,
                "yanchor": yanchor
            })

            self._update_buttons()

    def show_hide_bbox_dict(self, toggle: bool = True):
        """Generate dictionary for showing/hiding coordinate system elements.

        Parameters
        ----------
        toggle : bool, optional
            Whether to show (True) or hide (False) the coordinate system, by default True.

        Returns
        -------
        dict
            Dictionary with coordinate system visibility settings.
        """
        return {
            "scene.xaxis.showgrid": toggle,
            "scene.xaxis.showline": toggle,
            "scene.xaxis.zeroline": toggle,
            "scene.xaxis.showticklabels": toggle,
            "scene.xaxis.title": "X" if toggle else "",
            "scene.xaxis.visible": toggle,
            "scene.xaxis.showbackground": toggle,
            "scene.yaxis.showgrid": toggle,
            "scene.yaxis.showline": toggle,
            "scene.yaxis.zeroline": toggle,
            "scene.yaxis.showticklabels": toggle,
            "scene.yaxis.title": "Y" if toggle else "",
            "scene.yaxis.visible": toggle,
            "scene.yaxis.showbackground": toggle,
            "scene.zaxis.showgrid": toggle,
            "scene.zaxis.showline": toggle,
            "scene.zaxis.zeroline": toggle,
            "scene.zaxis.showticklabels": toggle,
            "scene.zaxis.title": "Z" if toggle else "",
            "scene.zaxis.visible": toggle,
            "scene.zaxis.showbackground": toggle
        }

    def add_coordinate_system_toggle_button(
            self,
            label: str = "Toggle Axes",
            x: float = 0.08,
            y: float = 1.02
        ) -> None:
        """Add a button to toggle the coordinate system (axes, grid, labels) on/off.

        Parameters
        ----------
        label : str, optional
            The text to display on the button, by default "Toggle Axes".
        x : float, optional
            X position of the button (0-1), by default 0.08.
        y : float, optional
            Y position of the button (0-1), by default 1.02.
        """
        self.add_button(
            label=label,
            method="relayout",
            args=[self.show_hide_bbox_dict(True)],
            args2=[self.show_hide_bbox_dict(False)],
            x=x,
            y=y
        )

    def add_dropdown_menu(
            self,
            options: List[dict],
            x: float = 0.02,
            y: float = 1.02,
            xanchor: str = "left",
            yanchor: str = "bottom"
        ) -> None:
        """Add a dropdown menu to the Plotly figure.

        Parameters
        ----------
        options : List[dict]
            List of dropdown options, each containing 'label', 'method', and 'args'.
        x : float, optional
            X position of the dropdown (0-1), by default 0.02.
        y : float, optional
            Y position of the dropdown (0-1), by default 1.02.
        xanchor : str, optional
            X anchor point for the dropdown, by default "left".
        yanchor : str, optional
            Y anchor point for the dropdown, by default "bottom".
        """
        dropdown_config = {
            "type": "dropdown",
            "buttons": options,
            "x": x,
            "y": y,
            "xanchor": xanchor,
            "yanchor": yanchor,
            "showactive": True,
            "direction": "down",
            "bgcolor": "rgba(255,255,255,0.95)",
            "bordercolor": "rgba(0,0,0,0.3)",
            "borderwidth": 1,
            "font": {"size": 12},
            "pad": {"t": 5, "b": 5, "l": 10, "r": 10}
        }

        self._buttons.append({
            "button": dropdown_config,
            "x": x,
            "y": y,
            "xanchor": xanchor,
            "yanchor": yanchor
        })

        self._update_dropdowns()

    def _update_dropdowns(self) -> None:
        """Update the figure layout with all dropdowns and buttons."""
        if not self._buttons:
            return

        # Create updatemenus for the layout
        updatemenus = []

        for button_info in self._buttons:
            if button_info["button"].get("type") == "dropdown":
                # This is a dropdown menu
                updatemenu = button_info["button"]
            else:
                # This is a regular button - create individual updatemenu for each
                updatemenu = {
                    "type": "buttons",
                    "buttons": [button_info["button"]],
                    "x": button_info["x"],
                    "y": button_info["y"],
                    "xanchor": button_info["xanchor"],
                    "yanchor": button_info["yanchor"],
                    "showactive": False,
                    "direction": "left",
                    "bgcolor": "rgba(255,255,255,0.95)",
                    "bordercolor": "rgba(0,0,0,0.3)",
                    "borderwidth": 1,
                    "font": {"size": 12},
                    "pad": {"t": 5, "b": 5, "l": 10, "r": 10}
                }
            updatemenus.append(updatemenu)

        self._fig.update_layout(updatemenus=updatemenus)

    def add_plane_view_buttons(
            self,
            xy_label: str = "XY View",
            xz_label: str = "XZ View",
            yz_label: str = "YZ View",
            iso_label: str = "ISO View",
            x: float = 0.02,
            y: float = 1.02,
        ) -> None:
        """Add a dropdown menu for standard plane views (XY, XZ, YZ) and isometric view.

        Parameters
        ----------
        xy_label : str, optional
            Label for XY plane view button, by default "XY View".
        xz_label : str, optional
            Label for XZ plane view button, by default "XZ View".
        yz_label : str, optional
            Label for YZ plane view button, by default "YZ View".
        iso_label : str, optional
            Label for isometric view button, by default "ISO View".
        x : float, optional
            X position for the dropdown, by default 0.02.
        y : float, optional
            Y position for the dropdown, by default 1.02.
        spacing : float, optional
            Not used in dropdown mode, kept for compatibility.
        """
        view_options = [
            {
                "label": xy_label,
                "method": "relayout",
                "args": [{
                    "scene.camera.eye": {"x": 0, "y": 0, "z": 2.5},
                    "scene.camera.center": {"x": 0, "y": 0, "z": 0},
                    "scene.camera.up": {"x": 0, "y": 1, "z": 0}
                }]
            },
            {
                "label": xz_label,
                "method": "relayout",
                "args": [{
                    "scene.camera.eye": {"x": 0, "y": -2.5, "z": 0},
                    "scene.camera.center": {"x": 0, "y": 0, "z": 0},
                    "scene.camera.up": {"x": 0, "y": 0, "z": 1}
                }]
            },
            {
                "label": yz_label,
                "method": "relayout",
                "args": [{
                    "scene.camera.eye": {"x": 2.5, "y": 0, "z": 0},
                    "scene.camera.center": {"x": 0, "y": 0, "z": 0},
                    "scene.camera.up": {"x": 0, "y": 0, "z": 1}
                }]
            },
            {
                "label": iso_label,
                "method": "relayout",
                "args": [{
                    "scene.camera.eye": {"x": 1.25, "y": 1.25, "z": 1.25},
                    "scene.camera.center": {"x": 0, "y": 0, "z": 0},
                    "scene.camera.up": {"x": 0, "y": 0, "z": 1}
                }]
            }
        ]

        self.add_dropdown_menu(view_options, x=x, y=y)

    def _update_buttons(self) -> None:
        """Update the figure layout with all buttons."""
        self._update_dropdowns()

    def add_measurement_toggle_button(
            self,
            label: str = "Toggle Measurement",
            x: float = 0.02,
            y: float = 0.87
        ) -> None:
        """Add a button to toggle the measurement widget on/off.

        Parameters
        ----------
        label : str, optional
            The text to display on the button, by default "Toggle Measurement".
        x : float, optional
            X position of the button (0-1), by default 0.02.
        y : float, optional
            Y position of the button (0-1), by default 0.87.
        """
        # Enable measurement tools in modebar
        enable_measurement = {
            "modebar": {
                "add": ["drawline", "drawopenpath", "drawclosedpath", "drawcircle", "drawrect", "eraseshape"],
                "remove": []
            }
        }

        # Disable measurement tools in modebar
        disable_measurement = {
            "modebar": {
                "add": [],
                "remove": ["drawline", "drawopenpath", "drawclosedpath", "drawcircle", "drawrect", "eraseshape"]
            }
        }

        self.add_button(
            label=label,
            method="relayout",
            args=[enable_measurement],
            args2=[disable_measurement],
            x=x,
            y=y
        )

    def add_projection_toggle_button(
            self,
            label: str = "Toggle Projection",
            x: float = 0.14,
            y: float = 1.02
        ) -> None:
        """Add a button to toggle between perspective and orthographic projection.

        Parameters
        ----------
        label : str, optional
            The text to display on the button, by default "Toggle Projection".
        x : float, optional
            X position of the button (0-1), by default 0.14.
        y : float, optional
            Y position of the button (0-1), by default 1.02.
        """
        # Set to orthographic projection
        orthographic_projection = {
            "scene.camera.projection.type": "orthographic"
        }

        # Set to perspective projection (default)
        perspective_projection = {
            "scene.camera.projection.type": "perspective"
        }

        self.add_button(
            label=label,
            method="relayout",
            args=[perspective_projection],
            args2=[orthographic_projection],
            x=x,
            y=y
        )

    def add_theme_toggle_button(
            self,
            label: str = "Toggle Theme",
            x: float = 0.2175,
            y: float = 1.02
        ) -> None:
        """Add a button to toggle between light and dark themes.

        Parameters
        ----------
        label : str, optional
            The text to display on the button, by default "Toggle Theme".
        x : float, optional
            X position of the button (0-1), by default 0.22.
        y : float, optional
            Y position of the button (0-1), by default 1.02.
        """
        # Define light theme properties manually to avoid JSON serialization issues
        # Use dot notation to target specific properties without overriding the entire scene
        # Colors extracted from official plotly template
        light_theme = {
            "paper_bgcolor": "white",
            "plot_bgcolor": "#E5ECF6",
            "font.color": "#2a3f5f",
            "scene.xaxis.backgroundcolor": "#E5ECF6",
            "scene.xaxis.gridcolor": "white",
            "scene.xaxis.linecolor": "white",
            "scene.xaxis.zerolinecolor": "white",
            "scene.yaxis.backgroundcolor": "#E5ECF6",
            "scene.yaxis.gridcolor": "white",
            "scene.yaxis.linecolor": "white",
            "scene.yaxis.zerolinecolor": "white",
            "scene.zaxis.backgroundcolor": "#E5ECF6",
            "scene.zaxis.gridcolor": "white",
            "scene.zaxis.linecolor": "white",
            "scene.zaxis.zerolinecolor": "white"
        }

        # Define dark theme properties manually
        # Colors extracted from official plotly_dark template
        dark_theme = {
            "paper_bgcolor": "rgb(17,17,17)",
            "plot_bgcolor": "rgb(17,17,17)",
            "font.color": "#f2f5fa",
            "scene.xaxis.backgroundcolor": "rgb(17,17,17)",
            "scene.xaxis.gridcolor": "#506784",
            "scene.xaxis.linecolor": "#506784",
            "scene.xaxis.zerolinecolor": "#C8D4E3",
            "scene.yaxis.backgroundcolor": "rgb(17,17,17)",
            "scene.yaxis.gridcolor": "#506784",
            "scene.yaxis.linecolor": "#506784",
            "scene.yaxis.zerolinecolor": "#C8D4E3",
            "scene.zaxis.backgroundcolor": "rgb(17,17,17)",
            "scene.zaxis.gridcolor": "#506784",
            "scene.zaxis.linecolor": "#506784",
            "scene.zaxis.zerolinecolor": "#C8D4E3"
        }

        # Add styling updates for all existing updatemenus + the theme button we're about to add
        # Get the actual number of updatemenus in the figure
        current_updatemenus = self._fig.layout.updatemenus or []
        # Add 1 to include the theme button we're about to create
        for i in range(len(current_updatemenus) + 1):
            light_theme[f"updatemenus[{i}].bgcolor"] = "rgba(255,255,255,0.95)"
            light_theme[f"updatemenus[{i}].bordercolor"] = "rgba(0,0,0,0.3)"
            light_theme[f"updatemenus[{i}].font.color"] = "black"

            dark_theme[f"updatemenus[{i}].bgcolor"] = "rgba(50,50,50,0.95)"
            dark_theme[f"updatemenus[{i}].bordercolor"] = "rgba(255,255,255,0.3)"
            dark_theme[f"updatemenus[{i}].font.color"] = "grey"

        self.add_button(
            label=label,
            method="relayout",
            args=[light_theme],
            args2=[dark_theme],
            x=x,
            y=y
        )