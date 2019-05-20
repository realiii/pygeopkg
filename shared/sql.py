"""
SQL Constants
"""

INSERT_GPKG_CONTENTS = (
    """INSERT INTO gpkg_contents (table_name, data_type, identifier, """
    """description, last_change, min_x, min_y, max_x, max_y, srs_id) """
    """VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
)

INSERT_GPKG_CONTENTS_SHORT = (
    """INSERT INTO gpkg_contents (table_name, data_type, identifier, """
    """description, last_change, srs_id) VALUES (?, ?, ?, ?, ?, ?)"""
)

INSERT_GPKG_GEOM_COL = (
    """INSERT INTO gpkg_geometry_columns (table_name, column_name, """
    """geometry_type_name, srs_id, z, m) """
    """VALUES (?, ?, ?, ?, ?, ?)"""
)

CREATE_FEATURE_TABLE = (
    """CREATE TABLE {name} ("""
    """fid INTEGER not null """
    """primary key autoincrement, """
    """SHAPE {feature_type}{other_fields})"""
)


CREATE_NON_SPATIAL_TABLE = (
    """CREATE TABLE {name} ("""
    """fid INTEGER not null """
    """primary key autoincrement, """ 
    """{other_fields})"""
)

INSERT_GPKG_SRS = (
    """INSERT INTO gpkg_spatial_ref_sys (srs_name, srs_id, organization, """
    """organization_coordsys_id, definition, description) """ 
    """VALUES (?, ?, ?, ?, ?, ?)"""
)

INSERT_TO_TABLE = (
    """INSERT INTO {table_name}({field_names}) VALUES ({q_marks})""")

TABLE_EXISTS = (
    "SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")

PRAGMA_TABLE_INFO = "PRAGMA table_info({table_name})"

SQL_COUNT = 'SELECT COUNT(*) FROM {table_name}'

CHECK_SRS_EXISTS = "SELECT srs_id FROM gpkg_spatial_ref_sys WHERE srs_id = {0}"

GET_TABLE_NAMES_BY_TYPE = (
    """SELECT table_name FROM gpkg_contents WHERE data_type = '{data_type}'""")

GET_TABLE_NAME_BY_TYPE = (
    """SELECT table_name FROM gpkg_contents WHERE data_type = '{data_type}' """
    """AND table_name = '{table_name}'"""
)

DELETE_FROM_TABLE_BY_NAME = (
    """DELETE FROM {gpkg_table} WHERE table_name = '{table_name}'""")

DROP_TABLE = """DROP TABLE {table_name}"""

ADD_COLUMN = (
    """ALTER TABLE {table_name} ADD COLUMN {column_name_type}""")

SELECT_SRS_BY_TABLE_NAME = (
"""
SELECT
       gpkg_contents.table_name,
       gpkg_spatial_ref_sys.srs_name,
       gpkg_spatial_ref_sys.organization,
       gpkg_spatial_ref_sys.organization_coordsys_id,
       gpkg_spatial_ref_sys.definition,
       gpkg_spatial_ref_sys.description
FROM gpkg_contents
       LEFT JOIN gpkg_spatial_ref_sys ON gpkg_contents.srs_id = gpkg_spatial_ref_sys.srs_id
WHERE gpkg_contents.table_name = '{0}'
"""
)

UPDATE_CONTENTS_EXTENT = (
    """
    UPDATE gpkg_contents 
    SET min_x=?, min_y=?, max_x=?, max_y=? 
    WHERE table_name = ?
    """)

GET_FC_EXTENT = (
    """
    SELECT min_x, min_y, max_x, max_y 
    FROM gpkg_contents 
    WHERE table_name = '{table_name}'
    """)


if __name__ == '__main__':
    pass
