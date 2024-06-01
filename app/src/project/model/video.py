
VIDEO_TABLE = "video"


class Video:
    def __init__(
            self,
            id=-1,
            name="",
            path="",
            sort=0,
    ):
        """

        :param id:
        :param name:
        :param path:
        :param sort:
        """
        self.id = id
        self.name = name
        self.path = path
        self.sort = sort
