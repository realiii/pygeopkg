"""
Geo Package Class
"""


from sys import version_info
from datetime import datetime
from os import remove
from os.path import exists, dirname, basename, join
from pygeopkg.core.field import Field
from pygeopkg.core.utils import (
    connection_execute, insert_table_rows, get_table_count,
    connection_execute_many, create_gpkg_from_sql)
from pygeopkg.shared.enumeration import (
    GeometryType, DataType, SQLFieldTypes, GeoPackageCoreTableNames,
    GPKGFLavors, GEOMETRY_FIELD_TYPES)
from pygeopkg.shared.messages import (
    ERR_DATASET_NO_EXIST, ERR_PROVIDE_PARAMS_FC, ERR_TABLE_EXISTS)
from pygeopkg.shared.sql import (
    CREATE_FEATURE_TABLE, GPKG_OGR_CONTENTS_DELETE_TRIGGER,
    GPKG_OGR_CONTENTS_INSERT_TRIGGER, INSERT_GPKG_CONTENTS_SHORT,
    INSERT_GPKG_CONTENTS, INSERT_GPKG_OGR_CONTENTS, INSERT_GPKG_SRS,
    INSERT_GPKG_GEOM_COL, TABLE_EXISTS, PRAGMA_TABLE_INFO,
    CREATE_NON_SPATIAL_TABLE, CHECK_SRS_EXISTS, GET_TABLE_NAMES_BY_TYPE,
    GET_TABLE_NAME_BY_TYPE, DELETE_FROM_TABLE_BY_NAME, DROP_TABLE, ADD_COLUMN,
    SELECT_SRS_BY_TABLE_NAME, UPDATE_CONTENTS_EXTENT, GET_FC_EXTENT)
from pygeopkg.shared.constants import COMMA, COMMA_SPACE, SHAPE, GPKG_EXT
from pygeopkg.core.srs import SRS


if version_info > (3,):
    # noinspection PyShadowingBuiltins
    unicode = str


