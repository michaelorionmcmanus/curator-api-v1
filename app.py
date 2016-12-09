import logging, traceback, sys, os
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
here = os.path.dirname(os.path.realpath(__file__))
sys.path = [os.path.join(here, "src/orion")] + sys.path
import sys, orion.providers.aws.app as app
current_module = sys.modules[__name__]

try:
    logger.info('CREATING APP')
    app.create(current_module)
except Exception as e:
    logger.info('UNABLE TO RUN')
    logger.info(e)
    if type(e.message) is dict:
        response = e.message
    else:
        traceback.print_exc()