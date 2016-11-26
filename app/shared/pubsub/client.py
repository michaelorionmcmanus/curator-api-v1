import boto3, os, time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
here = os.path.dirname(os.path.realpath(__file__))

def get_client():
    import logging
    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    myAWSIoTMQTTClient = AWSIoTMQTTClient(str(int(time.time())), useWebsocket=True)
    myAWSIoTMQTTClient.configureEndpoint(os.environ['IOT_ENDPOINT'], 443)
    myAWSIoTMQTTClient.configureCredentials(here + '/root_CA.pem')
    # myAWSIoTMQTTClient.configureIAMCredentials('ASIAIRSDWYO4OPD45ZRA', 'P9Aql6MG7My1GlrFzCpNy6G349zTMIgnQXIKRCsy')
    myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
    myAWSIoTMQTTClient.connect()
    return myAWSIoTMQTTClient