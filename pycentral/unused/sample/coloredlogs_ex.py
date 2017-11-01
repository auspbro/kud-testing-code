import coloredlogs, logging
import os

# Create a logger object.
logger = logging.getLogger(__name__)

os.environ['COLOREDLOGS_LOG_FORMAT'] ='%(asctime)s - %(message)s'

# By default the install() function installs a handler on the root logger,
# this means that log messages from your code and log messages from the
# libraries that you use will all show up on the terminal.
coloredlogs.install(level='DEBUG')

# If you don't want to see log messages from libraries, you can pass a
# specific logger object to the install() function. In this case only log
# messages originating from that logger will show up on the terminal.
coloredlogs.install(level='DEBUG', logger=logger)


# Some examples.
logger.debug("this is a debugging message")
logger.info("this is an informational message")
logger.warning("this is a warning message")
logger.error("this is an error message")
logger.critical("this is a critical message")

'''
2017-10-18 11:01:51 AN990113551 __main__[3684] DEBUG this is a debugging message
2017-10-18 11:01:51 AN990113551 __main__[3684] INFO this is an informational message
2017-10-18 11:01:51 AN990113551 __main__[3684] WARNING this is a warning message
2017-10-18 11:01:51 AN990113551 __main__[3684] ERROR this is an error message
2017-10-18 11:01:51 AN990113551 __main__[3684] CRITICAL this is a critical message
'''