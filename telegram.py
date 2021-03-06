import urllib.parse
import random
import json
import requests
import boto3
import uuid
from boto3.dynamodb.conditions import Key, Attr
from libcloud.storage.types import Provider
from libcloud.storage.providers import get_driver

ACCESS_KEY = open("ACCESS_KEY").read()
SECRET_KEY = open("SECRET_KEY").read()


client = boto3.client(
    'dynamodb',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

APIKEY = open("apikey").read()


URL = "https://api.telegram.org/bot{}/".format(APIKEY)


def api_call(url):
    """Taking telegrambot URL and making API call using requests"""
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def send_message(text, chat_id, reply_id=0):
    """sending telegram message to use with text and chat_id as required params"""
    text = urllib.parse.quote(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=html".format(text, chat_id)
    if reply_id != 0:
        url = url + "&reply_to_message_id={}".format(reply_id)
    api_call(url)

def send_picture(photo, chat_id, reply_id=0):
    """sending telegram photo to use with photourl and chat_id as required params"""
    url = URL + "sendPhoto?photo={}&chat_id={}".format(photo, chat_id)
    if reply_id != 0:
        url = url + "&reply_to_message_id={}".format(reply_id)
    api_call(url)

def get_file(file_id, caption):
    """using a fileid provided by telegram to grab the image"""
    url = URL + "getFile?file_id={}".format(file_id)
    fileurl = json.loads(api_call(url))
    url = "https://api.telegram.org/file/bot{}/".format(APIKEY)
    url = url + fileurl['result']['file_path']
    response = requests.get(url)
    if response.status_code == 200:
        with open("/tmp/{}.jpg".format(caption), 'wb') as f:
            f.write(response.content)
    #Returning temp path to uploaded file
    return "/tmp/{}.jpg".format(caption)

def get_raxkey():
    """Function to grab rax access token id and tenant_id. Then stores them as a dictionary."""
    rkey = open("rkey").read()
    url = 'https://identity.api.rackspacecloud.com/v2.0/tokens'


    payload = {
        "auth" : {
            "RAX-KSKEY:apiKeyCredentials" : {
                "username" : "cplimmer",
                "apiKey" : rkey
            }
        }
    }
    headers = {
        "Content-Type" : "application/json"
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)

    response = json.loads(response.content)
    token_id = response['access']['token']['id']
    tenant_id = response['access']['token']['tenant']['id']

    return {'token_id' : token_id, 'tenant_id' : tenant_id}

def upload_image(path, name):
    """Function to upload image to cloudfiles"""

    rkey = open("rkey").read()

    cls = get_driver(Provider.CLOUDFILES)

    driver = cls('cplimmer', rkey, region='iad')

    container = driver.get_container(container_name='pics')

    objectname = name + str(uuid.uuid4())[0:4] + '.jpg'

    try:
        with open(path, 'rb') as iterator:
            obj = driver.upload_object_via_stream(iterator=iterator,
                                                  container=container,
                                                  object_name=objectname)
    except:
        pass

    url = "http://45bee749b9633e0cdbef-8f80b823ed0636b36ed6366a0c590e0e.r54.cf5.rackcdn.com/" + objectname
    return url



def get_time(timeS):
    """takes time in seconds and converts to string format to send via telegram"""
    timeM = 0
    timeH = 0
    timeD = 0
    time = ""

    #get time in seconds and convert to minutes if over 60
    if timeS > 59:
        timeM = 0
        while timeS > 59:
            timeS = timeS - 60
            timeM += 1
    if timeS > 1:
        timeS = "{} seconds ".format(timeS)
    elif timeS == 1:
        timeS = "{} second ".format(timeS)
    elif timeS < 1:
        timeS = None
    #get time in minutes and conver to hours if over 60
    if timeM > 59:
        timeH = 0
        while timeM > 59:
            timeM = timeM - 60
            timeH += 1
    if timeM > 1:
        timeM = "{} minutes ".format(timeM)
    elif timeM == 1:
        timeM = "{} minute ".format(timeM)
    elif timeM < 1:
        timeM = None
    #get time in hours and convert to days if over 24
    if timeH > 23:
        timeD = 0
        while timeH > 23:
            timeH = timeH - 24
            timeD += 1
    if timeH > 1:
        timeH = "{} hours ".format(timeH)
    elif timeH == 1:
        timeH = "{} hour ".format(timeH)
    elif timeH < 1:
        timeH = None

    if timeD > 1:
        timeD = "{} days ".format(timeD)
    elif timeD == 1:
        timeD = "{} day ".format(timeD)
    elif timeD < 1:
        timeD = None


    if timeS != None:
        if timeM != None or timeH != None or timeD != None:
            timeS = "and {}".format(timeS)
    elif timeM != None and timeH != None or timeD != None and timeS == None:
        timeM = "and {}".format(timeM)
    elif timeH != None and timeD != None and timeS == None and timeM == None:
        timeH = "and {}".format(timeH)

    if timeD != None:
        time = time + timeD
    if timeH != None:
        time = time + timeH
    if timeM != None:
        time = time + timeM

    if timeS != None:
        time = time + timeS

    return time

def get_picture(query, type):
    #base url variable.
    imgurl = "https://api.imgur.com/3/"
    #import api key.
    clientid = open("clientid").read()
    #convert query for url format.
    query = urllib.parse.quote(query)

    #check which type of query
    if type == "random":
        imgurl = imgurl + "gallery/r/" + query
    elif type == "search":
        imgurl = imgurl + "gallery/search/?q=" + query
    else:
        errcode = "1. Invalid Search Type"
        return errcode

    data = requests.get(imgurl, headers={"Authorization" : "Client-ID {}".format(clientid)}).json()
    try:
        value = random.choice(data["data"])
        return json.dumps(value["link"]).replace('"', '')
    except:
        errcode = "1. Unable to find image in {}, please try again.".format(type)
        return errcode

def get_joke():
    """Grab random joke from JD joke file"""
    jokes = open("jd.txt", "r")
    jokes = jokes.readlines()
    return random.choice(jokes)

def search_db(name):
    """search dynamodb for any records with the name that matches, grab random one and return"""
    #Making name lowercase to match db standards
    name = name.lower()
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('pictures')
    response = table.query(
        KeyConditionExpression=Key('name').eq(name)
    )
    try:
        url = random.choice(response['Items'])
        return url['url']
    except:
        pe = "#na"
        ean = {"#na" : "name",}
        response = table.scan(
            ProjectionExpression=pe,
            ExpressionAttributeNames=ean
            )
        names = []
        for name in response['Items']:
            names.append(name['name'])
        uniquelist = set(names)
        newresponse = list(uniquelist)
        newresponse = "\n".join(newresponse)
        return newresponse

def add_db(name, url):
    """adds picture to database with url name as the key pair value"""
    #Checking to make sure the string is only alphabetic.
    if name.isalpha() is not True:
        return "1. Name contains invalid characters"
    #Making name lowercase to match db standards
    if url.startswith('http') is True or url.startswith('www') is True:
        pass
    else:
        return '1. URL appears to be invalid, try again'
    name = name.lower()
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('pictures')
    response = table.put_item(
        Item={
            'name' : name,
            'url' : url
        }
    )
    return response['ResponseMetadata']['HTTPStatusCode']
