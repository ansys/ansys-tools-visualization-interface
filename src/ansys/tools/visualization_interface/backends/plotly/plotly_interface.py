"""Plotly backend interface for visualization."""
from ansys.tools.visualization_interface.backends._base import BaseBackend
from ansys.tools.visualization_interface.types.mesh_object_plot import MeshObjectPlot
import plotly.graph_objects as go
from pyvista import PolyData
from typing import Union, Iterable, Any


class PlotlyBackend(BaseBackend):
    """Plotly interface for visualization."""

    def __init__(self, **kwargs):
        self._fig = go.Figure()

    def _pv_to_mesh3d(self, pv_mesh: PolyData) -> go.Mesh3d:
        """Convert a PyVista PolyData mesh to Plotly Mesh3d format."""
        points = pv_mesh.points
        x, y, z = points[:, 0], points[:, 1], points[:, 2]
        
        # Convert mesh to triangular mesh if needed, since Plotly only supports triangular faces
        triangulated_mesh = pv_mesh.triangulate()
        
        # Extract triangular faces
        faces = triangulated_mesh.faces.reshape((-1, 4))  # Now we know all faces are triangular (3 vertices + count)
        i, j, k = faces[:, 1], faces[:, 2], faces[:, 3]
        
        return go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k)
    @property
    def layout(self) -> Any:
        """Get the current layout of the Plotly figure."""
        return self._fig.layout

    @layout.setter
    def layout(self, new_layout: Any):
        """Set a new layout for the Plotly figure."""
        self._fig.update_layout(new_layout)

    def plot_iter(self, plotting_list):
        """Plot multiple objects using Plotly."""
        for item in plotting_list:
            self.plot(item)
        
    
    def plot(self, plottable_object: Union[PolyData, MeshObjectPlot, go.Mesh3d], **plotting_options):
        """Plot a single object using Plotly."""
        if isinstance(plottable_object, PolyData):
            mesh = self._pv_to_mesh3d(plottable_object)
            self._fig.add_trace(mesh)
        elif isinstance(plottable_object, MeshObjectPlot):
            pv_mesh = plottable_object.mesh
            mesh = self._pv_to_mesh3d(pv_mesh)
            self._fig.add_trace(mesh)
        elif isinstance(plottable_object, go.Mesh3d):
            self._fig.add_trace(plottable_object)
        else:
            try:
                self._fig.add_trace(plottable_object)
            except Exception:
                raise TypeError("Unsupported plottable_object type for PlotlyInterface.")

    def show(self, 
            plottable_object=None,
            screenshot: str = None,
            name_filter=None,
            **kwargs):
        """Render the Plotly scene."""
        if plottable_object is not None:
            self.plot(plottable_object)
        
        # Only show in browser if no screenshot is being taken
        if not screenshot:
            self._fig.show(**kwargs)
        
        if screenshot:
            screenshot_str = str(screenshot)
            if screenshot_str.endswith('.html'):
                self._fig.write_html(screenshot_str)
            else:
                self._fig.write_image(screenshot_str)
