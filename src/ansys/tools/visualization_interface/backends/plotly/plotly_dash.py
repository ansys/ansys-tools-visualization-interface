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
"""Module for dash plotly."""
from typing import TYPE_CHECKING, Union

from dash import Dash, Input, Output, dcc, html

from ansys.tools.visualization_interface.backends.plotly.plotly_interface import PlotlyBackend
from ansys.tools.visualization_interface.backends.plotly.widgets.dropdown_manager import DashDropdownManager

if TYPE_CHECKING:
    import plotly.graph_objects as go


class PlotlyDashBackend(PlotlyBackend):
    """Plotly Dash interface for visualization."""

    def __init__(self, app: Dash = None) -> None:
        """Initialize the Plotly Dash backend.

        Parameters
        ----------
        app : Dash
            The Dash application instance.
        """
        super().__init__()
        self._app = app or Dash(__name__)
        self._dropdown_manager = DashDropdownManager(self._fig)
        self._setup_callbacks()

    @property
    def dropdown_manager(self) -> DashDropdownManager:
        """Get the dropdown manager for this backend.

        Returns
        -------
        DashDropdownManager
            The dropdown manager instance.
        """
        return self._dropdown_manager

    def plot(self, plottable_object, name: str = None, **plotting_options) -> None:
        """Plot a single object using Plotly and track mesh names for dropdown.

        Parameters
        ----------
        plottable_object : Any
            The object to plot.
        name : str, optional
            Name of the mesh for labeling in Plotly.
        plotting_options : dict
            Additional plotting options.
        """
        # Call parent plot method
        super().plot(plottable_object, name=name, **plotting_options)

        # Track mesh names for dropdown functionality
        if name:
            self._dropdown_manager.add_mesh_name(name)
        else:
            # Try to get name from the latest trace added
            if self._fig.data:
                latest_trace = self._fig.data[-1]
                trace_name = getattr(latest_trace, 'name', None)
                if trace_name:
                    self._dropdown_manager.add_mesh_name(trace_name)

    def _setup_callbacks(self) -> None:
        """Setup Dash callbacks for mesh visibility control."""
        # Store reference to self for use in callback
        backend_instance = self

        @self._app.callback(
            Output('mesh-graph', 'figure'),
            Input('mesh-visibility-dropdown', 'value'),
            prevent_initial_call=True
        )
        def update_mesh_visibility(hidden_meshes):
            """Update mesh visibility based on dropdown selection.

            Parameters
            ----------
            hidden_meshes : List[str]
                List of mesh names to hide.

            Returns
            -------
            go.Figure
                Updated figure with modified mesh visibility.
            """
            if hidden_meshes is None:
                hidden_meshes = []

            # Get all mesh names
            all_mesh_names = backend_instance.dropdown_manager.get_mesh_names()
            visible_mesh_names = [name for name in all_mesh_names if name not in hidden_meshes]

            # Create a copy of the figure to avoid modifying the original
            import plotly.graph_objects as go
            updated_fig = go.Figure(backend_instance._fig)

            # Update visibility for each trace
            for i, trace in enumerate(updated_fig.data):
                trace_name = getattr(trace, 'name', None)
                is_visible = trace_name in visible_mesh_names
                updated_fig.data[i].visible = is_visible

            return updated_fig

    def create_dash_layout(self) -> html.Div:
        """Create the Dash layout with optional dropdown for mesh visibility.

        Returns
        -------
        html.Div
            The Dash layout component.
        """
        components = []

        if self.dropdown_manager.get_mesh_names():
            # Add dropdown for mesh visibility control
            mesh_names = self.dropdown_manager.get_mesh_names()
            components.append(
                    dcc.Dropdown(
                        id='mesh-visibility-dropdown',
                        options=[{'label': name, 'value': name} for name in mesh_names],
                        multi=True,
                        placeholder="Select meshes to hide",
                        searchable=True,
                        style={
                            'width': '280px',
                            'fontSize': '14px'
                        }
                    )

            )

        # Add the main graph
        components.append(dcc.Graph(
            id='mesh-graph',
            figure=self._fig,
            style={
                'height': '100vh',
                'width': '100%',
                'margin': '0',
                'padding': '0'
            },
            config={
                'responsive': True,
                'displayModeBar': True,
                'displaylogo': False
            }
        ))

        return html.Div(components, style={
            'fontFamily': '"Open Sans", verdana, arial, sans-serif',
            'backgroundColor': '#ffffff',
            'minHeight': '100vh',
            'width': '100%',
            'margin': '0',
            'padding': '0',
            'position': 'relative'
        })

    def show(self,
            plottable_object=None,
            screenshot: str = None,
            name_filter=None,
            **kwargs) -> Union["go.Figure", None]:
        """Render the Plotly scene.

        Parameters
        ----------
        plottable_object : Any, optional
            Object to show, by default None.
        screenshot : str, optional
            Path to save a screenshot, by default None.
        name_filter : bool, optional
            Flag to filter the object, by default None.
        kwargs : dict
            Additional options the selected backend accepts.

        Returns
        -------
        Union[go.Figure, None]
            The figure of the plot if in doc building environment. Else, None.
        """
        import os
        if os.environ.get("PYANSYS_VISUALIZER_DOC_MODE"):
            return self._fig

        if plottable_object is not None:
            self.plot(plottable_object)

        # Only show in browser if no screenshot is being taken
        if not screenshot:
            # Always use the create_dash_layout method to ensure dropdown is included when enabled
            self._app.layout = self.create_dash_layout()
            self._app.run()

        else:
            screenshot_str = str(screenshot)
            if screenshot_str.endswith('.html'):
                self._fig.write_html(screenshot_str)
            else:
                self._fig.write_image(screenshot_str)
