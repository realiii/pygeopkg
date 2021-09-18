"""
Geopackage SRS Class
"""


class SRS(object):
    """
    Spatial Reference System
    """
    def __init__(self, name, organization, org_coordsys_id, definition,
                 description=''):
        """
        Initialize the SRS class

        :param name: The name of the SRS
        :type name: str
        :param organization: The authority or organization
        :type organization: str
        :param org_coordsys_id: The Coordinate System ID
        :type org_coordsys_id: int
        :param definition: The well known text definition for the Spatial Ref
        :type definition: str
        :param description: A description of the spatial ref
        :type description: str
        """
        super(SRS, self).__init__()
        self.name = name
        self.organization = organization
        self.org_coordsys_id = org_coordsys_id
        self._srs_id = org_coordsys_id
        self.definition = definition
        self.description = description
    # End init built-in

    @property
    def srs_id(self):
        """
        The SRS id

        :return: The id of the spatial ref
        :rtype: int
        """
        return self._srs_id

    @srs_id.setter
    def srs_id(self, value):
        """
        Set the value of the srs id

        :param value: The new value for the srs id
        """
        self._srs_id = value
    # End srs_id property

    @property
    def row(self):
        """
        Row values

        :return: the row this SRS would represent in the underlying gpkg table.
        :rtype: tuple
        """
        return (self.name, self.srs_id, self.organization,
                self.org_coordsys_id, self.definition, self.description)
    # End row property
# End SRS class


if __name__ == '__main__':
    pass
