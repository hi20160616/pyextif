import os
from osgeo import gdal, ogr


class Tiff:
    """Tif file class"""

    def __init__(self, filepath):
        self.areanames = []
        self.ds = None
        self.filepath = filepath
        self.dir, self.filename = os.path.split(self.filepath)
        self.geometry = None
        self.siblings = []
        self.wkt = None

    def dataset(self):
        """Open tif file set `self.ds` and return dataset."""

        try:
            _ds = gdal.Open(self.filepath)
        except Exception as e:
            _ds = None
            raise e
        self.ds = _ds
        return _ds

    def dataset_close(self):
        self.ds = None

    def make_wkt_geom(self):
        """This should be used after dataset get done."""

        def make_wkt(points):
            pp = ""
            for point in points:
                pp += f"{point[0]} {point[1]}, "
            pp = pp[:-2]
            return f"POLYGON (({pp}))"

        ds = self.dataset()
        ulx, xres, _, uly, _, yres = ds.GetGeoTransform()
        lrx = ulx + (ds.RasterXSize * xres)  # low right x
        lry = uly + (ds.RasterYSize * yres)  # low right y
        minx, miny, maxx, maxy = ulx, lry, lrx, uly
        points = [[minx, miny], [maxx, miny], [
            maxx, maxy], [minx, maxy], [minx, miny]]
        self.wkt = make_wkt(points)
        self.geometry = ogr.CreateGeometryFromWkt(self.wkt)

    def set_siblings(self):
        """get and set sibling filepaths that have same name with tif file."""

        prename = self.filename.split(".tif")[0]
        tif_dir = os.path.split(self.filepath)[0]
        for item in os.scandir(tif_dir):
            itemname = os.path.basename(item)
            if itemname.split('.')[0] == prename:
                self.siblings.append(itemname)
