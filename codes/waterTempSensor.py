import boto3
import datetime
import random
from config import DefaultConfig

CONFIG = DefaultConfig

sqs = boto3.resource('sqs', endpoint_url=CONFIG.ENDPOINT_URL)
dynamodb = boto3.resource('dynamodb', endpoint_url=CONFIG.ENDPOINT_URL)
currentDateTime = str(datetime.datetime.now().strftime("%d-%m %H:%M"))


trucksList = dynamodb.Table('Trucks').scan(ProjectionExpression='truckID')['Items']


randIfElse = ["ERROR","noError"]


def detectWaterTemp():
    for truck in trucksList:
        randRes = random.choice(randIfElse)
        if randRes == "ERROR":
            queue = sqs.get_queue_by_name(QueueName="errors")
            msg = '{"truckID": "%s","dateTime": "%s"}' % (truck['truckID'], currentDateTime)
            print("Error occurred in Water Temperature Sensor" + msg + '\n')
            queue.send_message(MessageBody=msg)
        else:
            temperature = round(random.uniform(100.00, 350.00), 2)
            queue = sqs.get_queue_by_name(QueueName='waterTemperature')
            msg = '{"truckID": "%s","waterTemperature": "%.2f","dateTime": "%s"}\n' % (truck['truckID'],temperature, currentDateTime)
            print(msg)
            queue.send_message(MessageBody=msg)

detectWaterTemp()