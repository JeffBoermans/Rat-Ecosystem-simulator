class ExtensionException(Exception):
    """An exception occurred related to extensions"""
    pass


class DuplicateExtension(ExtensionException):
    """A simulation detects a duplicate extension"""
    pass


class MissingExtensionProperty(ExtensionException):
    """The extension could not retrieve a needed property from somewhere."""
    pass

class MissingOrganismProperty(MissingExtensionProperty):
    """The extension could not retrieve a required extension property from an
    organism's extension properties
    """
    pass

class MissingVegetationProperty(MissingExtensionProperty):
    """The extension could not retrieve a required extension property from a
    vegetation's extensions properties
    """
    pass
