import logging

"""as 
filename=node_id+'_log.txt',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG
"""


class Logger:

    logger = None

    # def __init__(self, node_id: str):
    #     logging.basicConfig()
    #
    #     self.logger = logging.getLogger(__name__)
    #     self.node_id = node_id

    @staticmethod
    def get_logger(node_id: str):

        if Logger.logger is None:
            logging.basicConfig(filename=node_id + '_log.txt',
                                filemode='a',
                                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                                datefmt='%H:%M:%S',
                                level=logging.DEBUG)

            Logger.logger = logging.getLogger(__name__)
        return Logger.logger

    def log_info(self, message: str):
        self.logger.log(logging.INFO, [self.node_id, message])

    def log_error(self, message: str):
        self.logger.log(logging.ERROR, [self.node_id, message])

    def log_debug(self, message: str):
        self.logger.log(logging.DEBUG, [self.node_id, message])






