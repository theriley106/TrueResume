#Python program to classify specified words in pdf/png files.
#Hayden Riewe, Chris Lambert, Ayush Petigara
#Repo: https://github.com/theriley106/TrueResume

from PIL import Image, ImageDraw
import sys
import re
import boto3
import json
import io
import os
from google.cloud import vision
from google.cloud.vision import types
from google.protobuf.json_format import MessageToJson

#Global variables needed for call in main
censorList = []
fratList = []
soroList = []

BLACKLIST = ["new", "in", "of", "dean", "deans", "dean's", "professional", "and", "north", "university", "college", "society"]

#Strip newlines from gcp response
def strip_newline(stringVal):
  if '@' in stringVal:
    return stringVal.partition("@")[0]
  return ' '.join(re.findall("\w+", stringVal))

#Process image with Google OCR API and get list of all text and locations of words.
def gcp(imageName):    
  #Instantiates a client
  client = vision.ImageAnnotatorClient()

  #The name of the image file to annotate
  file_name = os.path.join(
      os.path.dirname(__file__),
      imageName)

  # Loads the image into memory
  with io.open(file_name, 'rb') as image_file:
      content = image_file.read()

  image = types.Image(content=content)

  # Performs document text detection on the image file
  response = client.document_text_detection(image=image)

  #Strip response for just the body of the resume
  toAWS = str(response)
  toAWS = toAWS.split("}")[-2].partition(': "')[2][:-2].strip()

  ############################################################## 
  #Function that calls aws api and returns comprehension on text
  comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')
  toAWS.replace("\n", ' ')
  print('Calling DetectEntities')
  with open('awsResponse.json', 'w') as outfile:  
    json.dump(comprehend.detect_entities(Text=toAWS, LanguageCode='en'), outfile, sort_keys=True, indent=4)
  print('End of DetectEntities\n')

  #Open data for comparison to fraternities
  f = open('data/frats.txt')
  frats = f.read()

  #frats.replace('', ' ')
  for value in frats.split(','):
    for val in strip_newline(value.replace("'", "").strip().lower()).split():
      #print(val)
      if val.lower() not in BLACKLIST:
        fratList.append(val)
  f.close()

  #Open data for comparison to sororities
  f = open('data/Sororities.txt')
  soros = f.read()

  #soros.replace('', ' ')
  for value in soros.split(','):
    for val in strip_newline(value.replace("'", "").strip().lower()).split():
      #print(val)
      if val.lower() not in BLACKLIST:
        soroList.append(val)
  f.close()

  #print(soroList)
  
  response = MessageToJson(response)
  response = json.loads(str(response))

  keywords = findKeywords()

  with open('gcpResponse.json', 'w') as outfile:
    json.dump(response, outfile, indent=4)

  with open('gcpResponse.json') as f:
    gcpResponse = json.load(f)

  for values in gcpResponse['textAnnotations']:
    #strip_newline(values['description'].lower()).split()
    if strip_newline(values['description'].lower()) in fratList or strip_newline(values['description'].lower()) in soroList:
      if strip_newline(values['description'].lower()) not in BLACKLIST:
        print(strip_newline(values['description'].lower()))
        keywords.append(values['description'])
      
  for i in range(len(keywords)):
    for values in gcpResponse['textAnnotations']:
      if values['description'].lower() == keywords[i].lower():
        vertices = values['boundingPoly']['vertices']
        first = vertices[0]
        third = vertices[2]
        wordDict = {"x1": first['x'], "y1": first['y'], 'x2': third['x'], 'y2': third['y']}
        censorList.append(wordDict)

#pull keywords from returned aws json, populate list
def findKeywords():

  valsToCensor = []

  with open('awsResponse.json') as f:
    awsResponse = json.load(f)

  for value in awsResponse['Entities']:
    if value['Type'] == "PERSON":
      for val in value['Text'].split():
        valsToCensor.append(val)

  return valsToCensor

def classify(censorList, filename, saveas):

  im = Image.open(filename).convert('RGBA')

  for i in range(len(censorList)):
    draw = ImageDraw.Draw(im)
    draw.rectangle(((censorList[i]['x1'], censorList[i]['y1']), 
    (censorList[i]['x2'], censorList[i]['y2'])), fill='#000000')
    del draw

  #im.save(saveas)
  im.show()

def do_gender(fileName, saveAs):
  gcp(fileName)
  classify(censorList, fileName, saveAs)

def do_race(fileName, saveAs):
  gcp(fileName)
  classify(censorList, fileName, saveAs)

def do_both(fileName, saveAs):
  gcp(fileName)
  classify(censorList, fileName, saveAs)


if __name__ == "__main__":
  do_gender('testResumes/sample_christy.jpeg', "PLEASEWORK.png")
