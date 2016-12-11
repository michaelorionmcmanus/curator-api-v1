import sys, os

here = os.path.dirname(os.path.realpath(__file__))
sys.path = [os.path.join(here, "app/tight")] + sys.path

import tight.providers.aws.app as app
app.run()