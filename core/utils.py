"""
Utilities
"""
from os.path import exists, dirname
from sqlite3 import connect
from pygeopkg.resources.gpkg_sql import (
    ORDERED_GPKG_SQL, DEFAULT_ESRI_RECS, DEFAULT_EPSG_RECS)
from pygeopkg.shared.constants import COMMA_SPACE, Q_MARK
from pygeopkg.shared.enumeration import GPKGFLavors
from pygeopkg.shared.messages import ERR_DIMENSION_NO_MATCH
from pygeopkg.shared.sql import INSERT_TO_TABLE, SQL_COUNT, INSERT_GPKG_SRS


def connection_execute(db_path, sql, values=None):
    """
    Connection Execute

    :param db_path: The path to the geopackage
    :type db_path: str
    :param sql: The sql to execute
    :type sql: str
    :param values: The values to use with the sql
    :return: The results if any
    :rtype: list
    """
    with connect(db_path, isolation_level='EXCLUSIVE') as conn:
        if values:
            result = conn.execute(sql, values)
        else:
            result = conn.execute(sql)
        return result.fetchall()
# End connection_execute function


def connection_execute_many(db_path, sql, values):
    """
    Run Execute Many into the sqlite database

    :param db_path: The path to the geopackage
    :type db_path: str
    :param sql: The sql to execute
    :type sql: str
    :param values: The values to use with the sql
    """
    with connect(db_path, isolation_level='EXCLUSIVE') as conn:
        conn.executemany(sql, values)
# End connection_execute_many function


def get_table_count(db_path, table_name):
    """
    Get a tables row count

    :param db_path: The path to the geopackage
    :type db_path: str
    :param table_name: The name of the table
    :type table_name: str
    :return: Returns the count
    :rtype: int
    """
    result = connection_execute(
        db_path, SQL_COUNT.format(table_name=table_name))
    return result[0][0]
# End get_table_count function


def insert_table_rows(database_path, dataset_name, field_names, data):
    """
    Insert Many Table Rows to a Geopackage

    :param database_path: The path to the geopackage
    :type database_path: str
    :param dataset_name: The name of the dataset
    :type dataset_name: str
    :param field_names: List of field names involved
    :type field_names: list
    :param data: The data to use
    :type data: list or tuple
    :return:
    """
    if not field_names or not data:
        return
    test_row = data[0]
    if len(test_row) != len(field_names):
        raise ValueError(ERR_DIMENSION_NO_MATCH)
    q_marks = COMMA_SPACE.join([Q_MARK for _ in field_names])
    field_names = COMMA_SPACE.join(field_names)
    sql = INSERT_TO_TABLE.format(
        table_name=dataset_name, field_names=field_names, q_marks=q_marks)
    connection_execute_many(database_path, sql, data)
# End insert_table_rows function


def create_gpkg_from_sql(db_path, flavor=GPKGFLavors.esri):
    """
    Create gpkg from raw sql

    :param db_path: The path to the geopackage
    :type db_path: str
    :param flavor: The flavor to use for the default WKT
    :type flavor: str
    """
    if not exists(dirname(db_path)):
        raise ValueError('Containing folder of target location does not exist')
    if exists(db_path):
        raise ValueError('Target database already exists')
    with connect(db_path) as conn:
        for sql in ORDERED_GPKG_SQL:
            conn.execute(sql)
    default_srs_records = DEFAULT_ESRI_RECS
    if flavor == GPKGFLavors.epsg:
        default_srs_records = DEFAULT_EPSG_RECS
    connection_execute_many(db_path, INSERT_GPKG_SRS, default_srs_records)
# End create_gpkg_from_sql function


if __name__ == '__main__':
    pass
