"""
Enums
"""


class GPKGFLavors(object):
    """
    Geopackage Flavors mostly meaning which default srs definitions to use.
    Basically which 4326 definition to insert into the SRS table to start with.
    """
    esri = 'ESRI'
    epsg = 'EPSG'
# End GPKGFLavors class


class DataType(object):
    """
    Allowed Data Type values
    """
    features = 'features'
    attributes = 'attributes'
    tiles = 'tiles'
# End DataType class


class GeometryType(object):
    """
    Allowed Geometry Type values
    """
    point = 'POINT'
    linestring = 'LINESTRING'
    polygon = 'POLYGON'
    multi_point = 'MULTIPOINT'
    multi_linestring = 'MULTILINESTRING'
    multi_polygon = 'MULTIPOLYGON'
# End GeometryType class


class SQLFieldTypes(object):
    """
    SQL Field Types
    """
    boolean = 'BOOLEAN'
    tinyint = 'TINYINT'
    smallint = 'SMALLINT'
    mediumint = 'MEDIUMINT'
    integer = 'INTEGER'
    float = 'FLOAT'
    double = 'DOUBLE'
    real = 'REAL'
    text = 'TEXT'
    blob = 'BLOB'
    date = 'DATE'
    datetime = 'DATETIME'
    point = GeometryType.point
    linestring = GeometryType.linestring
    polygon = GeometryType.polygon
    multi_point = GeometryType.multi_point
    multi_linestring = GeometryType.multi_linestring
    multi_polygon = GeometryType.multi_polygon
# End SQLFieldTypes class


GEOMETRY_FIELD_TYPES = (
    SQLFieldTypes.point, SQLFieldTypes.linestring, SQLFieldTypes.polygon,
    SQLFieldTypes.multi_point, SQLFieldTypes.multi_linestring,
    SQLFieldTypes.multi_polygon)


class GeoPackageCoreTableNames(object):
    """
    Geopackage core table names
    """
    gpkg_contents = 'gpkg_contents'
    gpkg_extensions = 'gpkg_extensions'
    gpkg_geometry_columns = 'gpkg_geometry_columns'
    gpkg_spatial_ref_sys = 'gpkg_spatial_ref_sys'
    gpkg_tile_matrix = 'gpkg_tile_matrix'
    gpkg_tile_matrix_set = 'gpkg_tile_matrix_set'
# End GeoPackageCoreTableNames class


if __name__ == '__main__':
    pass
