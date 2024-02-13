"""Module for the ClipPlane class."""
from beartype.typing import Tuple

class ClipPlane():
    def __init__(self, normal: Tuple[float, float, float] = (1, 0, 0), origin: Tuple[float, float, float] = (0, 0, 0)):
        """Clipping plane for clipping meshes in the plotter. The clipping plane is defined by a normal and an origin.

        Parameters
        ----------
        normal : Tuple[float, float, float], optional
            Normal of the plane, by default (1, 0, 0).
        origin : Tuple[float, float, float], optional
            Origin point of the plane, by default (0, 0, 0).
        """
        self.normal = normal
        self.origin = origin
    @property
    def normal(self) -> Tuple[float, float, float]:
        """Return the normal of the plane.

        Returns
        -------
        Tuple[float, float, float]
            Normal of the plane.
        """
        return self._normal
    
    @normal.setter
    def normal(self, value: Tuple[float, float, float]) -> None:
        """Set the normal of the plane.

        Parameters
        ----------
        value : Tuple[float, float, float]
            Normal of the plane.
        """
        self._normal = value
    
    @property
    def origin(self) -> Tuple[float, float, float]:
        """Return the origin of the plane.

        Returns
        -------
        Tuple[float, float, float]
            Origin of the plane.
        """
        return self._origin
    
    @origin.setter
    def origin(self, value: Tuple[float, float, float]) -> None:
        """Set the origin of the plane.

        Parameters
        ----------
        value : Tuple[float, float, float]
            Origin of the plane.
        """
        self._origin = value