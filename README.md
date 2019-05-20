# pygeopkg

pygeopkg is a Python 2/3 compatible library that allows for the creation and
population of (write to) an OGC GeoPackage database.  For more details on
GeoPackages please see the [OGC web page](http://www.geopackage.org/).

## Installation

pygeopkg was created to work as a packaged sub-respository in a larger
python library. As such users should simply add this repository as
a sub repository (via git) to their main repository or download the files and
add them to their projects as they see fit.

## Usage

pygeopkg can be used to create a new empty GeoPackage from scratch,
create new Feature Classes within a GeoPackage and populate the
feature class with geometry and attributes.


### Create an empty GeoPackage

```python
from pygeopkg.core.geopkg import GeoPackage

# Creates an empty geopackage
gpkg = GeoPackage.create(r'c:\temp\test.gpkg')
```

Geopackages are created with three default spatial references defined
automatically, a pair of spatial references to handle undefined cases
and a WGS 84 entry.  The definition of the WGS84 entry if flexible
meaning that the WKT for WGS84 can be setup per the users liking. In
our case that means either using the EPSG WKT or the ESRI WKT. By
default the ESRI WKT is used however if EPSG WKT is desired you
may provide a "flavor" parameter to the create method specifying EPSG.

```
# Creates an empty geopackage
gpkg = GeoPackage.create(r'c:\temp\test.gpkg', flavor='EPSG')
```


### Create a new Feature Class

To create a new Feature Class in the empty GeoPackage you will need
to tell the GeoPackage the Spatial Reference of the Feature Class
and the schema (fields) the Feature Class will have.

A feature class can be created with Z or M (or both) enabled. If 
either of these options are enabled the geometry inserted into the 
feature class MUST include a value for the option specified.

```python
from pygeopkg.core.geopkg import GeoPackage
from pygeopkg.core.srs import SRS
from pygeopkg.core.field import Field
from pygeopkg.shared.enumeration import GeometryType, SQLFieldTypes

gpkg = GeoPackage.create(r'c:\temp\test.gpkg')

srs_wkt = (
    'PROJCS["WGS_1984_UTM_Zone_23N",'
    'GEOGCS["GCS_WGS_1984",'
    'DATUM["D_WGS_1984",'
    'SPHEROID["WGS_1984",6378137.0,298.257223563]],'
    'PRIMEM["Greenwich",0.0],'
    'UNIT["Degree",0.0174532925199433]],'
    'PROJECTION["Transverse_Mercator"],'
    'PARAMETER["False_Easting",500000.0],'
    'PARAMETER["False_Northing",0.0],'
    'PARAMETER["Central_Meridian",-45.0],'
    'PARAMETER["Scale_Factor",0.9996],'
    'PARAMETER["Latitude_Of_Origin",0.0],'
    'UNIT["Meter",1.0]]')

srs = SRS('WGS_1984_UTM_Zone_23N', 'EPSG', 32623, srs_wkt)
fields = (
    Field('int_fld', SQLFieldTypes.integer),
    Field('text_fld', SQLFieldTypes.text),
    Field('test_fld_size', SQLFieldTypes.text, 100),
    Field('test_bool', SQLFieldTypes.boolean))

fc = gpkg.create_feature_class(
    'test', srs, fields=fields, shape_type=GeometryType.point)
```


### A word on Spatial References

Spatial references in Geopackages are somewhat loosely defined. You
may provide a spatial reference of any definition and from any
authority be that EPSG, ESRI or some other source. This library follows
this lead and has no restriction on the definitions provided however
it should be noted that if you would like your feature classes to
be readable by major software packages you should provide a
definition which the software can read appropriately.  Our testing
has found that ArcMap prefers definitions corresponding to its
own WKT format.

A very simple Spatial Reference object is provided with this package
for convenice.  It requires the name, authority, spatial reference id,
and spatial reference well known text.  This object should be used when
creating a feature class.

### Insert Records into a Feature Class

Records can be inserted into a Feature Class using the insert_rows 
method. This method inserts all the rows with a single sql call to 
get the best performance.

Geometry fields on gpkg feature classes created by this code base will
always be named "SHAPE".  Geometry inserted into this field must always
be WKB.  To create WKB use the utility functions from the conversion 
subpackage.  Currently utility functions exists to handle points, lines
and polygons (including z and m varieties).

This example shows the creation of a random point feature class and
builds upon the code from previous examples (the create feature class
portion of the code is omitted)

```python
from random import choice, randint
from string import ascii_uppercase, digits
from pygeopkg.conversion.to_geopkg_geom import (
    point_to_gpkg_point, make_gpkg_geom_header)
from pygeopkg.shared.constants import SHAPE
from pygeopkg.core.geopkg import GeoPackage

gpkg = GeoPackage(r'c:\temp\test.gpkg')
fc = gpkg.get_feature_class('test')

# Field objects can also be used
field_names = [SHAPE, 'int_fld', 'text_fld']

# Generate the geometry header once because it is always the same
point_geom_hdr = make_gpkg_geom_header(fc.srs.srs_id)

# Generate some random points and attributes
rows = []
for i in range(10000):
    rand_str = ''.join(choice(ascii_uppercase + digits) for _ in range(10))
    rand_int = randint(0, 1000)
    rand_x = randint(300000, 600000)
    rand_y = randint(1, 100000)
    wkb = point_to_gpkg_point(point_geom_hdr, rand_x, rand_y)
    rows.append((wkb, rand_int, rand_str))

fc.insert_rows(field_names, rows)
```

### Creating OGC Geometry Well Known Binaries

As mentioned, this library supports the creation of point, line and 
polygon well known binaries.  Functions supporting these capabilities 
can be found in  **pygeopkg.conversion.to_geopkg_geom**. 
Examples are provided below and further examples can be found in the 
tests.  See code documentation for more details as warranted.

It is important to note that Z and M capabilities are defined at the
time a feature class is created.  If a feature class is Z or M enabled
then a value must be provided for that value.  Be sure to pick the 
correct conversion function depending on the z and m combination 
desired.

#### Point Example

A binary header with srs details is always needed but (in pygeopkg) 
is the same for all features in a feature class.  For best performance
create this once. 

```python
# Point in WGS 84
x, y = -119, 34
hdr = make_gpkg_geom_header(4326)
gpkg_wkb = point_to_gpkg_point(hdr, x, y)
```

#### Line Example

The utility function for creating lines expects a list of points 
representing its vertices.

```python
# Line with ZM Values for use with UTM Zone 23N (WGS 84)
line = [(300000, 1, 10, 0), (300000, 4000000, 20, 1000),
        (700000, 4000000, 30, 2000), (700000, 1, 40, 3000)]
hdr = make_gpkg_geom_header(32623)
gpkg_wkb = points_zm_to_gpkg_line_string_zm(hdr, line)
```

#### Polygon Example

The utility function for creating regular polygons expects a list of 
rings where a ring is simply the list of points it contains.

```python
rings = [[(300000, 1), (300000, 4000000), (700000, 4000000),
          (700000, 1), (300000, 1)]]
hdr = make_gpkg_geom_header(32623)
gpkg_wkb = point_lists_to_gpkg_polygon(hdr, rings)
```


## Roadmap

* Write unpackers so that this package can be used to extract data
  from GeoPackages (focus is currently on writing). Unpackers specific
  to this pacakge exist for testing only.
* Write a more thorough implementation of the individual geometry headers.

## License

[MIT](https://choosealicense.com/licenses/mit/)

