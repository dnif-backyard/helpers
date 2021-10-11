'''
Created on 01-Oct-2019

@author: apoorv
'''
import logging
from logging.handlers import RotatingFileHandler
import inspect

# from redis_helper import redis_constants
ERR_Q = 'ERR_Q'
LEVELS = {
            0: logging.DEBUG,
            1: logging.INFO,
            4: logging.WARNING,
            5: logging.ERROR,
            6: logging.CRITICAL,
          }


def get_logger(logger_name, log_level, log_format=None, file_name=None, max_bytes=10000000, backup_count=10):
    '''

    :param logger_name:
    :param log_level:
    :param log_format:
    :param file_name:
    :param max_bytes:
    :param backup_count:
    '''
    logger = MyLogger(logger_name, log_level, log_format, file_name, max_bytes, backup_count)
    return logger


class MyLogger():
    logger = None
    '''

        :param logger_name:
        :param log_level:
        :param log_format:
        :param file_name:
        :param max_bytes:
        :param backup_count:
        '''
    def __init__(self, logger_name, log_level, log_format=None, file_name=None,
                 max_bytes=10000000, backup_count=10):
        level = LEVELS.get(log_level, logging.INFO)

        if not log_format:
            log_format = f"%(asctime)s %(levelname)s {logger_name} : %(message)s"

        # self.robj = redis_helper.get_redis_obj()
        self.fmt = "%Y-%m-%dT%H:%M:%S"

        log_handler = RotatingFileHandler(file_name, maxBytes=max_bytes, backupCount=backup_count)
        logging.basicConfig(handlers=[log_handler], level=level, format=log_format, datefmt=self.fmt)
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(level)

    @staticmethod
    def __get_call_info():
        stack = inspect.stack()
        if len(stack) == 1:
            fn = stack[0][1]
            ln = stack[0][2]
            func = stack[0][3]
        else:
            fn = stack[3][1]
            ln = stack[3][2]
            func = stack[3][3]
        return fn, func, ln

    # def log_to_redis(self, message, type='error', evt_type=False):
    #     try:
    #         # call_info = self.__get_call_info()
    #         # file_name = os.path.split(call_info[0])[-1]
    #         # file_name = file_name.rstrip('.py')
    #         # err_dict = {'tstamp': datetime.now().strftime(self.fmt), 'file_name': file_name,
    #         err_dict = {'tstamp': datetime.now().strftime(self.fmt), 'error_msg': str(message).replace("'", "''"),
    #                     'type': type}
    #         # 'function': call_info[1], 'line': call_info[2], 'error_msg': str(message).replace("'", "''"), 'type': type}
    #
    #         self.robj.lpush(ERR_Q, str(err_dict))
    #     except Exception as e:
    #         # call_info = self.__get_call_info()
    #         # err_message = "{} - {} at line {}: {}".format(call_info[0], call_info[1], call_info[2], str(e))
    #         err_message = "{}".format(str(e))
    #         print(err_message)

    def debug(self, message, *args):
        self.logger.debug(message, *args)

    def info(self, message, *args):
        self.logger.info(message, *args)

    def warn(self, message, *args):
        self.warning(message, *args)

    def warning(self, message, *args):
        self.logger.warning(message, *args)

    def error(self, message, *args):
        self.logger.error(message, *args)
        # self.log_to_redis(message,'error')

    def critical(self, message, *args):
        self.logger.critical(message, *args)
        # self.log_to_redis(message,'critical')

