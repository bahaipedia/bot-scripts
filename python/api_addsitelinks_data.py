r"""
This script uses the bahaidata.org api to login and add sitelinks 
from needed_authors.txt, a file which should look something like this:

Created author Everett Tabor Gamage (Q811)
Created author A. G. B. (Q831)
Created author Philip Nash (Q834)

Be sure to replace your username and password below.

Usage: python api_addsitelinks_data.py
"""

import requests
import re

# Parameters for your Wikibase instance
api_url = 'https://bahaidata.org/api.php'
username = 'David'
password = 'replaceme'

# Function to set a sitelink for a given item
def set_sitelink(session, item_id, site_id, page_title, csrf_token):
    params = {
        'action': 'wbsetsitelink',
        'id': item_id,
        'linksite': site_id,
        'linktitle': page_title,
        'token': csrf_token,
        'format': 'json'
    }
    response = session.post(api_url, data=params)
    return response.json()

# Start a session to maintain cookies
session = requests.Session()

# Step 1: Get login token
login_token_response = session.get(api_url, params={
    'action': 'query',
    'meta': 'tokens',
    'type': 'login',
    'format': 'json'
})
login_token = login_token_response.json()['query']['tokens']['logintoken']

# Step 2: Perform login
login_response = session.post(api_url, data={
    'action': 'login',
    'lgname': username,
    'lgpassword': password,
    'lgtoken': login_token,
    'format': 'json'
})

# Step 3: Get CSRF token
csrf_token_response = session.get(api_url, params={
    'action': 'query',
    'meta': 'tokens',
    'format': 'json'
})
csrf_token = csrf_token_response.json()['query']['tokens']['csrftoken']

# Read the list of authors from the file and set sitelinks
with open('needed-authors.txt', 'r') as file:
    for line in file:
        match = re.search(r'Created author (.*?) \((Q\d+)\)', line)
        if match:
            author_name = match.group(1)
            item_id = match.group(2)
            page_title = f'Author:{author_name}'
            response = set_sitelink(session, item_id, 'works', page_title, csrf_token)

            # Print only if there's an error
            if 'success' not in response or response['success'] != 1:
                print(f"Error setting sitelink for {author_name} ({item_id}):", response)


# working so let's keep it just in case
#with open('needed-authors.txt', 'r') as file:
#    for line in file:
#        match = re.search(r'Created author (.*?) \((Q\d+)\)', line)
#        if match:
#            author_name = match.group(1)
#            item_id = match.group(2)
#            page_title = f'Author:{author_name}'
#            response = set_sitelink(session, item_id, 'works', page_title, csrf_token)
#            print(f"Set sitelink for {author_name} ({item_id}):", response)
