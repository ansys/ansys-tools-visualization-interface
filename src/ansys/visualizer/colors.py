from enum import Enum

class Colors(Enum):
    DEFAULT_COLOR = "#D6F7D1"
    """Default color we use for the plotter actors."""

    PICKED_COLOR = "#BB6EEE"
    """Color to use for the actors that are currently picked."""

    EDGE_COLOR = "#000000"
    """Default color to use for the edges."""

    PICKED_EDGE_COLOR = "#9C9C9C"
    """Color to use for the edges that are currently picked."""