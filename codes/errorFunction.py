import boto3
import time
import json
from random import randint
from config import DefaultConfig

CONFIG = DefaultConfig()
sqs = boto3.resource('sqs', endpoint_url=CONFIG.ENDPOINT_URL)
ses = boto3.client('ses', endpoint_url=CONFIG.ENDPOINT_URL)
dynamodb = boto3.resource('dynamodb', endpoint_url=CONFIG.ENDPOINT_URL)

errorsTable = dynamodb.Table('Errors')
trucks = errorsTable.scan()['Items']

def lambda_handler(event, context):
    queue = sqs.get_queue_by_name(QueueName='errors')
    messages = []
    while True:
        response = queue.receive_messages(
            MaxNumberOfMessages=10, VisibilityTimeout=10, WaitTimeSeconds=10)
        messages.extend(response)
        if response:
            for message in messages:
                content = json.loads(message.body)
                print(content)
                truckID = content['truckID']
                dateTime = content['dateTime']
                print(dateTime[:-5])
                #Putting elem into errors table
                item = {
                            'errNo': randint(0,999),
                            'truckID': truckID,
                            'dateTime': dateTime[:-5]
                        }
                errorsTable.put_item(Item=item)

                #Preparing MessageContent
                messageContent = {
                    'Subject': {
                        'Data': 'TruckManager',
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': "Error occurred in Water Temperature Sensor " + str(truckID) + " in " + str(dateTime),
                            'Charset': 'string'
                        },
                        'Html': {
                            'Data': 'This message body contains HTML formatting.',
                            'Charset': 'UTF-8'
                        }
                    }
                }
                # Send email to localstack
                response = ses.send_email(
                    Source=CONFIG.EMAIL,
                    Destination={
                        'ToAddresses': [
                            CONFIG.EMAIL,
                        ],
                        'CcAddresses': [],
                        'BccAddresses': []
                    },
                    Message=messageContent
                )

                # Log the email
                log_client = boto3.client(
                    'logs', endpoint_url=CONFIG.ENDPOINT_URL)

                log_event = {
                    'logGroupName': 'ErrorDetected',
                    'logStreamName': 'ErrorDetected',
                    'logEvents': [
                        {
                            'timestamp': int(round(time.time() * 1000)),
                            'message': str(messageContent)
                        },
                    ],
                }

                log_client.put_log_events(**log_event)

                message.delete()
        else:
            break


lambda_handler(None, None)
