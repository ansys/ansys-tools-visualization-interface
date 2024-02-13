import pyvista as pv
from beartype.typing import Any, List, Union
from ansys.visualizer.types.edgeplot import EdgePlot

class MeshObjectPlot():
    """Relates a custom object with a mesh, provided by consumer library."""
    def __init__(self, custom_object: Any, mesh: Union[pv.PolyData, pv.MultiBlock], actor: pv.Actor = None, edges: List[EdgePlot] = None) -> None:
        """Relates a custom object with a mesh, provided by consumer library.
        
        This class is meant to be used as a mapper between a custom object and its mesh representation. It is used 
        to store the custom object and its mesh, and to relate the custom object with its PyVista actor and its edges.

        Parameters
        ----------
        custom_object : Any
            Any object that the consumer library wants to relate with a mesh.
        mesh : Union[pv.PolyData, pv.MultiBlock]
            PyVista mesh that represents the custom object.
        actor : pv.Actor, optional
            Actor of the mesh in the plotter, by default None
        edges : List[EdgePlot], optional
            Edges of the object if they have any, by default None
        """
        self._custom_object = custom_object
        self._mesh = mesh
        self._actor = actor
        self._edges = edges
            
    @property
    def mesh(self) -> Union[pv.PolyData, pv.MultiBlock]:
        """Return the mesh of the object in PyVista format.

        Returns
        -------
        Union[pv.PolyData, pv.MultiBlock]
            Mesh of the object.
        """
        return self._mesh
    
    @mesh.setter
    def mesh(self, mesh: Union[pv.PolyData, pv.MultiBlock]):
        """Set the mesh of the object in PyVista format.

        Parameters
        ----------
        mesh : Union[pv.PolyData, pv.MultiBlock]
            Mesh of the object.
        """
        self._mesh = mesh
    
    @property
    def custom_object(self) -> Any:
        """Return the custom object.

        Returns
        -------
        Any
            Custom object.
        """
        return self._custom_object
    
    @custom_object.setter
    def custom_object(self, custom_object: Any):
        """Set the custom object.

        Parameters
        ----------
        custom_object : Any
            Custom object.
        """
        self._custom_object = custom_object
    
    @property
    def actor(self) -> pv.Actor:
        """Return the actor of the object in the plotter.

        Returns
        -------
        pv.Actor
            Actor of the object.
        """
        return self._actor

    @actor.setter
    def actor(self, actor: pv.Actor):
        """Set the actor of the object in the plotter.

        Parameters
        ----------
        actor : pv.Actor
            Actor of the object.
        """
        self._actor = actor
    
    @property
    def edges(self) -> List[EdgePlot]:
        """Return the edges of the object.

        Returns
        -------
        List[EdgePlot]
            Edges of the object.
        """
        return self._edges
    
    @edges.setter
    def edges(self, edges: List[EdgePlot]):
        """Set the edges of the object.

        Parameters
        ----------
        edges : List[EdgePlot]
            Edges of the object.
        """
        self._edges = edges
        
    @property
    def name(self) -> str:
        """Return the name of the object.

        Returns
        -------
        str
            Name of the object.
        """
        if hasattr(self._custom_object, "name"):
            return self._custom_object.name
        elif hasattr(self._custom_object, "id"):    
            return self._custom_object.id
        else:
            return "Unknown"