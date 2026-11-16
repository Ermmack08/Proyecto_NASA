import tempfile
import unittest
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import transform

from modules.data_loader import _sample_raster_point


class SatelliteSamplingTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.raster_path = Path(self.temporary_directory.name) / "sample.tif"
        self.transform = from_origin(500000, 700000, 10, 10)
        values = np.array(
            [[0.15, 0.35], [0.55, -9999.0]],
            dtype=np.float32,
        )
        with rasterio.open(
            self.raster_path,
            "w",
            driver="GTiff",
            width=2,
            height=2,
            count=1,
            dtype="float32",
            crs="EPSG:32618",
            transform=self.transform,
            nodata=-9999.0,
        ) as dataset:
            dataset.write(values, 1)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def _point_for_pixel(self, row, column):
        with rasterio.open(self.raster_path) as dataset:
            x, y = dataset.xy(row, column)
            longitude, latitude = transform(
                dataset.crs,
                "EPSG:4326",
                [x],
                [y],
            )
        return latitude[0], longitude[0]

    def _sample(self, latitude, longitude):
        return _sample_raster_point(
            str(self.raster_path),
            self.raster_path.stat().st_mtime_ns,
            latitude,
            longitude,
        )

    def test_samples_value_and_pixel_center_for_wgs84_point(self):
        latitude, longitude = self._point_for_pixel(0, 1)

        result = self._sample(latitude, longitude)

        self.assertIsNotNone(result)
        self.assertAlmostEqual(result["values"][0], 0.35)
        self.assertAlmostEqual(result["pixel_center"]["latitude"], latitude, places=5)
        self.assertAlmostEqual(result["pixel_center"]["longitude"], longitude, places=5)

    def test_returns_none_for_nodata_or_outside_point(self):
        nodata_latitude, nodata_longitude = self._point_for_pixel(1, 1)

        self.assertIsNone(self._sample(nodata_latitude, nodata_longitude))
        self.assertIsNone(self._sample(0, 0))


if __name__ == "__main__":
    unittest.main()
