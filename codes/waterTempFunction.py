import boto3
import json
import requests
from config import DefaultConfig

CONFIG = DefaultConfig()

sqs = boto3.resource('sqs', endpoint_url=CONFIG.ENDPOINT_URL)
dynamodb = boto3.resource('dynamodb', endpoint_url=CONFIG.ENDPOINT_URL)

truckTable = dynamodb.Table('Trucks')
trucks = truckTable.scan()['Items']


def lambda_handler(event, context):
    queue = sqs.get_queue_by_name(QueueName='waterTemperature')
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
                        if float(content['waterTemperature']) >= 230:
                            msg="Water temperature of truck " + str(content['truckID']) + ", detected at " + str(content['dateTime'])+ " is " + content['waterTemperature'] + "C. Too high, you need to stop now!"
                            print(msg)
                            requests.get('https://api.telegram.org/bot' + CONFIG.TOKEN_TELEGRAM + '/sendMessage?chat_id=' + CONFIG.CHAT_ID+ '&parse_mode=Markdown&text=' + msg)
                        else:
                            print("Water temperature of truck " + str(content['truckID']) + ", detected at " + str(content['dateTime'])+ " is " + content['waterTemperature'] + "C. Good, no need to send message!")
                        message.delete()           
        else:
            break


lambda_handler(None, None)
