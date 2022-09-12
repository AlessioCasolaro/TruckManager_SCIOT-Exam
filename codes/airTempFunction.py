import boto3
import json
from config import DefaultConfig

CONFIG = DefaultConfig()

sqs = boto3.resource('sqs', endpoint_url=CONFIG.ENDPOINT_URL)
dynamodb = boto3.resource('dynamodb', endpoint_url=CONFIG.ENDPOINT_URL)

truckTable = dynamodb.Table('Trucks')
trucks = truckTable.scan()['Items']


def lambda_handler(event, context):
    queue = sqs.get_queue_by_name(QueueName='airTemperature')
    messages = []
    while True:
        response = queue.receive_messages(
            MaxNumberOfMessages=10, VisibilityTimeout=10, WaitTimeSeconds=10)
        messages.extend(response)
        if response:
            for message in messages:
                content = json.loads(message.body)

                for truck in trucks:
                    if content['truckID'] == truck['truckID']:
                        if float(content['temperature']) >= 5:
                            print("Air temperature of truck " + str(content['truckID']) + ", detected at " + str(content['dateTime'])+ " is " + content['temperature'] + "C. Too high, adjusting it.\n")
                        elif float(content['temperature']) <= -5:
                            print("Air temperature of truck " + str(content['truckID']) + ", detected at " + str(content['dateTime'])+ " is " + content['temperature'] + "C. Too low, adjusting it.\n")
                        else:
                            print("Air temperature of truck " + str(content['truckID']) + ", detected at " + str(content['dateTime'])+ " is " + content['temperature'] + "C. Ok.\n")
                               
                        truckTable.update_item(Key={'truckID': content['truckID']}, 
                               UpdateExpression="set dateTimeDetection = :val1, temperature = :val2", 
                               ExpressionAttributeValues={':val1': content['dateTime'],':val2': str(content['temperature'])})
                        message.delete()
        else:
            break


lambda_handler(None, None)
