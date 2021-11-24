"""
Convert to Geopackage Geometry Blobs
"""
from sys import version_info
from struct import pack
from pygeopkg.conversion.to_wkb import (
    point_to_wkb_point, point_z_to_wkb_point_z, point_m_to_wkb_point_m,
    point_zm_to_wkb_point_zm, points_to_wkb_line_string,
    points_z_to_wkb_line_string_z, points_m_to_wkb_line_string_m,
    points_zm_to_wkb_line_string_zm, point_lists_to_wkb_polygon,
    point_lists_to_wkb_multipolygon, multipoint_to_wkb_multipoint,
    point_lists_to_multi_line_string)

GP_MAGIC = 'GP'
if version_info > (3,):
    GP_MAGIC = b'GP'
    # noinspection PyShadowingBuiltins
    buffer = bytes


def make_gpkg_geom_header(srs_id):
    """
    Make a Geopackage geometry binary header

    :param srs_id: The spatial reference id
    :type srs_id: int
    :return: the packed srs id
    """
    magic, version, flags = GP_MAGIC, 0, 1
    return pack('<2s2bi', magic, version, flags, srs_id)
# End make_gpkg_geom_header function


def point_to_gpkg_point(header, x, y):
    """
    Point to WKBPoint

    :param x: x coord
    :type x: float
    :param y: y coord
    :type y: float
    :param header: the binary header, see "make_gpkg_geom_header"
    :return: the WKB
    """
    return buffer(header + point_to_wkb_point(x, y))
# End point_to_gpkg_point


def point_z_to_gpkg_point_z(header, x, y, z):
    """
    Point to WKBPointZ

    :param x: x coord
    :type x: float
    :param y: y coord
    :type y: float
    :param z: z coord
    :type z: float
    :param header: the binary header, see "make_gpkg_geom_header"
    """
    return buffer(header + point_z_to_wkb_point_z(x, y, z))
# End point_z_to_gpkg_point_z function


def point_m_to_gpkg_point_m(header, x, y, m):
    """
    Point to WKBPointM

    :param x: x coord
    :type x: float
    :param y: y coord
    :type y: float
    :param m: m coord
    :type m: float
    :param header: the binary header, see "make_gpkg_geom_header"
    """
    return buffer(header + point_m_to_wkb_point_m(x, y, m))
# End point_m_to_gpkg_point_m function


def point_zm_to_gpkg_point_zm(header, x, y, z, m):
    """
    Point to WKBPointZM

    :param x: x coord
    :type x: float
    :param y: y coord
    :type y: float
    :param z: z coord
    :type z: float
    :param m: m coord
    :type m: float
    :param header: the binary header, see "make_gpkg_geom_header"
    """
    return buffer(header + point_zm_to_wkb_point_zm(x, y, z, m))
# End point_zm_to_gpkg_point_zm function


def points_to_gpkg_multipoint(header, points):
    """
    List of points to a gpkg multi point blob
    """
    return buffer(header + multipoint_to_wkb_multipoint(points))
# End points_to_gpkg_multi_point function


def points_to_gpkg_line_string(header, points):
    """
    List of points to a gpkg blob

    :param header: the binary header, see "make_gpkg_geom_header"
    :param points: list of points making up the line
    :type points: list
    :return:
    """
    return buffer(header + points_to_wkb_line_string(points))
# End points_to_gpkg_line_string


def points_z_to_gpkg_line_string_z(header, points):
    """

    :param header: the binary header, see "make_gpkg_geom_header"
    :param points: List of points making up the line
    :type points: list
    :return:
    """
    return buffer(header + points_z_to_wkb_line_string_z(points))
# End points_to_gpkg_line_string


def points_m_to_gpkg_line_string_m(header, points):
    """

    :param header: the binary header, see "make_gpkg_geom_header"
    :param points: List of points making up the line
    :type points: list
    :return:
    """
    return buffer(header + points_m_to_wkb_line_string_m(points))
# End points_to_gpkg_line_string


def points_zm_to_gpkg_line_string_zm(header, points):
    """

    :param header: the binary header, see "make_gpkg_geom_header"
    :param points: List of points making up the line
    :type points: list
    :return:
    """
    return buffer(header + points_zm_to_wkb_line_string_zm(points))
# End points_zm_to_gpkg_line_string_zm function


def point_lists_to_gpkg_multi_line_string(header, point_lists):
    """

    :param header:
    :param point_lists:
    :return:
    """
    return buffer(header + point_lists_to_multi_line_string(point_lists))
# End point_lists_to_gpkg_multi_line_string function


def point_lists_to_gpkg_polygon(header, ring_point_lists):
    """
    Ring point lists should be lists of points representing poly rings.

    # NOTE!! You MUST close the polygon or ArcMap will be unhappy!

    i.e. [[(x, y), (x, y), ..],[(x, y), (x, y)...]]

    :param header: the binary header, see "make_gpkg_geom_header"
    :param ring_point_lists: List of rings in the polygon
    :type ring_point_lists: list
    :return:
    """
    return buffer(header + point_lists_to_wkb_polygon(ring_point_lists))
# End point_lists_to_wkb_polygon function


def point_lists_to_gpkg_multi_polygon(header, list_of_polys):
    """
    This is a list (polygons) which are lists of rings which are lists of points
    Point lists should be lists of points representing poly rings.

    i.e. [[[(x, y), (x, y), ..],[(x, y), (x, y)...]],[etc]]
    """
    return buffer(header + point_lists_to_wkb_multipolygon(list_of_polys))
# End point_lists_to_gpkg_multi_polygon function


def wkb_to_gpkg_geometry(header, wkb):
    """
    This accepts a WKB object from PostGIS created with ST_AsBinary()
    :param header: the binary header, see "make_gpkg_geom_header"
    :param wkb: wkb object
    :return:
    """
    return buffer(header + wkb)


if __name__ == '__main__':
    pass