class GeoPackage(object):
    """
    GeoPackage class
    """
    def __init__(self, full_path):
        """
        Init

        :param full_path: Full path to the geopackage sqlite db
        :type full_path: str
        """
        self.full_path = full_path
    # End __init_ builtin method

    def _add_row_to_gpkg_contents(
            self, table_name, srs_id=None, data_type=DataType.features,
            description='', min_x=None, min_y=None, max_x=None, max_y=None):
        """
        Add a row to the gpkg_contents table

        :param table_name: The table name
        :type table_name: str
        :param srs_id: The SRS id
        :param data_type: The data_type
        :param description: Description of the feature class
        :param min_x: min x
        :param min_y: min y
        :param max_x: max x
        :param max_y: max y
        """
        time_stamp = self.get_now()
        sql = INSERT_GPKG_CONTENTS
        values = (table_name, data_type, table_name, description, time_stamp,
                  min_x, min_y, max_x, max_y, srs_id)
        if None in (min_x, min_y, max_x, max_y):
            sql = INSERT_GPKG_CONTENTS_SHORT
            values = (table_name, data_type, table_name, description,
                      time_stamp, srs_id)
        connection_execute(self.full_path, sql, values)
    # End _add_row_to_gpkg_contents method

    def _add_row_to_gpkg_ogr_contents(self, table_name):
        """
        Add a row to the gpkg_ogr_contents table

        :param table_name: The table name
        :type table_name: str
        """
        sql = INSERT_GPKG_OGR_CONTENTS
        connection_execute(self.full_path, sql, (table_name, 0))
    # End _add_row_to_gpkg_ogr_contents method

    def _add_gpkg_ogr_contents_triggers(self, table_name):
        """
        Add triggers for gpkg_ogr_contents

        :param table_name: The table name
        :type table_name: str
        """
        names = table_name, table_name, table_name
        sql = GPKG_OGR_CONTENTS_INSERT_TRIGGER
        connection_execute(self.full_path, sql % names)
        sql = GPKG_OGR_CONTENTS_DELETE_TRIGGER
        connection_execute(self.full_path, sql % names)
    # End _add_gpkg_ogr_contents_triggers method

    def _add_row_to_gpkg_geom_columns(
            self, table_name, geometry_type, srs_id, z_enabled, m_enabled):
        """
        Add a row to the geopackage geom columns table

        :param table_name: The name of the table
        :type table_name: str
        :param geometry_type: The geometry type
        :type geometry_type: str
        :param srs_id: The SRS id
        :type srs_id: int
        :param z_enabled: The z value
        :type z_enabled: bool
        :param m_enabled: The m value
        :type m_enabled: bool
        """
        z_enabled = 1 if z_enabled else 0
        m_enabled = 1 if m_enabled else 0
        values = (table_name, SHAPE, geometry_type, srs_id, z_enabled,
                  m_enabled)
        connection_execute(self.full_path, INSERT_GPKG_GEOM_COL, values)
    # End _add_row_to_gpkg_geom_columns method

    def _add_row_to_gpkg_srs(self, srs_obj):
        """
        Add a row to the geopackage srs table

        :param srs_obj: The SRS object
        :type srs_obj: SRS
        """
        if self.check_srs_exists(srs_obj.srs_id):
            return
        connection_execute(self.full_path, INSERT_GPKG_SRS, srs_obj.row)
    # End _add_row_to_gpkg_srs method

    def check_srs_exists(self, srs_id):
        """
        Check if a SRS already exists in the table.  This is done purely by
        srs id because thats all ESRI looks at.

        :param srs_id: The spatial reference ID
        :type srs_id: int
        :return: boolean indicating existence
        :rtype: bool
        """
        sql = CHECK_SRS_EXISTS.format(srs_id)
        results = connection_execute(self.full_path, sql)
        return len(results) > 0
    # End check_srs_exists method

    @classmethod
    def create(cls, target_path, flavor=GPKGFLavors.esri):
        """
        Create a new GeoPackage.  Note that this method overwrites anything
        that might already exist.

        :param target_path: The full path for the new geopackage
        :type target_path: str
        :param flavor: definition to use for the default WGS 84
         SRS defined in the SRS table. Options are ESRI or EPSG.  Note that ESRI
         will view definition of WGS 84 not in its particular style as "custom".
        :return: A new empty GeoPackage
        :rtype: GeoPackage
        """
        if exists(target_path):
            remove(target_path)
        create_gpkg_from_sql(target_path, flavor)
        return cls(target_path)
    # End create method

    def create_feature_class(
            self, name, srs, shape_type=GeometryType.point,
            z_enabled=False, m_enabled=False, fields=None, description=''):
        """
        Creates a feature class in the GeoPackage per the options given.

        :param name: Name of the table.
        :type name: str
        :param shape_type: Shape type
        :type shape_type: str
        :param z_enabled: boolean indicating z
        :type z_enabled: bool
        :param m_enabled: boolean indicating m
        :type m_enabled: bool
        :param fields: list of Field objects
        :type fields: list or tuple
        :param description: the description
        :type description: str
        :param srs: the spatial reference system
        :type srs: SRS
        :return: GeoPkgFeatureClass
        :rtype: GeoPkgFeatureClass
        """
        if not fields:
            fields = []
        if self.table_exists(name):
            raise ValueError(ERR_TABLE_EXISTS.format(name))
        self._create_feature_table(name, shape_type, fields)
        self._add_row_to_gpkg_srs(srs)
        self._add_row_to_gpkg_geom_columns(
            name, shape_type, srs.srs_id, z_enabled, m_enabled)
        self._add_row_to_gpkg_contents(
            name, srs.srs_id, description=description)
        self._add_row_to_gpkg_ogr_contents(name)
        self._add_gpkg_ogr_contents_triggers(name)
        return GeoPkgFeatureClass(geopackage=self, name=name)
    # End create_feature_class method

    def _create_feature_table(self, table_name, shape_type, fields):
        """
        Create a Feature Table

        :param table_name: The table name
        :type table_name: str
        :param shape_type: The Shape Type
        :type shape_type: str
        :param fields: The fields
        :type fields: list of Field
        """
        cols = COMMA + COMMA_SPACE.join([unicode(field) for field in fields])
        if not fields:
            cols = ''
        sql = CREATE_FEATURE_TABLE.format(
            name=table_name,  feature_type=shape_type, other_fields=cols)
        connection_execute(self.full_path, sql)
    # End _create_feature_table method

    def create_table(self, name, fields, description=''):
        """
        Create a regular non-spatial table in the geopackage

        :param name: Name of the table.
        :type name: str
        :param fields: list of Field objects
        :type fields: list or tuple
        :param description: the description
        :type description: str
        :return: GeoPkgTable
        :rtype: GeoPkgTable
        """
        if self.table_exists(name):
            raise ValueError(ERR_TABLE_EXISTS.format())
        self._create_nonspatial_table(name, fields)
        self._add_row_to_gpkg_contents(
            name, data_type=DataType.attributes, description=description)
        return GeoPkgTable(geopackage=self, name=name)
    # End create_table method

    def _create_nonspatial_table(self, table_name, fields):
        """
        Create non spatial table

        :param table_name: the table name
        :type table_name: str
        :param fields: the list of fields
        :type fields: list of Field
        """
        cols = COMMA_SPACE.join([unicode(field) for field in fields])
        sql = CREATE_NON_SPATIAL_TABLE.format(
            name=table_name,  other_fields=cols)
        connection_execute(self.full_path, sql)
    # End _create_nonspatial_table method

    def delete_feature_class(self, name):
        """
        Delete a Feature Class

        :param name: The name of the feature class to delete
        :type name: str
        """
        if not self.feature_class_exists(name):
            return
        delete_geom_col_table = DELETE_FROM_TABLE_BY_NAME.format(
            gpkg_table=GeoPackageCoreTableNames.gpkg_geometry_columns,
            table_name=name)
        delete_contents_table = DELETE_FROM_TABLE_BY_NAME.format(
            gpkg_table=GeoPackageCoreTableNames.gpkg_contents,
            table_name=name)
        drop_table = DROP_TABLE.format(table_name=name)
        connection_execute(self.full_path, drop_table)
        connection_execute(self.full_path, delete_contents_table)
        connection_execute(self.full_path, delete_geom_col_table)
    # End delete_feature_class method

    @staticmethod
    def get_now():
        """
        Get now

        :return: the current time stamp string
        :rtype: str
        """
        return datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    # End get_now method

    def insert_rows(self, dataset_name, field_names, data):
        """
        Insert Rows into a Table

        :param dataset_name: the name of the dataset to work with
        :type dataset_name: str
        :param field_names: the name of the fields
        :type field_names: list or tuple
        :param data: the data
        :type data: list, tuple
        """
        if not self.table_exists(dataset_name):
            raise ValueError(ERR_DATASET_NO_EXIST)
        insert_table_rows(self.full_path, dataset_name, field_names, data)
    # End insert_rows method

    @property
    def feature_classes(self):
        """
        Returns a list with all the feature classes in the GeoPackage

        :return: a list of feature classes in the GeoPackage
        :rtype: list of GeoPkgFeatureClass
        """
        sql = GET_TABLE_NAMES_BY_TYPE.format(data_type=DataType.features)
        results = connection_execute(self.full_path, sql)
        output = []
        for fc in results:
            output.append(GeoPkgFeatureClass(geopackage=self, name=fc[0]))
        return output
    # End feature_classes property

    def get_feature_class(self, name):
        """
        Get a Feature Class By Name

        :param name: feature class name to look for
        :type name: str
        :return: A GeoPkgFeatureClass or None
        :rtype: GeoPkgFeatureClass
        """
        if not self.feature_class_exists(name):
            return None
        return GeoPkgFeatureClass(geopackage=self, name=name)
    # End get_feature_class method

    def feature_class_exists(self, name):
        """
        Check if a feature class exists

        :param name: Name to check for existence
        :type name: str
        :return: boolean indicating existence
        :rtype: bool
        """
        sql = GET_TABLE_NAME_BY_TYPE.format(
            table_name=name, data_type=DataType.features)
        results = connection_execute(self.full_path, sql)
        if not results:
            return False
        return True
    # End feature_class_exists method

    def get_feature_class_srs(self, name):
        """
        Get the Feature Class SRS

        :param name: The name of the feature class to check
        :type name: str
        :return: The feature class SRS
        :rtype: SRS
        """
        sql = SELECT_SRS_BY_TABLE_NAME.format(name)
        result = self.execute_query(sql)
        if not result:
            return None
        _, srs_name, org, org_srs_id, definition, description = result[0]
        return SRS(srs_name, org, org_srs_id, definition, description)
    # End get_feature_class_srs method

    def table_exists(self, table_name):
        """
        Check existence of table

        :param table_name: Table name
        :type table_name: str
        :return: bool if the table exists
        :rtype: bool
        """
        out = connection_execute(
            self.full_path, TABLE_EXISTS.format(table_name=table_name))
        return len(out) > 0
    # End check_table_exists

    def execute_query(self, sql, values=None):
        """
        Execute Query against the Table or Feature Class

        :param sql: the sql to execute
        :type sql: str
        :param values: the values to use
        :return: The results of the query
        :rtype: list
        """
        return connection_execute(self.full_path, sql, values)
    # End execute_query method

    def execute_many_query(self, sql, values=None):
        """
        Execute Many Query against the Table or Feature Class

        :param sql: the sql to execute
        :type sql: str
        :param values: the values to use
        :return: The results of the query
        :rtype: list
        """
        return connection_execute_many(self.full_path, sql, values)
    # End execute_query method
