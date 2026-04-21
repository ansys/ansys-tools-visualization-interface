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
"""Provides the ``PlottingOptions`` dataclass for framework-specific plotting kwargs."""

from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from ansys.tools.visualization_interface.utils.clip_plane import ClipPlane


@dataclass
class PlottingOptions:
    """Structured representation of all plotting kwargs.

    Calling :meth:`from_kwargs` splits a raw ``**kwargs`` dictionary into:

    * **Framework fields** (``name_filter``, ``clipping_plane``) — consumed by
      the visualization framework and **not** forwarded to the renderer.
    * **extra** — every remaining key, forwarded verbatim to the underlying
      rendering library (PyVista ``add_mesh``, Plotly ``Figure.show``, etc.).

    Parameters
    ----------
    name_filter : str, optional
        Regular expression with the desired name or names to include in the
        plotter.  Objects whose ``name`` does not match the expression are
        skipped.
    clipping_plane : ClipPlane, optional
        Plane used to clip the mesh before adding it to the scene.
    extra : dict
        Renderer-specific options forwarded verbatim to the underlying library.
    """

    name_filter: Optional[str] = None
    clipping_plane: Optional["ClipPlane"] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_kwargs(cls, kwargs: Dict) -> "PlottingOptions":
        """Parse and consume **all** keys from *kwargs*.

        Framework-specific keys (matching dataclass fields other than
        ``extra``) are mapped to their typed fields.  All remaining keys are
        collected into :attr:`extra`.  The supplied *kwargs* dictionary is
        **cleared** in-place so that callers can safely inspect it afterwards
        and know it has been fully consumed.

        Parameters
        ----------
        kwargs : dict
            Mutable keyword-argument dictionary to parse.  All keys are
            removed in-place.

        Returns
        -------
        PlottingOptions
            Instance populated from *kwargs*.
        """
        framework_keys = {f.name for f in fields(cls) if f.name != "extra"}
        parsed = {key: kwargs.pop(key) for key in framework_keys if key in kwargs}
        extra = dict(kwargs)
        kwargs.clear()
        return cls(**parsed, extra=extra)
