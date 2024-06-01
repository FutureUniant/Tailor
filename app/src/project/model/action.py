from app.src.utils.timer import Timer

ACTION_TABLE = "action"


class Action:
    def __init__(
            self,
            id=0,
            operation_id="",
            act_time=Timer.get_timestamp(integer=True, string=False),
            parameter=None,
            output=None,
            video=None,
            file=None,
    ):
        """

        :param id:
        :param operation_id:
        :param act_time:
        :param parameter:
        :param output:
        :param video:
        :param file:
        """
        self.id = id
        self.operation_id = operation_id
        self.act_time = act_time
        self.parameter = parameter
        self.output = output
        self.video = video
        self.file = file