# End GeoPackage class


class BaseGeoPkgTable(object):
    """
    Base Geopackage Table
    """
    def __init__(self, geopackage=None, name='', full_path=''):
        """
        Initialize the GeoPkgFeatureClass class

        :param geopackage: The geopackage
        :type geopackage: GeoPackage
        :param name: the name of the table/fc
        :type name: str
        :param full_path: Full path to the table (optional alternative)
        """
        super(BaseGeoPkgTable, self).__init__()
        if not any([geopackage, name, full_path]):
            raise ValueError(ERR_PROVIDE_PARAMS_FC)
        if full_path and dirname(full_path).lower().endswith(GPKG_EXT):
            self.geopackage = GeoPackage(dirname(full_path))
            self.name = basename(full_path)
            self.full_path = full_path
        elif isinstance(geopackage, GeoPackage) and name:
            self.geopackage = geopackage
            self.name = name
            self.full_path = join(geopackage.full_path, name)
        else:
            raise ValueError(ERR_PROVIDE_PARAMS_FC)
    # End init built-in

    def add_field(self, field):
        """
        Add a field (column) to a table / feature class

        :param field: The field to add
        :type field: Field
        """
        if field.name in self.field_names:
            raise ValueError('Field already exists!')
        sql = ADD_COLUMN.format(
            table_name=self.name, column_name_type=str(field))
        connection_execute(self.geopackage.full_path, sql)
    # End add_field method

    def insert_rows(self, field_names, data):
        """
        Insert Rows into a Table

        :param field_names: the name of the fields
        :type field_names: list or tuple
        :param data: the data
        :type data: list, tuple
        """
        if not field_names:
            return
        if isinstance(field_names[0], Field):
            field_names = [f.name for f in field_names]
        insert_table_rows(
            self.geopackage.full_path, self.name, field_names, data)
    # End insert_rows method

    @property
    def fields(self):
        """
        Fields for the table

        :return: List of fields
        :rtype: list of Field
        """
        sql = PRAGMA_TABLE_INFO.format(table_name=self.name)
        out = connection_execute(self.geopackage.full_path, sql)
        fields = []
        for _, name, type_, _, _, _ in out:
            size = None
            if type_.startswith(SQLFieldTypes.text) and len(type_) > 4:
                size = int(type_[4:])
                type_ = SQLFieldTypes.text
            fields.append(Field(name, type_, size=size))
        return fields
    # End fields property

    @property
    def field_names(self):
        """
        Field Names

        :return: List of field names
        :rtype: list of str
        """
        return [f.name for f in self.fields]
    # End field_names property

    @property
    def count(self):
        """
        Row count

        :return: The row count
        :rtype: int
        """
        return get_table_count(self.geopackage.full_path, self.name)
    # End count property

    def execute_query(self, sql, values=None):
        """
        Execute Query against the Table or Feature Class

        :param sql: the sql to execute
        :type sql: str
        :param values: the values to use
        :return: The results of the query
        :rtype: list
        """
        return connection_execute(self.geopackage.full_path, sql, values)
    # End execute_query method

    def execute_many_query(self, sql, values=None):
        """
        Execute Many Query against the Table or Feature Class

        :param sql: the sql to execute
        :type sql: str
        :param values: the values to use
        :return: The results of the query
        :rtype: list
        """
        return connection_execute_many(self.geopackage.full_path, sql, values)
    # End execute_query method
