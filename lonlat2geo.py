import osgeo
from osgeo import gdal
from osgeo import osr
from osgeo import ogr


def lonlat2geo_ds(dataset, lon, lat):
    """将经纬度坐标转为投影坐标（具体的投影坐标系由给定数据确定）

    :param dataset: tif 文件的数据集
    :param lon: 地理坐标lon经度
    :param lat: 地理坐标lat纬度

    :return: 经纬度坐标(lon, lat)对应的投影坐标
    """

    srs = osr.SpatialReference()
    srs.ImportFromWkt(dataset.GetProjection())
    if int(osgeo.__version__[0]) >= 3:
        # GDAL 3 changes axis order: https://github.com/OSGeo/gdal/issues/1546
        srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    tgt = srs.CloneGeogCS()
    ct = osr.CoordinateTransformation(tgt, srs)
    coords = ct.TransformPoint(lon, lat)
    return coords[:2]

def lonlat2geo_static(epsg, lon, lat):
    """将经纬度坐标转为投影坐标（具体的投影坐标系由给定数据确定）

    :param epsg: EPSG 数据库类型
    :param lon: 地理坐标lon经度
    :param lat: 地理坐标lat纬度

    :return: 经纬度坐标(lon, lat)对应的投影坐标
    """

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    if int(osgeo.__version__[0]) >= 3:
        # GDAL 3 changes axis order: https://github.com/OSGeo/gdal/issues/1546
        srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    tgt = osr.SpatialReference()
    tgt.ImportFromEPSG(epsg)
    ct = osr.CoordinateTransformation(srs, tgt)
    # transform = osr.CoordinateTransformation(tgt, srs)
    # point = ogr.CreateGeometryFromWkt(f"POINT ({lat} {lon})")
    # point.Transform(transform)
    # return point.ExportToWkt()[7:-2]
    coords = ct.TransformPoint(lon, lat)
    return f"{coords[0]} {coords[1]}"


def degree2float(degree: str) -> float:
    """
    exchange degree style numbers to float style
    """

    degree = degree.replace('°', 'd').replace('′', '\'').replace('″', '\"').lower()
    d = m = s = ""
    if 'd' in degree:
        d, dd = degree.split('d')
    else:
        return float(degree)
    if '\'' in degree:
        m, mm = dd.split('\'')
    if '\"' in degree:
        s = mm.split('\"')[0]
    d = float(d) if d else 0
    m = float(m) if m else 0
    s = float(s) if s else 0
    negative = True if 'w' in degree or 's' in degree else False
    if negative:
        return -float(d + m/60 + s/3600)
    else:
        return float(d + m/60 + s/3600)


if __name__ == '__main__':
    # lon = 122.47242
    # lat = 52.51778
    lon = degree2float("103°50′37.50″")
    lat = degree2float("36°6′15.00″")

    print('经纬度 -> 投影坐标：')
    coords = lonlat2geo_static(3857, lon, lat)
    print('(%s, %s)->(%s)' % (lon, lat, coords))

    ds = gdal.Open("./example/test/test.tif")
    coords = lonlat2geo_ds(ds, lon, lat)
    print('(%s, %s)->(%s)' % (lon, lat, coords))
