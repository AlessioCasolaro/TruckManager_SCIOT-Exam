import boto3
from config import DefaultConfig
from datetime import datetime,date,timedelta
import requests

CONFIG = DefaultConfig()

dynamodb = boto3.resource('dynamodb', endpoint_url=CONFIG.ENDPOINT_URL)

truckTable = dynamodb.Table('Trucks')
trucks = truckTable.scan()['Items']
times = []
names = []
currentTime = datetime.now().time()

def lambda_handler(event, context):
    for truck in trucks:
        names.append(truck['name'])
        times.append(truck['dateTimeDeparture'][11:])
    for index, time in enumerate(times):
        if ':' in time:
            time_object = datetime.strptime(time, '%H:%M').time()
                
            if datetime.combine(date.today(), currentTime) - datetime.combine(date.today(), time_object) > timedelta(hours=9):
                print("Time exceded for truck " + names[index]+ "\tSending message to Telegram")
                requests.get('https://api.telegram.org/bot' + CONFIG.TOKEN_TELEGRAM + '/sendMessage?chat_id=' + CONFIG.CHAT_ID+ '&parse_mode=Markdown&text=' + names[index] +" - You're driving more than 9 Hours. Stop NOW!")    
lambda_handler(None, None)
