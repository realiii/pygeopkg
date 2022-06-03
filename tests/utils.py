"""
Test Utilities
"""
from datetime import datetime, timedelta
from sys import version_info
from sqlite3 import connect
from random import randint, choice
from struct import pack
from string import ascii_uppercase, digits
from pygeopkg.conversion.to_geopkg_geom import GP_MAGIC


if version_info > (3,):
    # noinspection PyShadowingBuiltins
    buffer = bytes


def get_table_count(database, table_name):
    """
    Get a tables row count
    """
    with connect(database) as conn:
        result = conn.execute('SELECT COUNT(*) FROM {0}'.format(table_name))
        out = result.fetchone()
    return out[0]
# End get_table_count function


def get_table_rows(database, table_name):
    """
    Get table rows

    :param database:
    :param table_name:
    :return:
    """
    with connect(database) as conn:
        result = conn.execute('SELECT * FROM {0}'.format(table_name))
        out = result.fetchall()
    return out
# End get_table_rows function


def check_table_exists(database, table_name):
    """
    Check existence of table
    """
    return _check_object_name(database, 'table', table_name)
# End check_table_exists function


def check_ogr_trigger_exists(database, table_name):
    """
    Check existence of triggers for OGR
    """
    insert = 'trigger_insert_feature_count_%s' % table_name
    delete = 'trigger_delete_feature_count_%s' % table_name
    has_insert = _check_object_name(database, 'trigger', insert)
    has_delete = _check_object_name(database, 'trigger', delete)
    return has_insert and has_delete
# End check_ogr_trigger_exists function


def _check_object_name(database, type_, name):
    with connect(database) as conn:
        result = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='{type_}' "
            "AND name='{name}'".format(type_=type_, name=name))
        out = result.fetchall()
    return bool(out)
# End _check_object_name function


def random_attrs(count):
    """
    Generate Random Points and attrs (Use some UTM Zone)

    :param count:
    :return:
    """
    rows = []
    start = datetime.now()
    for _ in range(count):
        rand_str = ''.join(choice(ascii_uppercase + digits) for _ in range(10))
        rand_bool = True if randint(0, 1) else False
        rand_int = randint(0, 1000)
        rand_date = start + timedelta(days=rand_int - 500)
        rows.append((rand_int, rand_str, rand_str, rand_bool, rand_date))
    return rows
# End random_points_and_attrs function


def random_points_and_attrs(count, srs_id):
    """
    Generate Random Points and attrs (Use some UTM Zone)

    :param count:
    :param srs_id:
    :return:
    """
    points = generate_utm_points_as_wkb(count, srs_id)
    rows = []
    start = datetime.now()
    for p in points:
        rand_str = ''.join(choice(ascii_uppercase + digits) for _ in range(10))
        rand_bool = True if randint(0, 1) else False
        rand_int = randint(0, 1000)
        rand_date = start + timedelta(days=rand_int - 500)
        rows.append((p, rand_int, rand_str, rand_str, rand_bool, rand_date))
    return rows
# End random_points_and_attrs function


def generate_utm_points_as_wkb(count, srs_id):
    """
    Generate UTM points in the boundaries of the UTM coordinate space

    :param count: Number of points to generate
    :param srs_id: The spatial refernce ID
    :return:
    """
    magic, version, flags = GP_MAGIC, 0, 1
    header = pack('2s2bi', magic, version, flags, srs_id)

    eastings = [randint(300000, 700000) for _ in range(count)]
    northings = [randint(0, 4000000) for _ in range(count)]

    prefix = pack('<Bi', 1, 1)
    return [buffer(header + prefix + pack('<2d', easting, northing))
            for easting, northing in zip(eastings, northings)]
# End generate_utm_points function


if __name__ == '__main__':
    pass
