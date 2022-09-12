import boto3
from werkzeug.security import generate_password_hash
from config import DefaultConfig

CONFIG = DefaultConfig

dynamodb = boto3.resource('dynamodb', endpoint_url=CONFIG.ENDPOINT_URL)

#Tables creating
trucks = dynamodb.create_table(
    TableName='Trucks',
    KeySchema=[
        {
            'AttributeName': 'truckID',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'truckID',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

managers = dynamodb.create_table(
    TableName='Managers',
    KeySchema=[
        {
            'AttributeName': 'email',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'email',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

errors = dynamodb.create_table(
    TableName='Errors',
    KeySchema=[
        {
            'AttributeName': 'errNo',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'errNo',
            'AttributeType': 'N'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)
print('Tables created!')

#Tables populating
trucks.put_item(Item={'name': 'Scania V10','truckID': 'A1','dateTimeDeparture': '','dateTimeArrival': ''})
trucks.put_item(Item={'name': 'Scania V5','truckID': 'A2','dateTimeDeparture': '','dateTimeArrival': ''})
trucks.put_item(Item={'name': 'Volvo V12','truckID': 'A3','dateTimeDeparture': '','dateTimeArrival': ''})
trucks.put_item(Item={'name': 'Iveco Tails','truckID': 'A4','dateTimeDeparture': '','dateTimeArrival': ''})
trucks.put_item(Item={'name': 'MAN Storm','truckID': 'A5','dateTimeDeparture': '','dateTimeArrival': ''})

managers.put_item(Item={'managerName': 'Luca Argentero', 'email': 'luca@truckmanager.it', 'password': generate_password_hash('luca')})
managers.put_item(Item={'managerName': 'Pasquale Scotti', 'email': 'pasquale@truckmanager.it', 'password': generate_password_hash('pasquale')})

errors.put_item(Item={'errNo': 277,'truckID': 'A5','dateTime': '01-09'})
errors.put_item(Item={'errNo': 279,'truckID': 'A5','dateTime': '01-09'})
errors.put_item(Item={'errNo': 278,'truckID': 'A4','dateTime': '02-09'})


print('Table', trucks, 'populated!')
print('Table', managers, 'populated!')
print('Table', errors, 'populated!')


#Log group
client = boto3.client('logs', endpoint_url=CONFIG.ENDPOINT_URL)

client.create_log_group(logGroupName='ErrorDetected')

client.put_retention_policy(logGroupName='ErrorDetected', retentionInDays=7)
client.create_log_stream(logGroupName='ErrorDetected', logStreamName='ErrorDetected')

print('Cloudwatch stream ErrorDetected created!')
