"""Plotly backend interface for visualization."""
from ansys.tools.visualization_interface.backends._base import BaseBackend
from ansys.tools.visualization_interface.types.mesh_object_plot import MeshObjectPlot
import plotly.graph_objects as go
from pyvista import PolyData
from typing import Union, Iterable, Any


class PlotlyInterface(BaseBackend):
    """Plotly interface for visualization."""

    def __init__(self, **kwargs):
        self._fig = go.Figure()

    def _pv_to_mesh3d(self, pv_mesh: PolyData) -> go.Mesh3d:
        """Convert a PyVista PolyData mesh to Plotly Mesh3d format."""
        points = pv_mesh.points
        x, y, z = points[:, 0], points[:, 1], points[:, 2]
        
        faces = pv_mesh.faces.reshape((-1, 4))  # First number in each row is the number of points in the face (3 for triangles)
        i, j, k = faces[:, 1], faces[:, 2], faces[:, 3]
        
        return go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k)
    @property
    def layout(self) -> Any:
        """Get the current layout of the Plotly figure."""
        return self._fig.layout
    
    @setters.layout
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

    def show(self):
        """Render the Plotly scene."""
        self._fig.show()
