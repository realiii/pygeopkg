"""
Test GeoPackage
"""


from os.path import dirname, join, exists, isfile
from unittest import TestCase
from pygeopkg.conversion.to_geopkg_geom import (
    points_to_gpkg_line_string, make_gpkg_geom_header,
    point_lists_to_gpkg_polygon, points_z_to_gpkg_line_string_z,
    points_m_to_gpkg_line_string_m, points_zm_to_gpkg_line_string_zm,
    point_lists_to_gpkg_multi_polygon, points_to_gpkg_multipoint,
    point_lists_to_gpkg_multi_line_string)
from pygeopkg.core.geopkg import GeoPackage, GeoPkgFeatureClass, GeoPkgTable
from pygeopkg.core.srs import SRS
from pygeopkg.core.field import Field
from pygeopkg.shared.enumeration import GeometryType, SQLFieldTypes
from tests.projection_strings import WGS_1984_UTM_Zone_23N
from tests.utils import (
    check_ogr_trigger_exists, get_table_rows, check_table_exists,
    random_points_and_attrs, random_attrs)


class TestGeoPackage(TestCase):
    """
    Test GeoPackage
    """

    @staticmethod
    def _setup_basics(gpkg_name):
        """

        :param gpkg_name:
        :return:
        """
        target_path = join(dirname(__file__), gpkg_name)
        gpkg = GeoPackage.create(target_path)
        srs = SRS('WGS_1984_UTM_Zone_23N', 'EPSG', 32623, WGS_1984_UTM_Zone_23N)
        fields = (
            Field('int_fld', SQLFieldTypes.integer),
            Field('text_fld', SQLFieldTypes.text),
            Field('test_fld_size', SQLFieldTypes.text, 100),
            Field('test_bool', SQLFieldTypes.boolean))
        return target_path, gpkg, srs, fields

    def test_create_gpkg(self):
        """
        Test create a new gpkg
        """
        target_path = join(dirname(__file__), 'test_create.gpkg')
        gpkg = GeoPackage.create(target_path)
        self.assertTrue(exists(target_path))
        self.assertTrue(isfile(target_path))
        self.assertTrue(isinstance(gpkg, GeoPackage))
    # End test_create_gpkg method

    def test_gpkg_fcs(self):
        """
        Test the geopackage list fcs and get fcs
        """
        target_path, gpkg, srs, fields = self._setup_basics(
            'test_gpkg_funcs.gpkg')

        gpkg.create_feature_class('test_pnts', srs, fields=fields)
        gpkg.create_feature_class(
            'test_lines', srs, fields=fields,
            shape_type=GeometryType.linestring)
        gpkg.create_feature_class(
            'test_polys', srs, fields=fields,
            shape_type=GeometryType.polygon)

        fcs = gpkg.feature_classes
        self.assertEqual(len(fcs), 3)
        for fc in fcs:
            self.assertIsInstance(fc, GeoPkgFeatureClass)
            self.assertIsInstance(fc.srs, SRS)
            self.assertEqual(fc.srs.srs_id, 32623)

        fc = gpkg.get_feature_class('test_p')
        self.assertIsNone(fc)
        fc = gpkg.get_feature_class('test_polys')
        self.assertIsInstance(fc, GeoPkgFeatureClass)
        self.assertEqual(fc.name, 'test_polys')

        gpkg.delete_feature_class('test_polys')
        fc = gpkg.get_feature_class('test_polys')
        self.assertIsNone(fc)

        sql = "SELECT * FROM gpkg_geometry_columns " \
              "WHERE table_name = 'test_polys'"
        results = gpkg.execute_query(sql)
        self.assertFalse(results)

        sql = "SELECT * FROM gpkg_geometry_columns " \
              "WHERE table_name = 'test_pnts'"
        results = gpkg.execute_query(sql)
        self.assertTrue(results)
    # End test_gpkg_fcs method

    def test_create_point_fc(self):
        """
        Test create a feature class
        """
        target_path, gpkg, srs, fields = self._setup_basics(
            'test_create_point_fc.gpkg')

        table_name = 'test1'
        fc = gpkg.create_feature_class(table_name, srs, fields=fields)
        self.assertIsInstance(fc, GeoPkgFeatureClass)

        self.assertTrue(check_table_exists(target_path, table_name))
        self.assertTrue(check_ogr_trigger_exists(target_path, table_name))

        exp_contents = [u'test1', u'features', u'test1', u'',
                        None, None, None, None, 32623]
        tst_contents = list(get_table_rows(target_path, 'gpkg_contents')[0])
        # pop timestamp
        tst_contents.pop(4)
        self.assertEqual(exp_contents, tst_contents)

        exp_geom_col = [(u'test1', u'SHAPE', u'POINT', 32623, 0, 0)]
        self.assertEqual(exp_geom_col,
                         get_table_rows(target_path, 'gpkg_geometry_columns'))

        exp_srs = (u'WGS_1984_UTM_Zone_23N', 32623, u'EPSG', 32623,
                   WGS_1984_UTM_Zone_23N, u'')
        self.assertEqual(
            exp_srs, get_table_rows(target_path, 'gpkg_spatial_ref_sys')[-1])
        fld = Field('boooom', SQLFieldTypes.double)
        fc.add_field(fld)
        self.assertIn(fld.name, fc.field_names)

    # End test_create_point_fc method

    def test_create_line_fc(self):
        """
        Test create a feature class
        """
        target_path, gpkg, srs, fields = self._setup_basics(
            'test_create_line_fc.gpkg')

        fc = gpkg.create_feature_class(
            'test1', srs, fields=fields, shape_type=GeometryType.linestring)
        self.assertIsInstance(fc, GeoPkgFeatureClass)

        self.assertTrue(check_table_exists(target_path, 'test1'))

        exp_contents = [u'test1', u'features', u'test1', u'',
                        None, None, None, None, 32623]
        tst_contents = list(get_table_rows(target_path, 'gpkg_contents')[0])
        # pop timestamp
        tst_contents.pop(4)
        self.assertEqual(exp_contents, tst_contents)

        exp_geom_col = [(u'test1', u'SHAPE', u'LINESTRING', 32623, 0, 0)]
        self.assertEqual(exp_geom_col,
                         get_table_rows(target_path, 'gpkg_geometry_columns'))

        exp_srs = (u'WGS_1984_UTM_Zone_23N', 32623, u'EPSG', 32623,
                   WGS_1984_UTM_Zone_23N, u'')
        self.assertEqual(
            exp_srs, get_table_rows(target_path, 'gpkg_spatial_ref_sys')[-1])
    # End test_create_fc method

    def test_create_poly_fc(self):
        """
        Test create a feature class
        """
        target_path, gpkg, srs, fields = self._setup_basics(
            'test_create_poly_fc.gpkg')

        fc = gpkg.create_feature_class(
            'test1', srs, fields=fields, shape_type=GeometryType.polygon)
        self.assertIsInstance(fc, GeoPkgFeatureClass)
        self.assertTrue(check_table_exists(target_path, 'test1'))

        exp_contents = [u'test1', u'features', u'test1', u'',
                        None, None, None, None, 32623]
        tst_contents = list(get_table_rows(target_path, 'gpkg_contents')[0])
        # pop timestamp
        tst_contents.pop(4)
        self.assertEqual(exp_contents, tst_contents)

        exp_geom_col = [(u'test1', u'SHAPE', u'POLYGON', 32623, 0, 0)]
        self.assertEqual(exp_geom_col,
                         get_table_rows(target_path, 'gpkg_geometry_columns'))

        exp_srs = (u'WGS_1984_UTM_Zone_23N', 32623, u'EPSG', 32623,
                   WGS_1984_UTM_Zone_23N, u'')
        self.assertEqual(
            exp_srs, get_table_rows(target_path, 'gpkg_spatial_ref_sys')[-1])
        # NOTE - tests GeoPackage
        self.assertTrue(gpkg.table_exists('test1'))
    # End test_create_fc method

    def test_insert_point_rows(self):
        """
        Test Insert Point Rows
        """
        target_path, gpkg, srs, fields = self._setup_basics(
            'test_insert_points.gpkg')

        fc = gpkg.create_feature_class(
            'test1', srs, fields=fields, shape_type=GeometryType.point)

        self.assertIsInstance(fc, GeoPkgFeatureClass)
        rows = random_points_and_attrs(10000, srs.srs_id)
        field_names = ['SHAPE'] + [f.name for f in fields]
        # from time import clock
        # a = clock()
        fc.insert_rows(field_names, rows)
        # print 'Insert time: {0}s'.format(clock() - a)
        fc.extent = (300000, 1, 700000, 4000000)
        self.assertEqual((300000, 1, 700000, 4000000), fc.extent)
    # End test_insert_point_rows method

    def test_insert_point_rows_from_pkg(self):
        """
        Test Insert Point Rows
        """
        target_path, gpkg, srs, fields = self._setup_basics(
            'test_insert_points.gpkg')

        fc = gpkg.create_feature_class(
            'test1', srs, fields=fields, shape_type=GeometryType.point)

        self.assertIsInstance(fc, GeoPkgFeatureClass)
        rows = random_points_and_attrs(10000, srs.srs_id)
        field_names = ['SHAPE'] + [f.name for f in fields]
        # from time import clock
        # a = clock()
        gpkg.insert_rows('test1', field_names, rows)
        # print 'Insert time: {0}s'.format(clock() - a)
        results = fc.execute_query('SELECT * FROM test1 WHERE int_fld > 750')
        self.assertTrue(len(results) > 0)
    # End test_insert_point_rows method

    def test_create_table(self):
        """
        Test create a table

        :return:
        """
        target_path, gpkg, srs, fields = self._setup_basics(
            'test_create_table.gpkg')
        table_name = 'test1'
        tbl = gpkg.create_table(table_name, fields, 'wutevah')
        self.assertTrue(check_table_exists(target_path, table_name))
        self.assertTrue(check_ogr_trigger_exists(target_path, table_name))
        self.assertIsInstance(tbl, GeoPkgTable)
        exp_contents = [u'test1', u'attributes', u'test1', u'wutevah',
                        None, None, None, None, None]
        tst_contents = list(get_table_rows(target_path, 'gpkg_contents')[0])
        # pop timestamp
        tst_contents.pop(4)
        self.assertEqual(exp_contents, tst_contents)
        self.assertTrue(gpkg.table_exists('test1'))
    # End test_create_table

    def test_table_object(self):
        """
        Test create a table

        :return:
        """
        target_path, gpkg, srs, fields = self._setup_basics(
            'test_insert_rows.gpkg')
        tbl = gpkg.create_table('test1', fields, 'wutevah')
        self.assertIsInstance(tbl, GeoPkgTable)
        self.assertTrue(gpkg.table_exists('test1'))
        rows = random_attrs(1000)
        tbl.insert_rows(fields, rows)
        self.assertEqual(tbl.count, 1000)
    # End test_create_table

    def test_fc_object(self):
        """
        Test the props of the fc object
        :return:
        """
        target_path, gpkg, srs, fields = self._setup_basics(
            'test_insert_points.gpkg')

        fc = gpkg.create_feature_class(
            'test1', srs, fields=fields, shape_type=GeometryType.point)

        self.assertIsInstance(fc, GeoPkgFeatureClass)
        rows = random_points_and_attrs(1000, srs.srs_id)
        field_names = ['SHAPE'] + [f.name for f in fields]
        fc.insert_rows(field_names, rows)

        test_fields = fc.fields
        self.assertEqual(len(test_fields), 6)
        self.assertIsInstance(test_fields[0], Field)
        test_field_names = [f.name for f in test_fields]
        field_names = ['fid'] + field_names
        self.assertEqual(test_field_names, field_names)
        self.assertEqual(fc.count, 1000)

        shape_field = fc.shape_field
        self.assertEqual(shape_field.name, 'SHAPE')
        self.assertEqual(shape_field.data_type, 'POINT')
    # End test_fc_object

    def test_fc_object_from_full_path(self):
        """
        Test the props of the fc object
        :return:
        """
        target_path, gpkg, srs, fields = self._setup_basics(
            'test_insert_points2.gpkg')

        gpkg.create_feature_class(
            'test1', srs, fields=fields, shape_type=GeometryType.point)

        fc = GeoPkgFeatureClass(full_path=join(target_path, 'test1'))
        self.assertIsInstance(fc, GeoPkgFeatureClass)
        self.assertEqual(fc.name, 'test1')
        self.assertEqual(fc.full_path, join(target_path, 'test1'))

        field_names = ['SHAPE'] + [f.name for f in fields]
        test_fields = fc.fields
        self.assertEqual(len(test_fields), 6)
        self.assertIsInstance(test_fields[0], Field)
        test_field_names = [f.name for f in test_fields]
        field_names = ['fid'] + field_names
        self.assertEqual(test_field_names, field_names)
        self.assertEqual(fc.count, 0)
    # End test_fc_object

    def test_insert_polys(self):
        """
        Test create a feature class
        """
        target_path, gpkg, srs, fields = self._setup_basics(
            'test_insert_polys.gpkg')
        fc = gpkg.create_feature_class(
            'test1', srs, fields=fields, shape_type=GeometryType.polygon)

        # 32623
        rings = [[(300000, 1), (300000, 4000000), (700000, 4000000),
                  (700000, 1), (300000, 1)]]
        hdr = make_gpkg_geom_header(32623)
        gpkg_poly = point_lists_to_gpkg_polygon(hdr, rings)

        fc.insert_rows(['SHAPE'], [(gpkg_poly,)])
        self.assertEqual(fc.count, 1)
        fc.extent = (300000, 1, 700000, 4000000)
        self.assertEqual((300000, 1, 700000, 4000000), fc.extent)
    # End test_create_fc method

    def test_insert_polys_hole(self):
        """
        Test create a feature class
        """
        target_path, gpkg, srs, fields = self._setup_basics(
            'test_insert_polys_hole.gpkg')
        fc = gpkg.create_feature_class(
            'test1', srs, fields=fields, shape_type=GeometryType.polygon)

        # 32623
        rings = [[(300000.0, 1.0), (300000.0, 4000000.0),
                  (700000.0, 4000000.0), (700000.0, 1.0), (300000.0, 1.0)],
                 [(400000.0, 100000.0), (600000.0, 100000.0),
                  (600000.0, 3900000.0), (400000.0, 3900000),
                  (400000.0, 100000.0)]]
        hdr = make_gpkg_geom_header(32623)
        gpkg_poly = point_lists_to_gpkg_polygon(hdr, rings)

        fc.insert_rows(['SHAPE'], [(gpkg_poly,)])
        self.assertEqual(fc.count, 1)
    # End test_create_fc method

    def test_insert_multi_poly(self):
        """
        Test create a feature class with "multi polygons"
        """
        target_path, gpkg, srs, fields = self._setup_basics(
            'test_insert_multi_polys.gpkg')
        fc = gpkg.create_feature_class(
            'test1', srs, fields=fields, shape_type=GeometryType.multi_polygon)

        # 32623
        polys = [[[(300000.0, 1.0), (300000.0, 4000000.0),
                   (700000.0, 4000000.0), (700000.0, 1.0), (300000.0, 1.0)]],
                 [[(100000.0, 1000000.0), (100000.0, 2000000.0),
                   (200000.0, 2000000.0), (200000.0, 1000000.0),
                   (100000.0, 1000000.0)]]]
        hdr = make_gpkg_geom_header(32623)
        gpkg_poly = point_lists_to_gpkg_multi_polygon(hdr, polys)

        fc.insert_rows(['SHAPE'], [(gpkg_poly,)])
        self.assertEqual(fc.count, 1)
    # End test_insert_multi_poly method

    def test_insert_lines(self):
        """
        Test insert a line
        """
        target_path, gpkg, srs, fields = self._setup_basics(
            'test_insert_lines.gpkg')
        fc = gpkg.create_feature_class(
            'test1', srs, fields=fields, shape_type=GeometryType.linestring)

        # 32623
        line = [(300000, 1), (300000, 4000000), (700000, 4000000), (700000, 1)]
        hdr = make_gpkg_geom_header(32623)
        gpkg_line = points_to_gpkg_line_string(hdr, line)

        fc.insert_rows(['SHAPE'], [(gpkg_line,)])
        self.assertEqual(fc.count, 1)
    # End test_insert_lines method

    def test_insert_multi_point(self):
        """
        Test insert a multi point
        """
        target_path, gpkg, srs, fields = self._setup_basics(
            'test_insert_multi_points.gpkg')
        fc = gpkg.create_feature_class(
            'test1', srs, fields=fields, shape_type=GeometryType.multi_point)

        # 32623
        multipoints = [(300000, 1), (300000, 4000000)]
        hdr = make_gpkg_geom_header(32623)
        gpkg_mp = points_to_gpkg_multipoint(hdr, multipoints)

        fc.insert_rows(['SHAPE', 'int_fld'], [(gpkg_mp, 1)])
        self.assertEqual(fc.count, 1)

    # End test_insert_multi_point method

    def test_insert_lines_4326(self):
        """
        Test insert a line
        """
        target_path, gpkg, srs, fields = self._setup_basics(
            'test_insert_lines_4326.gpkg')
        srs = SRS('', 'ESRI', 4326, '')
        fc = gpkg.create_feature_class(
            'test1', srs, fields=fields, shape_type=GeometryType.linestring)

        # 32623
        line = [(10, 10), (10, 20), (20, 20), (20, 30)]
        hdr = make_gpkg_geom_header(4326)
        gpkg_line = points_to_gpkg_line_string(hdr, line)

        fc.insert_rows(['SHAPE'], [(gpkg_line,)])
        self.assertEqual(fc.count, 1)
    # End test_insert_lines method

    def test_insert_lines_z(self):
        """
        Test insert a line
        """
        target_path, gpkg, srs, fields = self._setup_basics(
            'test_insert_lines_z.gpkg')
        fc = gpkg.create_feature_class(
            'test1', srs, fields=fields, shape_type=GeometryType.linestring,
            z_enabled=True)

        # 32623
        line = [(300000, 1, 10), (300000, 4000000, 20), (700000, 4000000, 30),
                (700000, 1, 40)]
        hdr = make_gpkg_geom_header(32623)
        gpkg_line = points_z_to_gpkg_line_string_z(hdr, line)

        fc.insert_rows(['SHAPE'], [(gpkg_line,)])
        self.assertEqual(fc.count, 1)
    # End test_insert_lines method

    def test_insert_lines_m(self):
        """
        Test insert a line
        """
        target_path, gpkg, srs, fields = self._setup_basics(
            'test_insert_lines_m.gpkg')
        fc = gpkg.create_feature_class(
            'test1', srs, fields=fields, shape_type=GeometryType.linestring,
            m_enabled=True)

        # 32623
        line = [(300000, 1, 10), (300000, 4000000, 20), (700000, 4000000, 30),
                (700000, 1, 40)]
        hdr = make_gpkg_geom_header(32623)
        gpkg_line = points_m_to_gpkg_line_string_m(hdr, line)

        fc.insert_rows(['SHAPE'], [(gpkg_line,)])
        self.assertEqual(fc.count, 1)
    # End test_insert_lines method

    def test_insert_lines_zm(self):
        """
        Test insert a line
        """
        target_path, gpkg, srs, fields = self._setup_basics(
            'test_insert_lines_zm.gpkg')
        fc = gpkg.create_feature_class(
            'test1', srs, fields=fields, shape_type=GeometryType.linestring,
            z_enabled=True, m_enabled=True)

        # 32623
        line = [(300000, 1, 10, 0), (300000, 4000000, 20, 1000),
                (700000, 4000000, 30, 2000), (700000, 1, 40, 3000)]
        hdr = make_gpkg_geom_header(32623)
        gpkg_line = points_zm_to_gpkg_line_string_zm(hdr, line)

        fc.insert_rows(['SHAPE'], [(gpkg_line,)])
        self.assertEqual(fc.count, 1)
    # End test_insert_lines method

    def test_insert_multi_lines(self):
        """
        Test insert multi lines
        """
        target_path, gpkg, srs, fields = self._setup_basics(
            'test_insert_multi_lines.gpkg')
        fc = gpkg.create_feature_class(
            'test1', srs, fields=fields,
            shape_type=GeometryType.multi_linestring,
            z_enabled=True, m_enabled=True)
        line = [[(300000.0, 1.0), (300000.0, 4000000.0),
                 (700000.0, 4000000.0), (700000.0, 1.0)],
                [(600000.0, 100000.0),
                 (600000.0, 3900000.0), (400000.0, 3900000),
                 (400000.0, 100000.0)]]
        hdr = make_gpkg_geom_header(32623)
        gpk_multi_line = point_lists_to_gpkg_multi_line_string(hdr, line)
        fc.insert_rows(['SHAPE'], [(gpk_multi_line,)])
        self.assertEqual(fc.count, 1)
        self.assertEqual('SHAPE', fc.shape_field_name)
    # End test_insert_multi_lines method
# End TestGeoPackage class


if __name__ == '__main__':
    pass
