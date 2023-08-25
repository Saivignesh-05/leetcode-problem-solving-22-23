import requests
import pandas as pd
from datetime import datetime
import os
from pathlib import Path
import json
import re
from time import sleep

script_dir = Path( __file__ ).parent.absolute()

# First create info.json file
'''
The program needs the info.json file in the current working directory.
Create this file.
{
  "timestamp": 0,
  "LEETCODE_SESSION": "LEETCODE_SESSION from browser cookies",
  "csrftoken": "csrftoken from browser cookies"
}
'''

# The LEETCODE_SESSION and csrftoken can be found by using a cookie editor extension on a browser.
# Use it when opening the leetcode.com when logged in.

# From within your directory run
# python ../lc.py




problems_url='https://leetcode.com/problems/'

code_path="codes/"
if not os.path.exists(code_path):
   os.makedirs(code_path)

info_path="info.json"
if not os.path.exists(info_path):
  print('info.json does not exist')
  exit(1)

num_retries = 10
retry_wait=5

submissions_path="README.adoc"

note_replaces = {"\n":" +\n","|":"\|"}

def multiple_replace(dict, text):
  # Create a regular expression  from the dictionary keys
  regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))

  # For each match, look-up corresponding value in dictionary
  return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text) 


colour_map = {"Easy":"green-background","Medium":"yellow-background","Hard":"red-background"}

session = requests.Session()
prv_timestamp=0

with open(info_path,"r") as f:
  info = json.load(f)
  session.cookies['LEETCODE_SESSION']=info['LEETCODE_SESSION']
  session.cookies['csrftoken']=info['csrftoken']
  prv_timestamp=info['timestamp']


graphql_url='https://leetcode.com/graphql/'
headers = {
    'Content-Type': 'application/json',
}

data_submission_id={'query':"""
query submissionList($offset: Int!, $limit: Int!, $questionSlug: String!) {
     submissionList(
    offset: $offset
    limit: $limit
    questionSlug: $questionSlug
  ) {
    hasNext
    submissions {
      id
      timestamp
      statusDisplay
      title
      titleSlug
      lang
      notes
    }
  }
}
""",'variables':{'offset':0,'limit':3,'questionSlug':""}}


Q_title={"query":"""
query ($titleSlug: String!) {
    question(titleSlug: $titleSlug) {
        questionFrontendId
        title 
        difficulty
        topicTags {
            name
        }
      }
  }
""",'variables':{'titleSlug':"two-sum"}}

data_sumbission_info={'query':"""
query submissionDetails($submissionId: Int!) {
  submissionDetails(submissionId: $submissionId) {
    runtimeDisplay
    memoryDisplay
    code
  }
}
""",'variables':{"submissionId": 1022704592}}

upt_timestamp=prv_timestamp
offset=0
limit=10
hasNext=True
subs=[]
total_submissions=0
accepted_submissions=0
while hasNext:
  data_submission_id['variables']['offset']=offset
  data_submission_id['variables']['limit']=limit

  for i in range(num_retries):
    response = session.post(graphql_url, headers=headers, json=data_submission_id)
    if response.status_code==200:
      break
    print("Failed with code {} \n Retrying {} for submission list after {} seconds.".format(response.status_code,graphql_url,retry_wait))
    sleep(retry_wait)
  else:
    print("Retries failed")
    exit(2)
  data=response.json()
  hasNext=data['data']['submissionList']['hasNext']
  submissions_data=data['data']['submissionList']['submissions']
  offset+=limit
  for x in submissions_data:
    x['timestamp']=int(x['timestamp'])
    upt_timestamp=max(upt_timestamp,x['timestamp'])
    if x['timestamp']<=prv_timestamp:
      hasNext=False
      break
    row=dict()
    total_submissions+=1
    if x['statusDisplay']!='Accepted':
      continue
    accepted_submissions+=1
    Q_title['variables']['titleSlug']=x['titleSlug']

    for i in range(num_retries):
      response = session.post(graphql_url, headers=headers, json=Q_title)
      if response.status_code==200:
        break
      print("Failed with code {} \n Retrying {} for submission list after {} seconds.".format(response.status_code,graphql_url,retry_wait))
      sleep(retry_wait)
    else:
      print("Retries failed")
      exit(2)
    Q_title_data = response.json()['data']['question']
    Q_title_data['topicTags']=[topic['name'] for topic in Q_title_data['topicTags']]
    data_sumbission_info['variables']['submissionId']=x['id']

    for i in range(num_retries):
      response = session.post(graphql_url, headers=headers, json=data_sumbission_info)
      if response.status_code==200:
        break
      print("Failed with code {} \n Retrying {} for submission list after {} seconds.".format(response.status_code,graphql_url,retry_wait))
      sleep(retry_wait)
    else:
      print("Retries failed")
      exit(2)
    submission_details=response.json()['data']['submissionDetails']

    row['Date']=datetime.fromtimestamp(x['timestamp']).strftime("%d/%m/%Y")
    row['id']=Q_title_data['questionFrontendId']
    row['Title']=Q_title_data['title']
    row['titleSlug']=x['titleSlug']
    row['Difficulty']=Q_title_data['difficulty']
    row['Tags']=Q_title_data['topicTags']
    row['Notes']=multiple_replace(note_replaces,x['notes'])
    print(i,"\t",row['Title'])
    with open(os.path.join(code_path,x['id']+"_"+x['titleSlug']+"."+x['lang']),"w") as f:
      f.write(submission_details['code'])
    subs.append(row)
print(' New Submissions \t{} \n Accepted submissions \t{}'.format(total_submissions,accepted_submissions))
subs.reverse()
isExist=os.path.exists(submissions_path)
with open(submissions_path,"a+") as f:
  if not isExist:
    f.write("""
[cols="1,3,1,3,6"]
[options="header"]
|=========================================================
| Date | Title | Difficulty | Topics | Notes
    """)
  for submission in subs:
    tags=''
    for tag in submission['Tags']:
      if tags!='':
        tags+=' , '
      tags+=tag
    f.write("| {} | {}{}[{}.{}] | [.{}. {}]#*{}*# | {} | {}".format(submission['Date'],
            problems_url,
            submission['titleSlug'],
            submission['id'],
            submission['Title'],
            colour_map[submission['Difficulty']],
            "black",
            submission['Difficulty'],
            tags,submission['Notes']))
info['timestamp']=upt_timestamp
with open(info_path,"w")as jsonFile:
  json.dump(info,jsonFile)