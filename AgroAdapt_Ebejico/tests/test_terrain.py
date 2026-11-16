import unittest

import numpy as np
from rasterio.crs import CRS
from rasterio.transform import from_origin

from modules.terrain import SLOPE_NODATA, compute_slope_degrees


class TerrainSlopeTests(unittest.TestCase):
    def setUp(self):
        self.transform = from_origin(-75.8, 6.4, 1 / 3600, 1 / 3600)
        self.crs = CRS.from_epsg(4326)

    def test_flat_dem_has_zero_slope_and_masks_edges(self):
        elevation = np.full((7, 7), 1200, dtype=np.float32)
        valid = np.ones(elevation.shape, dtype=bool)

        slope, slope_valid = compute_slope_degrees(
            elevation,
            valid,
            self.transform,
            self.crs,
        )

        self.assertAlmostEqual(float(slope[3, 3]), 0.0, places=5)
        self.assertTrue(np.all(slope_valid[1:-1, 1:-1]))
        self.assertFalse(slope_valid[0, 0])
        self.assertEqual(float(slope[0, 0]), SLOPE_NODATA)

    def test_planar_dem_returns_expected_angle_and_masks_nodata_neighbors(self):
        width = 7
        height = 7
        center_latitude = (
            self.transform.f + self.transform.e * (height / 2)
        )
        latitude_radians = np.deg2rad(center_latitude)
        meters_per_degree_longitude = (
            111412.84 * np.cos(latitude_radians)
            - 93.5 * np.cos(3 * latitude_radians)
        )
        pixel_width_m = abs(self.transform.a) * meters_per_degree_longitude
        gradient = 0.1
        elevation = np.tile(
            np.arange(width, dtype=np.float32) * pixel_width_m * gradient,
            (height, 1),
        )
        valid = np.ones(elevation.shape, dtype=bool)
        valid[3, 3] = False

        slope, slope_valid = compute_slope_degrees(
            elevation,
            valid,
            self.transform,
            self.crs,
        )

        expected = np.rad2deg(np.arctan(gradient))
        self.assertAlmostEqual(float(slope[1, 1]), expected, places=3)
        self.assertFalse(slope_valid[2, 2])
        self.assertFalse(slope_valid[4, 4])
        self.assertTrue(slope_valid[1, 1])

    def test_rejects_projected_crs(self):
        with self.assertRaises(ValueError):
            compute_slope_degrees(
                np.ones((3, 3), dtype=np.float32),
                np.ones((3, 3), dtype=bool),
                from_origin(500000, 700000, 30, 30),
                CRS.from_epsg(32618),
            )


if __name__ == "__main__":
    unittest.main()
