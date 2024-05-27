class SaiCommon:
    """
    Base class for all SAI objects.
    """

    def __init__(self, name: str, description: str):
        self.name: str = name
        self.description: str = description
