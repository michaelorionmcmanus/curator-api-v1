import os, json, re

def load(aws_profile="default"):
    aws_credentials = '{}/.aws/credentials'.format(os.environ['HOME'])
    if os.path.isfile(aws_credentials):
        # Get aws credentials file in order to access key/secret for specified profile.
        with open(os.path.expanduser(aws_credentials)) as credentials_file:
            credentials = credentials_file.read()

        # Split on line break in order to loop through contents.
        credential_lines = credentials.split('\n')
        for i, elem in enumerate(credential_lines):
            # Once a profile match is found, grab the next two lines.
            if(elem == '['+ aws_profile + ']'):
                key = credential_lines[i+1]
                secret = credential_lines[i+2]
                # We've found what we're looking for. Bail out.
                break

        # Inject environment variables for aws connection. This is not done in an actual environment.
        if key and secret:
            os.environ['AWS_ACCESS_KEY_ID'] = key.split('=')[1].strip()
            os.environ['AWS_SECRET_ACCESS_KEY'] = secret.split('=')[1].strip()
        else:
            # Expect environment variables to be already present.
            pass

    os.environ['SERVERLESS_PROJECT'] = 'sls-v1'
    # Default to "dev" stage.
    os.environ['SERVERLESS_STAGE'] = stage = os.environ.get('SERVERLESS_STAGE') or 'dev'
    os.environ['SERVERLESS_REGION'] = region = os.environ.get('SERVERLESS_REGION') or 'us-west-2'