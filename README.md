# pygeopkg

**pygeopkg** is a Python compatible library that allows for the creation and
population of (*write-to*) an OGC GeoPackage database, including creating features within this resource. GeoPackages can be opened and viewed software solutions built for viewing and analyzing spatial data, including ArcGIS and QGIS. 

For more details on OGC GeoPackages, please see the [OGC web page](http://www.geopackage.org/).


## Installation

**pygeopkg** was created to work as a packaged sub-respository in a larger
Python library. As such, users should simply add this repository as
a sub-repository via git to their main repository or download the files and
add them to their projects as they see fit.


### Python Compatibility

The **pygeopkg** library is compatible with Python 2+ and Python 3+.


## Usage

**pygeopkg** can be used to: 
* Create a new empty GeoPackage from scratch.
* Create new Feature Classes within a GeoPackage.
* Populate Feature Classes with geometry and attributes. (see **Steps 3 & 4**)


### Step 1 - Create An Empty GeoPackage

```python
from pygeopkg.core.geopkg import GeoPackage

# Creates an empty geopackage
gpkg = GeoPackage.create(r'c:\temp\test.gpkg')
```

Geopackages are created with *three* default Spatial References defined
automatically, a pair of Spatial References to handle undefined cases,
and a WGS 84 entry. 

The definition of the WGS84 entry is flexible - meaning that the *WKT for WGS84* can be setup per the users liking. As an example, use with Esri's ArcGIS means either using the *EPSG WKT* or the *ESRI WKT*. By
default the *ESRI WKT* is used - However, if *EPSG WKT* is desired, you
may provide a ``flavor`` parameter to the create method specifying EPSG.

```
# Creates an empty geopackage
gpkg = GeoPackage.create(r'c:\temp\test.gpkg', flavor='EPSG')
```


### Step 2 - Create A New Feature Class

To create a new Feature Class in the empty GeoPackage, you will need
to tell the GeoPackage the Spatial Reference of the Feature Class
and the schema (e.g., fields) to be available in the Feature Class.

A Feature Class can be created with *Z* or *M* (or both) enabled. If 
either of these options are enabled, the geometry inserted into the 
Feature Class **must** include a value for the option specified.

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


#### About Spatial References For GeoPackages

Spatial References in GeoPackages are somewhat loosely defined. You
may provide a Spatial Reference of any definition and from any
authority - be that EPSG, ESRI, or another source. This library follows
this lead and has no restriction on the definitions provided. However,
it should be noted that if you would like Feature Classes to
be readable by major software packages, you should provide a
definition which the software can read appropriately. For example, our testing
has found that ArcMap prefers definitions corresponding to its
own WKT format.

A very simple Spatial Reference object is provided with this package
for convenience. It requires the name, authority, Spatial Reference ID,
and Spatial Reference well known text. This object should be used when
creating a Feature Class.


### Step 3 - Insert Records Into A Feature Class

Records can be inserted into a Feature Class using the ``insert_rows`` 
method. This method inserts all the rows with a single sql call to 
get the best performance.

Geometry fields on **gpkg** Feature Classes created by this code base will
always be named ``SHAPE``. Geometry inserted into this field must always
be *WKB*. To create *WKB*, use the utility functions from the conversion 
subpackage. Currently utility functions exists to handle points, lines
and polygons (including *Z* and *M* varieties).

This example shows the creation of a random point Feature Class and
builds upon the code from previous examples. Note that the create Feature Class
portion of the code is omitted...

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


### Step 4 - Creating OGC Geometry Well Known Binaries

As mentioned, this library supports the creation of point, line, and 
polygon well known binaries. Functions supporting these capabilities 
can be found in ``pygeopkg.conversion.to_geopkg_geom``. 

Examples are provided below and further examples can be found in the 
tests. See code documentation for more details as warranted.

It is important to note that *Z* and *M* capabilities are defined at the
time a Feature Class is created. If a Feature Class is *Z* or *M* enabled,
then a value must be provided for that value. Be sure to pick the 
correct conversion function depending on the *Z* and *M* combination 
desired.


#### Point Example

A binary header with srs details is always needed but (in **pygeopkg**) 
is the same for all features in a Feature Class. For best performance,
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
  from GeoPackages. Focus is currently on writing. Unpackers specific
  to this pacakge exist for testing only.
* Write a more thorough implementation of the individual geometry headers.


## License

[MIT](https://choosealicense.com/licenses/mit/)

