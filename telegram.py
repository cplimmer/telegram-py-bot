import urllib.parse
import random
import json
import requests
import boto3

APIKEY = open("apikey").read()


URL = "https://api.telegram.org/bot{}/".format(APIKEY)


def api_call(url):
    """Taking telegrambot URL and making API call using requests"""
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def send_message(text, chat_id, reply_id=0):
    """sending telegram message to use with text and chat_id as required params"""
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
    jokes = open("jd.txt", "r")
    jokes = jokes.readlines()
    return random.choice(jokes)
    