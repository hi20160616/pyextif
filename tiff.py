import os
import lonlat2geo
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

    def dataset_open(self):
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

    def gdalinfo(self):
        print(
            f"Driver: {self.ds.GetDriver().ShortName} / {self.ds.GetDriver().LongName}")
        print(f"Size is {self.ds.RasterXSize}, {self.ds.RasterYSize}")
        print(f"Bands = %d" % self.ds.RasterCount)
        print(f"Coordinate System is: {self.ds.GetProjectionRef ()}")
        print(f"GetGeoTransform() = {self.ds.GetGeoTransform ()}")
        print(f"GetMetadata() = {self.ds.GetMetadata ()}")

    def points2wkt(self, points):
        wkt = ""
        for p in points:
            p1, p2 = p.split(',')
            p1 = lonlat2geo.degree2float(p1.strip())
            p2 = lonlat2geo.degree2float(p2.strip())
            p = lonlat2geo.lonlat2geo_ds(self.ds, p1, p2)
            wkt += f'{p[0]} {p[1]}' + ', '
        return f"POINT ({wkt[:-2]})" if len(points) == 1 else f"POLYGON (({wkt[:-2]}))"

    def make_wkt_geom(self):
        """This will get geo wkt string, and only be used after dataset open success."""

        def make_wkt(points):
            pp = ""
            for point in points:
                pp += f"{point[0]} {point[1]}, "
            pp = pp[:-2]
            return f"POLYGON (({pp}))"

        ds = self.ds
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
