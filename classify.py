#Python program to classify specified words in pdf/png files.
#Hayden Riewe, Chris Lambert, Ayush Petigara
#Repo: https://github.com/theriley106/TrueResume

from PIL import Image, ImageDraw
import sys
import boto3
import json
import io
import os
from google.cloud import vision
from google.cloud.vision import types
from google.protobuf.json_format import MessageToJson
censorList = []
#Process image with google ocr api and get list of all text and location
def gcp(imageName):    
  # Instantiates a client
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

  keywords = findKeywords()

  response = MessageToJson(response)
  response = json.loads(str(response))

  #print(json.dumps(response, indent=4))

  with open('gcpResponse.json', 'w') as outfile:
    json.dump(response, outfile, indent=4)

  with open('gcpResponse.json') as f:
    gcpResponse = json.load(f)

  
  keywords.append('Science')

  for i in range(len(keywords)):
    for values in gcpResponse['textAnnotations']:
      #print(values['description'] + "VALUES " + keywords[i] + "KEYWORDS")
      if values['description'].lower() == keywords[i].lower():
        vertices = values['boundingPoly']['vertices']
        first = vertices[0]
        third = vertices[2]
        wordDict = {"x1": first['x'], "y1": first['y'], 'x2': third['x'], 'y2': third['y']}
        censorList.append(wordDict)
  # for i in range(len(censorList)):
  #   print(censorList[i])

#pull keywords from returned aws json, populate list
def findKeywords():
  with open('awsResponse.json') as f:
    awsResponse = json.load(f)

  valsToCensor = []

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

  im.save(saveas)

def do_all(fileName, saveAs):
  gcp(fileName)
  classify(censorList, fileName, saveAs)


if __name__ == "__main__":
  do_all('resumes/HaydenRieweResume.jpeg', "PLEASEWORK2.png")
