# importing modules
import pandas as pd
import requests
from bs4 import BeautifulSoup

# making url variable
url = ''
# get request to the url
response = requests.get(url)
# scrapping the content
soup = BeautifulSoup(response.content,'lxml')
# finds the first table
# change the number of table
table = soup.find_all('table')[0]
# using pandas parses the html tables found in the content
df = pd.read_html(str(table))
# this stores the data in the json file
with open('internship_data.json', 'w') as f:
    f.write(df[0].to_json(orient='records', lines=True))
