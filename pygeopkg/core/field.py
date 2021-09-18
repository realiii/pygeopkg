"""
Field
"""
from pygeopkg.shared.enumeration import SQLFieldTypes


class Field(object):
    """
    Field Object for GeoPackage
    """
    def __init__(self, name, data_type, size=None):
        """
        Initialize the Field class

        :param name: The name of the field
        :type name: str
        :param data_type: The data type of the field
        :type data_type: str
        :param size: the size of the field (basically unecessary in sqlite)
        """
        super(Field, self).__init__()
        self.name = name
        self.data_type = data_type
        self.size = size
    # End init built-in

    def __repr__(self):
        """
        String representation
        """
        if (self.size and
                self.data_type in (SQLFieldTypes.blob, SQLFieldTypes.text)):
            return '{0} {1}{2}'.format(self.name, self.data_type, self.size)
        return '{0} {1}'.format(self.name, self.data_type)
    # End __repr__ built-in
# End Field class


if __name__ == '__main__':
    pass
