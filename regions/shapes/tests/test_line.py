# Licensed under a 3-clause BSD style license - see LICENSE.rst

from __future__ import absolute_import, division, print_function, unicode_literals

from numpy.testing import assert_allclose
import pytest

from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.tests.helper import assert_quantity_allclose
from astropy.utils.data import get_pkg_data_filename
from astropy.io import fits
from astropy.wcs import WCS

from ...tests.helpers import make_simple_wcs
from ...core import PixCoord
from ..line import LinePixelRegion, LineSkyRegion
from .utils import ASTROPY_LT_13, HAS_MATPLOTLIB  # noqa
from .test_common import BaseTestPixelRegion, BaseTestSkyRegion


@pytest.fixture(scope='session')
def wcs():
    filename = get_pkg_data_filename('data/example_header.fits')
    header = fits.getheader(filename)
    return WCS(header)


class TestLinePixelRegion(BaseTestPixelRegion):

    reg = LinePixelRegion(PixCoord(3, 4), PixCoord(4, 4))
    sample_box = [-2, 8, -1, 9]
    inside = []
    outside = [(3.1, 4.2), (5, 4)]
    expected_area = 0
    expected_repr = '<LinePixelRegion(start=PixCoord(x=3, y=4), end=PixCoord(x=4, y=4))>'
    expected_str = 'Region: LinePixelRegion\nstart: PixCoord(x=3, y=4)\nend: PixCoord(x=4, y=4)'

    def test_pix_sky_roundtrip(self):
        wcs = make_simple_wcs(SkyCoord(2 * u.deg, 3 * u.deg), 0.1 * u.deg, 20)
        reg_new = self.reg.to_sky(wcs).to_pixel(wcs)
        assert_allclose(reg_new.start.x, self.reg.start.x)
        assert_allclose(reg_new.start.y, self.reg.start.y)
        assert_allclose(reg_new.end.x, self.reg.end.x)
        assert_allclose(reg_new.end.y, self.reg.end.y)

    @pytest.mark.skipif('not HAS_MATPLOTLIB')
    def test_as_patch(self):
        patch = self.reg.as_patch()
        assert 'Arrow' in str(patch)


class TestLineSkyRegion(BaseTestSkyRegion):

    start = SkyCoord(3 * u.deg, 4 * u.deg, frame='galactic')
    end = SkyCoord(3 * u.deg, 5 * u.deg, frame='galactic')
    reg = LineSkyRegion(start, end)

    if ASTROPY_LT_13:
        expected_repr = ('<LineSkyRegion(start=<SkyCoord (Galactic): (l, b) in deg\n'
                         '    (3.0, 4.0)>, end=<SkyCoord (Galactic): (l, b) in deg\n'
                         '    (3.0, 5.0)>)>')
        expected_str = ('Region: LineSkyRegion\nstart: <SkyCoord (Galactic): (l, b) in deg\n'
                         '    (3.0, 4.0)>\nend: <SkyCoord (Galactic): (l, b) in deg\n'
                         '    (3.0, 5.0)>')
    else:
        expected_repr = ('<LineSkyRegion(start=<SkyCoord (Galactic): (l, b) in deg\n'
                         '    ( 3.,  4.)>, end=<SkyCoord (Galactic): (l, b) in deg\n'
                         '    ( 3.,  5.)>)>')
        expected_str = ('Region: LineSkyRegion\nstart: <SkyCoord (Galactic): (l, b) in deg\n'
                         '    ( 3.,  4.)>\nend: <SkyCoord (Galactic): (l, b) in deg\n'
                         '    ( 3.,  5.)>')

    def test_transformation(self, wcs):
        pixline = self.reg.to_pixel(wcs)

        assert_allclose(pixline.start.x, -50.5)
        assert_allclose(pixline.start.y, 299.5)
        assert_allclose(pixline.end.x, -50.5)
        assert_allclose(pixline.end.y, 349.5)

        skyline = pixline.to_sky(wcs)

        assert_quantity_allclose(skyline.start.data.lon, self.reg.start.data.lon)
        assert_quantity_allclose(skyline.start.data.lat, self.reg.start.data.lat)
        assert_quantity_allclose(skyline.end.data.lon, self.reg.end.data.lon)
        assert_quantity_allclose(skyline.end.data.lat, self.reg.end.data.lat)
