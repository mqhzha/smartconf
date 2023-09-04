import logging

class ilog:
    def __init__(self,logfile='',logger_name=''):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        fh = logging.FileHandler(logfile)
        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # add the handlers to the logger
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)



    def get_logger(self):
        return self.logger


if __name__=='__main__':
    logger=ilog('test.log','test').get_logger()
    logger.info('aaa')