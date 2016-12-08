from flask import Flask, request
import json
import requests
import urllib

#for getting logs
import sys
import logging

from wit import Wit
import time

#import aiml

#grocery list class
from bstest6_3 import foodSites

import os

app = Flask(__name__)

#alice
#kernel = aiml.Kernel()
#kernel.learn("std-startup.xml")
#kernel.respond("load aiml b")

#logs errors for heroku 
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

site = ''
loc = False
lat = ''
lon = ''

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.
PAT = str(os.environ.get('FBKey',3))

#verify
@app.route('/', methods=['GET'])
def handle_verification():
  print "Handling Verification."
  if request.args.get('hub.verify_token', '') == 'my_voice_is_my_password_verify_me':
    print "Verification successful!"
    return request.args.get('hub.challenge', '')
  else:
    print "Verification failed!"
    return 'Error, wrong validation token'


#messaging
@app.route('/', methods=['POST'])
def handle_messages():
  #variables
  global site
  global loc
  global lat 
  global lon
  
  context0 = {}
  count = 0
  
  print "Handling Messages"
  payload = request.get_data()
  print payload
  data = json.loads(payload)
  msgev = data["entry"][0]["messaging"]
  for event in msgev:
    if "message" in event:
      if "attachments" in event["message"]:
        for atta in event["message"]["attachments"]:
          if "payload" in atta:
            if "coordinates" in atta["payload"]:
              print(atta["payload"]["coordinates"])
              lat = atta["payload"]["coordinates"]["lat"]
              lon = atta["payload"]["coordinates"]["long"]
              f =  open("geo.txt", "w")
              f.write(str(lat)+","+str(lon))
              send_message(PAT, event["sender"]["id"], str(atta["payload"]["coordinates"]))
              send_message(PAT,event["sender"]["id"], "Coordinates Recieved")
              loc = True
              return "ok"
  
  #checks if chat option is on or not
  for sender, message in messaging_events(payload):
      
      print "Incoming from %s: %s" % (sender, message)
      print type(message)
      resp = client.message(message) #get response from wit.ai
      print(resp)
      
      #decides what type of response it is
      if u'entities' in resp:
        resp = resp[u'entities']
        if u'intent' in resp:
          resp = resp[u'intent']
        else:
          send_message(PAT, sender, "I'm sorry. I couldn't understand you. Please rephrase that.")
          return "ok"
      else:
        send_message(PAT, sender, "I'm sorry. I couldn't understand you. Please rephrase that.")
        return "ok"
        
      #if response is understood, get it
      resp = resp[0]
      print ("Response type is.... "+resp[u'value'])
      
      
      #id type of response and run correct method
      if u'value' in resp:
        
        #grocery response to get list of groceries. From imported class
        if resp[u'value'] == "grocery":
          message = get_cooking()
          while( len(message) > 300):
            msg2 = message[:300]
            message = message[300:]
            send_message(PAT, sender, msg2)
          send_message(PAT, sender, message)
          send_message(PAT, sender, site) 
          
        elif resp[u'value'] == "beef":
          message1 = get_cookingspec("beef")
          text1 = message1.splitlines()
          for message in text1:
            while( len(message) > 300):
              msg2 = message[:300]
              message = message[300:]
              send_message(PAT, sender, msg2)
            send_message(PAT, sender, message)
            
          send_message(PAT, sender, site)
          
        elif resp[u'value'] == "chicken":
          message1 = get_cookingspec("chicken")
          text1 = message1.splitlines()
          for message in text1:
            while( len(message) > 300):
              msg2 = message[:300]
              message = message[300:]
              send_message(PAT, sender, msg2)
            send_message(PAT, sender, message)
            
          send_message(PAT, sender, site)
          
        elif resp[u'value'] == "pasta":
          message1 = get_cookingspec("pasta")
          text1 = message1.splitlines()
          for message in text1:
            while( len(message) > 300):
              msg2 = message[:300]
              message = message[300:]
              send_message(PAT, sender, msg2)
            send_message(PAT, sender, message)
            
          send_message(PAT, sender, site)
          
        elif resp[u'value'] == "pork":
          message1 = get_cookingspec("pork")
          text1 = message1.splitlines()
          for message in text1:
            while( len(message) > 300):
              msg2 = message[:300]
              message = message[300:]
              send_message(PAT, sender, msg2)
            send_message(PAT, sender, message)
            
          send_message(PAT, sender, site)
            
        #greetings response. Usually used to start up
        elif resp[u'value'] == "greetings":
          print("This resp greetings RIGHT HERE")
          resp = client.converse('my-user-session-42',message, context0)
          print("This resp greetings ")
          print (resp)
          
          while('msg' not in resp):
            resp = client.converse('my-user-session-42',message, context0)
            print ("This resp HERE ")
            print(resp)
            
          print("the msg is "+resp['msg'])
          message = str(resp["msg"])
          print("Trying to send...")
          send_message(PAT, sender, message)
          print("Probably sent")
        
            
            
        #catch all for other intents  
        else:
          print("Else")
          resp = client.converse('my-user-session-42',message, context0)
          while('msg' not in resp and count <=10):
            resp = client.converse('my-user-session-42',message, context0)
            print ("This resp HERE ")
            print(resp)
              
          print("the msg is "+resp['msg'])
          message = str(resp["msg"])
          print("Trying to send...")
          send_message(PAT, sender, message)
  return "ok"

#Sorts messages
def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"]:
      yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
    else:
      yield event["sender"]["id"], "I can't echo this"


#Send the message. Limited to 320 char
def send_message(token, recipient, text):
  """Send the message text to recipient with id recipient.
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": text.decode('unicode_escape')}
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

#wit ai method not implemented
def merge():
    return 0

#wit ai method not implemented (important probably)
def error():
    return 0

#wit ai method works
def say(id, dict, response):
    print ("id " +id)
    print (dict)
    print ("respo "+response)
    return response
    
#wit ai send method
def send(request, response):
    print(response['text'])

#wit ai function method
def my_action(request):
    print('Received from user...', request['text'])


#works fine so far. Can't run from wit.ai
def get_cooking():
    print("Inside grocery")
    global site
    context = ""
    cook = foodSites()
    cook.initList("beef")
    context= cook.getIngred()
    site = cook.getSites()
    return context

#works fine so far. Can't run from wit.ai
def get_cookingspec(item):
    print("Inside grocery spec "+item)
    global site
    context = ""
    cook = foodSites()
    cook.initList(item)
    context= cook.getIngred()
    site = cook.getSites()
    return context

  
  
#wit ai action list
actions = {
    'send': send,
    'say': say,
    'merge': merge,
    'error': error,
    'my_action': my_action,
}

#server access
client = Wit(access_token=str(os.environ.get('ATKey',3)), actions=actions)


if __name__ == '__main__':
  app.run()
