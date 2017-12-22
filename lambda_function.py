import json
import boto3
from telegram import *


def respond(res):
    print("hit lambda kill")
    return {
        'statusCode': '200',
        'body': json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            },
        }


def lambda_handler(event, context):

#Setting Variables
    jd = 'GDude'
    delay = 1
    #Grabbing Python dictonary event.body then converting to json
    body = json.loads(event['body'])
    #Grabbing json properties and storing to variables that are reused.
    try:
        chatid = body['message']['chat']['id']
        text = body['message']['text']
        username = body['message']['from']['username']
        messagedate = body['message']['date']
        messageid = body['message']['message_id']
#Starting Main Script
    except:
        return respond(print("Unable to find key variables"))
    #Looking for JD and reply from trigger. It then looks at the time to see if a joke is required.
    try:
        if body['message']['reply_to_message'] != None and username == jd:
            dif = messagedate - body['message']['reply_to_message']['date']
            if dif / 60 > delay:
            #Grabs the joke and formats with the Get_time function then sends back to the chatroom.
                print("JD and time delay trigger hit")
                reply = get_joke().replace("\n", "").format(get_time(dif))
                return respond(send_message(reply, chatid, reply_id=messageid))
            print("JD Trigger hit but time delay trigger missed")
    except:
        pass

    #Looking for search or random triggers then sending an image with the request query.
    if text.startswith('/random'):
        print("random trigger hit")
        string = text[8:]
        image = get_picture(string, "random")
        if image.startswith('1.'):
            reply = "<b>Error</b> = <i>{}</i> \n<b>Query</b> =  <i>{}</i> ".format(image[2:], string)
            print(reply)
            return respond(send_message(reply, chatid))
        else:
            return respond(send_picture(get_picture(string, "random"), chatid))
    elif text.startswith('/search'):
        print("search trigger hit")
        string = text[8:]
        image = get_picture(string, "search")
        if image.startswith('1.'):
            reply = "<b>Error</b> = <i>{}</i> \n<b>Query</b> = <i>{}</i> ".format(image[2:], string)
            print(reply)
            return respond(send_message(reply, chatid))
        else:
            return respond(send_picture(get_picture(string, "search"), chatid))

    #Ending lambda function because no triggers met. 
    return respond(print("Nothing triggered ending lambda call."))
