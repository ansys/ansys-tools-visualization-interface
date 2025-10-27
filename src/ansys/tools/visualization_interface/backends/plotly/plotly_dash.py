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
"""Module for dash plotly."""
from typing import TYPE_CHECKING, Union

from dash import Dash, dcc, html

from ansys.tools.visualization_interface.backends.plotly.plotly_interface import PlotlyBackend

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
            self._app.layout = html.Div([
                dcc.Graph(figure=self._fig)
            ])
            self._app.run()

        else:
            screenshot_str = str(screenshot)
            if screenshot_str.endswith('.html'):
                self._fig.write_html(screenshot_str)
            else:
                self._fig.write_image(screenshot_str)
