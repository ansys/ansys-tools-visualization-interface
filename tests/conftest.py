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
"""Conftest file for unit tests."""
import os
from pathlib import Path

from PIL import Image, ImageChops
import pytest

os.environ.setdefault("PYANSYS_VISUALIZER_TESTMODE", "true")

@pytest.fixture
def image_compare():
    """Fixture to compare images."""
    def _compare_images(generated_image_path):
        """Compare two images and optionally save the difference image.

        Parameters
        ----------
        generated_image_path : str
            Path to the generated image.
        baseline_image_path : str
            Path to the baseline image.
        diff_image_path : str, optional
            Path to save the difference image if images do not match.

        Returns
        -------
        bool
            True if images match, False otherwise.
        """
        # Get the name of the image file using Pathlib
        image_name = Path(generated_image_path).name

        # Define the baseline image path
        baseline_image_path = Path(__file__).parent / "_image_cache" / image_name

        img1 = Image.open(generated_image_path).convert("RGB")
        try:
            img2 = Image.open(baseline_image_path).convert("RGB")
        except FileNotFoundError:
            # copy generated image to baseline location if baseline does not exist
            img1.save(baseline_image_path)
            img2 = Image.open(baseline_image_path).convert("RGB")

        # Compute the difference between the two images
        diff = ImageChops.difference(img1, img2)

        if diff.getbbox() is None:
            return True
        else:
            return False

    return _compare_images