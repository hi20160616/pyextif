from osgeo import gdal
from osgeo import osr
from osgeo import ogr


def lonlat2geo_tif(dataset, lon, lat):
    """将经纬度坐标转为投影坐标（具体的投影坐标系由给定数据确定）

    :param dataset: tif 文件的数据集
    :param lon: 地理坐标lon经度
    :param lat: 地理坐标lat纬度

    :return: 经纬度坐标(lon, lat)对应的投影坐标
    """

    source = osr.SpatialReference()
    source.ImportFromWkt(dataset.GetProjection())
    target = source.CloneGeogCS()
    ct = osr.CoordinateTransformation(target, source)
    coords = ct.TransformPoint(lat, lon)
    return coords[:2]

def lonlat2geo_static(epsg, lon, lat):
    """将经纬度坐标转为投影坐标（具体的投影坐标系由给定数据确定）

    :param epsg: EPSG 数据库类型
    :param lon: 地理坐标lon经度
    :param lat: 地理坐标lat纬度

    :return: 经纬度坐标(lon, lat)对应的投影坐标
    """

    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)
    target = osr.SpatialReference()
    target.ImportFromEPSG(epsg)
    transform = osr.CoordinateTransformation(source, target)
    # transform = osr.CoordinateTransformation(target, source)
    # point = ogr.CreateGeometryFromWkt(f"POINT ({lat} {lon})")
    # point.Transform(transform)
    # return point.ExportToWkt()[7:-2]
    coords = transform.TransformPoint(lat, lon)
    return f"{coords[0]} {coords[1]}"


def degree2float(degree: str) -> float:
    """
    exchange degree style numbers to float style
    """

    if "°" in degree:
        degree = degree.replace('\'', '′').replace('\"', '″')
        d, dd = degree.split('°')
        d = float(d) if d else 0
        m, mm = dd.split('′')
        m = float(m) if m else 0
        s = mm.split('″')[0]
        s = float(s) if s else 0
        return d + m/60 + s/3600
    else:
        return float(degree)


if __name__ == '__main__':
    # lon = 122.47242
    # lat = 52.51778
    lon = degree2float("103°50′37.50″")
    lat = degree2float("36°6′15.00″")

    print('经纬度 -> 投影坐标：')
    coords = lonlat2geo_static(3857, lon, lat)
    print('(%s, %s)->(%s)' % (lon, lat, coords))

    ds = gdal.Open("./example/test/test.tif")
    coords = lonlat2geo_tif(ds, lon, lat)
    print('(%s, %s)->(%s)' % (lon, lat, coords))