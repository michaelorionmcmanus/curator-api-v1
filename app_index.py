import sys, os

here = os.path.dirname(os.path.realpath(__file__))
sys.path = [os.path.join(here, "app/vendored")] + sys.path

import tight.providers.aws.lambda_app.app as app
app.run()