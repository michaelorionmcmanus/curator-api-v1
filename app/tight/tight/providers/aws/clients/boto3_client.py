import boto3, sys
boto3_session = None
def session():
    current_module = sys.modules[__name__]
    boto3_session = getattr(current_module, 'boto3_session')
    if boto3_session:
        return boto3_session
    else:
        boto3_session = boto3.Session()
        setattr(current_module, 'boto3_session', boto3_session)
        return boto3_session
