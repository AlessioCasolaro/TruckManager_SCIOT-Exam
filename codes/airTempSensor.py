import boto3
import datetime
import random
from config import DefaultConfig

CONFIG = DefaultConfig

sqs = boto3.resource('sqs', endpoint_url=CONFIG.ENDPOINT_URL)
dynamodb = boto3.resource('dynamodb', endpoint_url=CONFIG.ENDPOINT_URL)
currentDateTime = str(datetime.datetime.now().strftime("%d-%m %H:%M"))

trucksList = dynamodb.Table('Trucks').scan(ProjectionExpression='truckID')['Items']

def detectAirTemp():
    for truck in trucksList:
        temperature = round(random.uniform(-15.0, 15.0), 2)
        queue = sqs.get_queue_by_name(QueueName='airTemperature')
        msg = '{"truckID": "%s","temperature": "%.2f","dateTime": "%s"}' % (
            truck['truckID'], temperature, currentDateTime)
        print(msg)
        queue.send_message(MessageBody=msg)


detectAirTemp()