# End BaseGeoPkgTable class


class GeoPkgTable(BaseGeoPkgTable):
    """
    GeoPackage Non-Spatial Table
    """
    pass
# End GeoPkgTable class


class GeoPkgFeatureClass(BaseGeoPkgTable):
    """
    GeoPackage Feature Class
    """
    @property
    def extent(self):
        """
        Extent property

        :return: Returns the extent (min_x, min_y, max_x, max_y)
        :rtype: tuple
        """
        result = self.execute_query(GET_FC_EXTENT.format(table_name=self.name))
        if not result:
            return None
        return result[0]

    @extent.setter
    def extent(self, value):
        """
        Sets the extent for the feature class.  Writes given tuple of
        values into the gpkg_contents table.

        :param value:
        :type value: tuple or list
        """
        if not isinstance(value, (tuple, list)):
            raise ValueError('Please supply a tuple or list of values')
        if not len(value) == 4:
            raise ValueError('The tuple/list of values must have four values')
        value = tuple(value) + (self.name,)

        self.execute_query(UPDATE_CONTENTS_EXTENT, value)
    # End extent property

    @property
    def shape_field(self):
        """
        Shape Field

        :return: The shape field
        :rtype: Field
        """
        for field in self.fields:
            if field.data_type in GEOMETRY_FIELD_TYPES:
                return field
        return None
    # End shape_field property

    @property
    def shape_field_name(self):
        """
        Shape Field Name

        :return: the name of the shape field
        :rtype: str
        """
        if self.shape_field:
            return self.shape_field.name
        return
    # End shape_field_name property

    @property
    def srs(self):
        """
        Spatial Reference Object

        :return: the spatial reference of the feature class
        :rtype: SRS
        """
        return self.geopackage.get_feature_class_srs(self.name)
    # End srs property
    spatial_reference = srs
# End GeoPkgFeatureClass class


if __name__ == '__main__':
    pass
