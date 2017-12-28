import json
from telegram import *


def respond(res):
    """Function to end lambda call and return ok message to API Gateway"""
    print("hit lambda kill")
    return {
        'statusCode': '200',
        'body': json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            },
        }


def lambda_handler(event, context):
    """Main lambda function"""
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
    except:
        return respond(print("Unable to find key variables"))
    #Starting Main Script

    #Testing to see if the message contains an image
    try:
        caption = body['message']['caption']
        file_id = body['message']['photo'][2]['file_id']

        #Looking for /name switch inside of caption if it contains image
        if caption.startswith('/name'):
            caption = caption[6:]
    except:
        pass   


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

    elif text.startswith('/pic'):
        print("pic trigger hit")
        string = text[5:]
        dbcall = search_db(string)
        if dbcall.startswith('http'):
            reply = dbcall
            return respond(send_picture(reply, chatid))
        else:
            reply = "<b>Unable to find {} in the database, try these names instead:</b>\n{}".format(string, dbcall)
            return respond(send_message(reply, chatid))

    #Ending lambda function because no triggers met.
    return respond(print("Nothing triggered ending lambda call."))
