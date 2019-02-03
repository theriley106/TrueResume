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

#Function to censor words based on coordinates in image
def classify(censorList, filename, saveas):

  im = Image.open(filename).convert('RGBA')

  for i in range(len(censorList)):
    draw = ImageDraw.Draw(im)
    draw.rectangle(((censorList[i]['x1'], censorList[i]['y1']), 
    (censorList[i]['x2'], censorList[i]['y2'])), fill='#000000')
    del draw

  im.save(saveas)

#Function that calls aws api and returns comprehension on text
def comprehend(text):
  comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')
  text.replace("\n", ' ')
  print('Calling DetectEntities')
  print(json.dumps(comprehend.detect_entities(Text=text, LanguageCode='en'), sort_keys=True, indent=4))
  print('End of DetectEntities\n')

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
  comprehend(toAWS)

gcp('resumes/ChrisResume.png')
