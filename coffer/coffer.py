"""
Secure storage container for treasures
"""

class Coffer(object):
    """
    Secure storage container for treasures

    Treasures must be removed to be modified and re-added to be
    stored again.
    """

    def __init__(self, path, *args, **kwargs):
        """
        Creates a new coffer
        """
        self.__path = path

    def add(self, outer_path, inner_path, *args, **kwargs):
        """
        Adds a treasure to the coffer
        """
        pass

    def remove(self, inner_path, outer_path, *args, **kwargs):
        """
        Removes a treasure from the coffer
        """
        return None

    def get_treasures(self, *args, **pwargs):
        """
        Get an iterable of paths to each treasure inside the coffer
        """
        return iter(())

    @property
    def path(self, *args, **kwargs):
        return self.__path
