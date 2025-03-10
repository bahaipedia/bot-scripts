r"""
This script uses the bahaidata.org api to login and add sitelinks 
from needed-books.txt, a file which should look something like this:

Created 239 Days (Q6135)

Be sure to replace your username and password below.

Usage: python api_addsitelinks_data-bookformat.py
"""

import requests
import re

# Parameters for your Wikibase instance
api_url = 'https://bahaidata.org/api.php'
username = 'changeme'
password = 'changeme'

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

# Read the list of books from the file and set sitelinks
with open('needed-books.txt', mode='r', encoding='utf-8') as file:
    lines = file.readlines()

successful_lines = []

for line in lines:
    match = re.search(r'Created (.*?) \((Q\d+)\)', line)
    if match:
        book_title = match.group(1)
        item_id = match.group(2)
        page_title = book_title
        response = set_sitelink(session, item_id, 'works', page_title, csrf_token)

        # If successful, add line to successful_lines
        if 'success' in response and response['success'] == 1:
            successful_lines.append(line)
        else:
            print(f"Error setting sitelink for {book_title} ({item_id}):", response)

# Rewrite the file excluding successful lines
with open('needed-books.txt', mode='w', encoding='utf-8') as file:
    for line in lines:
        if line not in successful_lines:
            file.write(line)
