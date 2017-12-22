import boto3
import json
from telegram import *

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
    
    JD = "GDude"
    delay = 1
    
    body = json.loads(event['body'])

    chatid = body['message']['chat']['id']
    text = body['message']['text']
    username = body['message']['from']['username']
    messagedate = body['message']['date']
    
    if body['message']['reply_to_message']:
        if username == JD:
            replytime = body['message']['reply_to_message']['date']
            dif = messagedate - replytime
            if dif / 60 > delay:
                reply = get_joke().replace("\n", "").format(get_time(dif))
                #dif = get_time(dif)
                respond(None, send_message(reply, chatid))

                
        


    #if token != expected_token:
    #    logger.error("Request token (%s) does not match expected", token)
    #    return respond(Exception('Invalid request token'))

    return respond(None, "Nothing triggered ending lambda call.")
    
