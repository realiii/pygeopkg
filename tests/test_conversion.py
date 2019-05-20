"""
Test conversion
"""
import sys
from unittest import TestCase
from struct import unpack
from pygeopkg.conversion.to_geopkg_geom import (
    make_gpkg_geom_header, point_to_gpkg_point, points_to_gpkg_line_string,
    point_lists_to_gpkg_polygon, points_z_to_gpkg_line_string_z,
    points_m_to_gpkg_line_string_m, points_zm_to_gpkg_line_string_zm, GP_MAGIC,
    points_to_gpkg_multipoint)
from pygeopkg.conversion.to_wkb import (
    point_to_wkb_point, points_to_wkb_line_string, point_lists_to_wkb_polygon,
    point_z_to_wkb_point_z, point_m_to_wkb_point_m, point_zm_to_wkb_point_zm,
    points_z_to_wkb_line_string_z, point_lists_to_wkb_multipolygon,
    multipoint_to_wkb_multipoint, point_lists_to_multi_line_string)


class TestConversion(TestCase):
    """
    Test the conversion utils
    """
    @staticmethod
    def _unpack_byte_and_type(data):
        """
        Unpack the byte and type
        :param data:
        :return:
        """
        return unpack('<BI', data)

    @staticmethod
    def _unpack_base_point(data):
        """
        Unpack a Point
        """
        return unpack('<2d', data)
    # End _unpack_point function

    @staticmethod
    def _unpack_base_point_z_or_m(data):
        """
        Unpack a Point
        """
        return unpack('<3d', data)
    # End _unpack_point function

    @staticmethod
    def _unpack_base_point_z_and_m(data):
        """
        Unpack a Point
        """
        return unpack('<4d', data)
    # End _unpack_point function

    def _unpack_base_points(self, data, geom_type):
        """
        Unpack a set of points (aka LineString or LinearRing)
        data should include the count at the front
        """
        if geom_type < 17:
            unpacker = self._unpack_base_point
            point_len = 16
        elif geom_type < 3000:
            unpacker = self._unpack_base_point_z_or_m
            point_len = 24
        elif geom_type < 3017:
            unpacker = self._unpack_base_point_z_and_m
            point_len = 32
        else:
            raise ValueError('bad wkb')

        count = unpack('<I', data[:4])[0]
        points = []
        last_end = 4
        for i in range(0, count):
            end = last_end + point_len
            points.append(unpacker(data[last_end: end]))
            last_end = end
        return points
    # End _unpack_line function

    @staticmethod
    def _unpack_wkb_point(data):
        """
        Unpack a Point
        """
        return unpack('<2d', data[5:])
    # End _unpack_point function

    @staticmethod
    def _unpack_wkb_point_z_or_m(data):
        """
        Unpack a Point
        """
        return unpack('<3d', data[5:])
    # End _unpack_point function

    @staticmethod
    def _unpack_wkb_point_z_and_m(data):
        """
        Unpack a Point
        """
        return unpack('<4d', data[5:])
    # End _unpack_point function

    def _unpack_wkb_points(self, data, geom_type):
        """
        Unpack a well known binary point
        """
        if geom_type < 17:
            unpacker = self._unpack_wkb_point
            point_len = 16 + 5
        elif geom_type < 3000:
            unpacker = self._unpack_wkb_point_z_or_m
            point_len = 24 + 5
        elif geom_type < 3017:
            unpacker = self._unpack_wkb_point_z_and_m
            point_len = 32 + 5
        else:
            raise ValueError('bad wkb')

        count = unpack('<I', data[:4])[0]
        points = []
        last_end = 4
        for i in range(0, count):
            end = last_end + point_len
            points.append(unpacker(data[last_end: end]))
            last_end = end
        return points
    # End _unpack_wkb_points method

    def _unpack_rings(self, data, geom_type):
        """
        Unpack a set of rings. should include the count at the beginning

        :param data:
        :return:
        """
        if geom_type < 17:
            point_len = 16
        elif geom_type < 3000:
            point_len = 24
        elif geom_type < 3017:
            point_len = 32
        else:
            raise ValueError('bad wkb')

        count = unpack('<I', data[:4])[0]
        data = data[4:]
        rings = []
        last_end = 0
        for i in range(0, count):
            ring_length = unpack('<I', data[last_end:last_end + 4])[0]
            end = last_end + 4 + point_len * ring_length
            points = self._unpack_base_points(data[last_end:end], geom_type)
            last_end = end
            rings.append(points)
        return rings
    # End _unpack_rings

    def _unpack_wkb_multi_linestrings(self, data, geom_type):
        """
        Unpack a set of wkb multilinestrings. should include the count at
        the beginning

        Note! a multi line string is a just a list of WKB Linestrings with
        consisting of a bunch of base points.
        """
        if geom_type < 17:
            point_len = 16
        elif geom_type < 3000:
            point_len = 24
        elif geom_type < 3017:
            point_len = 32
        else:
            raise ValueError('bad wkb')

        count = unpack('<I', data[:4])[0]
        data = data[4:]
        rings = []
        last_end = 0
        for i in range(0, count):
            _, _, ring_length = unpack('<BII', data[last_end: last_end + 9])
            end = last_end + 9 + point_len * ring_length
            points = self._unpack_base_points(data[last_end + 5:end], geom_type)
            last_end = end
            rings.append(points)
        return rings
    # End _unpack_wkb_rings method

    def _unpack_wkb_multi_polygons(self, data, geom_type):
        """
        Unpack a set of wkb polys.  Should include the count at the begnning

        Note! a multi polygon is a set of base linestrings and points.
        """
        if geom_type < 17:
            point_len = 16
        elif geom_type < 3000:
            point_len = 24
        elif geom_type < 3017:
            point_len = 32
        else:
            raise ValueError('bad wkb')

        count = unpack('<I', data[:4])[0]
        data = data[4:]
        rings = []
        last_end = 0
        for i in range(0, count):
            points = self._unpack_rings(data[last_end + 5:], geom_type)
            num_rings = len(points)
            points_in_poly = sum(len(x) for x in points)
            last_end = points_in_poly * point_len + num_rings * 4 + 9
            rings.append(points)
        return rings
    # End _unpack_wkb_multi_polygons method

    def test_wkb_point(self):
        """
        Test the basic point
        """
        out = point_to_wkb_point(45, 20)
        expected = (1, 1, 45.0, 20.0)
        test = unpack('<BI2d', out)
        self.assertEqual(expected, test)
    # End test_wkb_point method

    def test_wkb_pointz(self):
        """
        Test the basic point
        """
        out = point_z_to_wkb_point_z(45, 20, 10)
        expected = (1, 1001, 45.0, 20.0, 10.0)
        test = unpack('<BI3d', out)
        self.assertEqual(expected, test)
    # End test_wkb_point method

    def test_wkb_pointm(self):
        """
        Test the basic point
        """
        out = point_m_to_wkb_point_m(45, 20, 10)
        expected = (1, 2001, 45.0, 20.0, 10.0)
        test = unpack('<BI3d', out)
        self.assertEqual(expected, test)
    # End test_wkb_point method

    def test_wkb_pointzm(self):
        """
        Test the basic point
        """
        out = point_zm_to_wkb_point_zm(45, 20, 10, 5)
        expected = (1, 3001, 45.0, 20.0, 10.0, 5.0)
        test = unpack('<BI4d', out)
        self.assertEqual(expected, test)
    # End test_wkb_point method

    def test_wkb_multipoint(self):
        """
        Test the basic multi point
        """
        expected = [(0.0, 0.0), (1.0, 1.0)]
        out = multipoint_to_wkb_multipoint(expected)
        test = self._unpack_byte_and_type(out[:5])
        self.assertEqual((1, 4), test)
        length = unpack('<I', out[5:9])[0]
        self.assertEqual(length, 2)
        points = self._unpack_wkb_points(out[5:], test[1])
        self.assertEqual(points, expected)
    # End test_wkb_multipoint method

    def test_wkb_line(self):
        """
        Test the line string
        """
        expected = [(0.0, 0.0), (1.0, 1.0)]
        out = points_to_wkb_line_string(expected)
        test = self._unpack_byte_and_type(out[:5])
        self.assertEqual((1, 2), test)
        length = unpack('<I', out[5:9])[0]
        self.assertEqual(length, 2)
        points = self._unpack_base_points(out[5:], test[1])
        self.assertEqual(points, expected)
    # End test_wkb_line

    def test_wkb_multiline(self):
        """
        Test the multi line
        """
        expected = [[(300000.0, 1.0), (300000.0, 4000000.0),
                     (700000.0, 4000000.0), (700000.0, 1.0), (300000.0, 1.0)],
                    [(400000.0, 100000.0), (600000.0, 100000.0),
                     (600000.0, 3900000.0), (400000.0, 3900000),
                     (400000.0, 100000.0)]]
        out = point_lists_to_multi_line_string(expected)
        test = self._unpack_byte_and_type(out[:5])
        self.assertEqual((1, 5), test)
        points = self._unpack_wkb_multi_linestrings(out[5:], test[1])
        self.assertEqual(points, expected)
    # End test_wkb_multiline method

    def test_wkb_poly(self):
        """
        Test the polygon
        """
        expected = [[(300000.0, 1.0), (300000.0, 4000000.0),
                     (700000.0, 4000000.0), (700000.0, 1.0), (300000.0, 1.0)]]
        out = point_lists_to_wkb_polygon(expected)
        test = self._unpack_byte_and_type(out[:5])
        self.assertEqual((1, 3), test)
        rings = self._unpack_rings(out[5:], test[1])
        self.assertEqual(rings, expected)
    # End test_wkb_poly

    def test_wkb_multi_poly(self):
        """
        Test the polygon
        """
        expected = [[[(300000.0, 1.0), (300000.0, 4000000.0),
                   (700000.0, 4000000.0), (700000.0, 1.0), (300000.0, 1.0)]],
                 [[(100000.0, 1000000.0), (100000.0, 2000000.0),
                   (200000.0, 2000000.0), (200000.0, 1000000.0),
                   (100000.0, 1000000.0)]]]
        out = point_lists_to_wkb_multipolygon(expected)
        test = self._unpack_byte_and_type(out[:5])
        self.assertEqual((1, 6), test)
        points = self._unpack_wkb_multi_polygons(out[5:], test[1])
        self.assertEqual(expected, points)
    # End test_wkb_poly

    def test_gpkg_header(self):
        """
        Test the Geopackage Header
        """
        hdr = make_gpkg_geom_header(32623)
        test = unpack('<2s2bi', hdr)
        self.assertEqual((GP_MAGIC, 0, 1, 32623), test)
    # End test_gpkg_header

    def test_gpkg_point(self):
        """
        Test geopackage point
        """
        hdr = make_gpkg_geom_header(32623)
        out = point_to_gpkg_point(hdr, 23.0, 99.0)
        out_hdr = unpack('<2s2bi', out[:8])
        self.assertEqual((GP_MAGIC, 0, 1, 32623), out_hdr)
        wkb_point_hdr = self._unpack_byte_and_type(out[8:13])
        self.assertEqual(wkb_point_hdr, (1, 1))
        point = self._unpack_base_point(out[13:])
        self.assertEqual((23.0, 99.0), point)
    # End test_gpkg_point

    def test_gpkg_multipoint(self):
        """
        Test the geopackage multpoint
        """
        hdr = make_gpkg_geom_header(32623)
        expected = [(300000.0, 1.0), (700000.0, 4000000.0)]
        out = points_to_gpkg_multipoint(hdr, expected)
        wkb_mp_hdr = self._unpack_byte_and_type(out[8:13])
        self.assertEqual(wkb_mp_hdr, (1, 4))
        points = self._unpack_wkb_points(out[13:], wkb_mp_hdr[1])
        self.assertEqual(expected, points)

    def test_gpkg_line(self):
        """
        Test geopackage line
        """
        hdr = make_gpkg_geom_header(32623)
        expected = [(300000.0, 1.0), (700000.0, 4000000.0)]
        out = points_to_gpkg_line_string(hdr, expected)
        wkb_line_hdr = self._unpack_byte_and_type(out[8:13])
        self.assertEqual(wkb_line_hdr, (1, 2))
        points = self._unpack_base_points(out[13:], wkb_line_hdr[1])
        self.assertEqual(expected, points)

    def test_gpkg_linez(self):
        """
        Test geopackage line
        """
        hdr = make_gpkg_geom_header(32623)
        expected = [(300000.0, 1.0, 20.0), (700000.0, 4000000.0, 40.0)]
        out = points_z_to_gpkg_line_string_z(hdr, expected)
        wkb_line_hdr = self._unpack_byte_and_type(out[8:13])
        self.assertEqual(wkb_line_hdr, (1, 1002))
        points = self._unpack_base_points(out[13:], wkb_line_hdr[1])
        self.assertEqual(expected, points)

    def test_gpkg_linem(self):
        """
        Test geopackage line
        """
        hdr = make_gpkg_geom_header(32623)
        expected = [(300000.0, 1.0, 20.0), (700000.0, 4000000.0, 40.0)]
        out = points_m_to_gpkg_line_string_m(hdr, expected)
        wkb_line_hdr = self._unpack_byte_and_type(out[8:13])
        self.assertEqual(wkb_line_hdr, (1, 2002))
        points = self._unpack_base_points(out[13:], wkb_line_hdr[1])
        self.assertEqual(expected, points)

    def test_gpkg_linezm(self):
        """
        Test geopackage line
        """
        hdr = make_gpkg_geom_header(32623)
        expected = [(300000.0, 1.0, 20.0, 0), (700000.0, 4000000.0, 40.0, 1000)]
        out = points_zm_to_gpkg_line_string_zm(hdr, expected)
        wkb_line_hdr = self._unpack_byte_and_type(out[8:13])
        self.assertEqual(wkb_line_hdr, (1, 3002))
        points = self._unpack_base_points(out[13:], wkb_line_hdr[1])
        self.assertEqual(expected, points)

    def test_gpkg_poly(self):
        """
        Test geopackage poly
        """
        hdr = make_gpkg_geom_header(32623)
        expected = [[(300000.0, 1.0), (300000.0, 4000000.0),
                     (700000.0, 4000000.0), (700000.0, 1.0), (300000.0, 1.0)]]
        out = point_lists_to_gpkg_polygon(hdr, expected)
        wkb_poly_hdr = self._unpack_byte_and_type(out[8:13])
        self.assertEqual(wkb_poly_hdr, (1, 3))
        rings = self._unpack_rings(out[13:], wkb_poly_hdr[1])
        self.assertEqual(expected, rings)

    def test_gpkg_poly_hole(self):
        """
        Test geopackage poly with hole
        """
        hdr = make_gpkg_geom_header(32623)
        expected = [[(300000.0, 1.0), (300000.0, 4000000.0),
                     (700000.0, 4000000.0), (700000.0, 1.0), (300000.0, 1.0)],
                    [(400000.0, 100000.0), (600000.0, 100000.0),
                     (600000.0, 3900000.0), (400000.0, 3900000),
                     (400000.0, 100000.0)]]
        out = point_lists_to_gpkg_polygon(hdr, expected)
        wkb_poly_hdr = self._unpack_byte_and_type(out[8:13])
        self.assertEqual(wkb_poly_hdr, (1, 3))
        rings = self._unpack_rings(out[13:], wkb_poly_hdr[1])
        self.assertEqual(expected, rings)
