from app.src.utils.timer import Timer


class ProjectInfo:
    def __init__(self,
                 id=-1,
                 name="",
                 state=0,
                 image_path="",
                 tailor_path="",
                 last_open_time=Timer.get_timestamp(integer=True, string=False),
                 major=0,
                 minor=0,
                 patch=0):
        """

        :param id:
        :param name:
        :param state:        项目的状态。-1是删除；0是还未完成；1是已经完成
        :param image_path:
        :param tailor_path:
        :param last_open_time:
        :param major:
        :param minor:
        :param patch:
        """
        self.id = id
        self.name = name
        self.state = state
        self.image_path = image_path
        self.tailor_path = tailor_path
        self.last_open_time = last_open_time
        self.major = major
        self.minor = minor
        self.patch = patch

    def __eq__(self, other):
        return self.id == other.id and \
            self.name == other.name and \
            self.state == other.state and \
            self.tailor_path == other.tailor_path

    def __str__(self):
        project_str = (f"Project Info : \n"
                       f"\tID:      {self.id}\n"
                       f"\tName:    {self.name}\n"
                       f"\tPath:    {self.tailor_path}\n"
                       f"\tVersion: {self.major}.{self.minor}.{self.patch}\n"
                       f"\tState:   {self.state}\n"
                       )
        return project_str
