
import logging


logging.basicConfig(format="%(message)s", level=logging.DEBUG)
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.ERROR)

log = logging.getLogger('lback_log')
