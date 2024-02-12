from beartype.typing import Tuple

class ClipPlane():
    def __init__(self, normal: Tuple[float, float, float] = (1, 0, 0), origin: Tuple[float, float, float] = (0, 0, 0)):
        self.normal = normal
        self.origin = origin
    @property
    def normal(self) -> Tuple[float, float, float]:
        return self._normal
    
    @normal.setter
    def normal(self, value: Tuple[float, float, float]) -> None:
        self._normal = value
    
    @property
    def origin(self) -> Tuple[float, float, float]:
        return self._origin
    
    @origin.setter
    def origin(self, value: Tuple[float, float, float]) -> None:
        self._origin = value