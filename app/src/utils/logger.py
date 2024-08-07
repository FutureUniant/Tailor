import logging
import datetime


class Logger:
    def __init__(self, log_path, logger_name, log_level=logging.INFO):
        self.log_path = log_path
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.FileHandler(log_path)
            formatter = logging.Formatter("%(asctime)s|%(levelname)s|%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def set_level(self, log_level):
        self.logger.setLevel(log_level)

    def write_log(self, content, log_level=logging.INFO):
        """

        :param content:
                The format specification of the content :
                type: total stage: current stage: total step: current step: remark

                type:
                    interval: No actual progress, simulate progress based on time intervals.
                              When it belongs to the interval type, step related does not take effect
                    follow:   Calculate according to the step
        :param log_level:
        :return:
        """
        if log_level == logging.DEBUG:
            self.logger.debug(content)
        elif log_level == logging.WARNING:
            self.logger.warning(content)
        elif log_level == logging.ERROR:
            self.logger.error(content)
        elif log_level == logging.CRITICAL:
            self.logger.critical(content)
        else:
            self.logger.info(content)

    def read_log(self):
        log_records = []
        with open(self.log_path, "r") as file:
            for line in file:
                parts = line.split("|", 2)
                if len(parts) == 3:
                    log_time_str, log_level_str, log_content = parts
                    log_time = datetime.datetime.strptime(log_time_str.strip(), '%Y-%m-%d %H:%M:%S')
                    log_level = logging.getLevelName(log_level_str.strip())
                    log_records.append((log_time, log_level, log_content.strip()))
        return log_records

    def get_latest_log(self):
        with open(self.log_path, "r") as file:
            lines = file.readlines()
            if lines:
                latest_line = lines[-1]
                parts = latest_line.split("|", 2)
                if len(parts) == 3:
                    log_time_str, log_level_str, log_content = parts
                    log_time = datetime.datetime.strptime(log_time_str.strip(), '%Y-%m-%d %H:%M:%S')
                    log_level = logging.getLevelName(log_level_str.strip())
                    return log_time, log_level, log_content.strip()
        return None, None, None
