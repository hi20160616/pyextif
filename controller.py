import os
import pathlib
import lonlat2geo
from osgeo import ogr
from tiff import Tiff


class Controller:
    """Deal with folder and files"""

    def __init__(self, src=os.getcwd(), cfg="config.txt"):
        self.src = src if src else os.getcwd()
        self.cfg = cfg if cfg else "config.txt"
        self.tifs = []
        self.areas = []
        # self.read_cfg(self.cfg)
        # self.scan_tifs(self.src)

    def scan_tifs(self, dir):
        """Scan dir for tif files recursively"""

        for entry in os.scandir(dir):
            if entry.is_dir():
                self.scan_tifs(entry)
            elif not entry.name.startswith(".") and entry.name.endswith(".tif"):
                tif = Tiff(entry.path)
                self.tifs.append(tif)

    def read_cfg(self, cfg):
        with open(cfg) as f:
            for line in f:
                if not line.strip() or line.startswith("#") or line.startswith("//"):
                    continue
                line = line.split('//')[0].strip()
                name, poly = line.split(':')
                points = poly.strip().split('|') if poly else []
                self.areas.append([name, points])
                # wkt = ""
                # name, poly = line.split(':')
                # points = poly.strip().split('|') if poly else []
                # for p in points:
                #     p1, p2 = p.split(',')
                #     p1 = lonlat2geo.degree2float(p1.strip())
                #     p2 = lonlat2geo.degree2float(p2.strip())
                #     p = lonlat2geo.lonlat2geo_static(
                #         3857, p1, p2)  # TODO: 坐标系3857是否会发生变化？
                #     wkt += p + ', '
                # wkt = f"POINT ({wkt[:-2]})" if len(
                #     points) == 1 else f"POLYGON (({wkt[:-2]}))"
                # self.areas.append([name, wkt.strip()])

    def set_tifs_area(self):
        """if tif intersected with areas in config, set the areaname to the tif."""

        def intersection(wkt1, wkt2):
            poly1 = ogr.CreateGeometryFromWkt(wkt1)
            poly2 = ogr.CreateGeometryFromWkt(wkt2)
            intersection = poly1.Intersection(poly2)
            if "EMPTY" in intersection.ExportToWkt():
                # print("wkt1: " + wkt1)  # just for debug
                # print("wkt2: " + wkt2)  # just for debug
                return False
            else:
                return True

        for tif in self.tifs:
            tif.dataset_open()
            # tif.gdalinfo()  # just for debug.
            tif.make_wkt_geom()
            for area in self.areas:
                wkt = tif.points2wkt(area[1])
                if intersection(tif.wkt, wkt):
                    tif.areanames.append(area[0])
            tif.dataset_close()

    def rename(self):
        """rename tif name if shot,
        also contain siblings files and folder that have same name.

        TODO: if areanames is contained, not add the prefix to the files.
        """

        for tif in self.tifs:
            prefix = ""
            for area in tif.areanames:
                prefix += f"[{area}]"
            if prefix == "":
                continue
            # rename tif file only
            newtifpath = os.path.join(tif.dir, prefix + tif.filename)
            # print(f"[{tif.filepath}] => should rename as => [{newtifpath}]")
            os.rename(tif.filepath, newtifpath)

            # rename siblings
            tif.set_siblings()
            for s in tif.siblings:
                oldpath = os.path.join(tif.dir, s)
                newpath = os.path.join(tif.dir, prefix + s)
                # print(f"[{oldpath}] => should rename as => [{newpath}]")
                os.rename(oldpath, newpath)

            # rename tif dir, if it's name is same as tif file.
            tiffoldername = os.path.split(tif.dir)[1]
            puretifname = tif.filename.split(".tif")[0]
            if tiffoldername == puretifname:
                oldpath = tif.dir
                newpath = tif.dir.replace(puretifname, prefix + puretifname)
                # print(f"[{oldpath}] => should rename as => [{newpath}]")
                os.rename(oldpath, newpath)
