
class Custom:
    def __init__(self,
                 name="",
                 value=""):
        """

        :param name:
        :param value:
        """
        self.name = name
        self.value = value

    def __eq__(self, other):
        return self.name == other.name
