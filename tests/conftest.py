import pytest
import pyvista as pv

pv.OFF_SCREEN = True

@pytest.fixture(autouse=True)
def wrapped_verify_image_cache(verify_image_cache):
    return verify_image_cache