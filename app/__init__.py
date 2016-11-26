import sys, os
here = os.path.dirname(os.path.realpath(__file__))
sys.path = [os.path.join(here, "./vendored")] + sys.path
sys.path = [os.path.join(here, "./shared")] + sys.path
sys.path = [os.path.join(here, "./models")] + sys.path
sys.path = [os.path.join(here, "../")] + sys.path

import logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info('LOCKED AND LOADED')