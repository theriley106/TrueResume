#Python program to classify specified words in pdf/png files.
#Hayden Riewe, Chris Lambert, Ayush Petigara
#Repo: https://github.com/theriley106/TrueResume

from PIL import Image, ImageDraw
import sys

#Function to censor words based on coordinates in image
def classify(censorList, filename, saveas):

  im = Image.open(filename).convert('RGBA')

  for i in range(len(censorList)):
    draw = ImageDraw.Draw(im)
    draw.rectangle(((censorList[i]['x1'], censorList[i]['y1']), 
    (censorList[i]['x2'], censorList[i]['y2'])), fill='#000000')
    del draw

  im.save(saveas)