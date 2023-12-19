r"""
This script uses the bahai.works api to login and add author pages from 
needed_authors.txt, a file which should look something like this:

Created author Everett Tabor Gamage (Q811)
Created author A. G. B. (Q831)
Created author Philip Nash (Q834)

Be sure to replace your username and password below.

Usage: python api_addpages_works.py
"""

import requests
import re

def process_line(line):
    match = re.search(r'Created author (.*?) \((Q\d+)\)', line)
    if match:
        return match.group(1), match.group(2)  # Name, Identifier
    return None, None

def format_author_page(name, identifier):
    return f"""{{{{author2|wb={identifier}}}}}

===Articles===
====World Order====
<section begin=wo_article/>
{{{{#invoke:WorldOrder|getArticlesByAuthor|{identifier}}}}}
<section end=wo_article/>
__NOTOC__
"""

def get_csrf_token(session, api_url):
    # Get login token
    login_token_response = session.get(api_url, params={
        'action': 'query',
        'meta': 'tokens',
        'type': 'login',
        'format': 'json'
    })
    login_token = login_token_response.json()['query']['tokens']['logintoken']

    # Perform login
    login_response = session.post(api_url, data={
        'action': 'login',
        'lgname': 'David',
        'lgpassword': 'replaceme',
        'lgtoken': login_token,
        'format': 'json'
    })

    # Get CSRF token
    csrf_token_response = session.get(api_url, params={
        'action': 'query',
        'meta': 'tokens',
        'format': 'json'
    })
    return csrf_token_response.json()['query']['tokens']['csrftoken']

def create_page(session, api_url, title, content, csrf_token):
    create_params = {
        'action': 'edit',
        'title': title,
        'text': content,
        'token': csrf_token,
        'format': 'json'
    }
    return session.post(api_url, data=create_params).json()

# Main process
api_url = 'https://bahai.works/api.php'
session = requests.Session()
csrf_token = get_csrf_token(session, api_url)

input_file = 'needed-authors.txt'
with open(input_file, 'r') as file:
    for line in file:
        name, identifier = process_line(line)
        if name and identifier:
            page_title = f"Author:{name}"
            page_content = format_author_page(name, identifier)
            response = create_page(session, api_url, page_title, page_content, csrf_token)
            if 'error' in response:
                print(f"Error creating page for {name}: {response['error']}")
            else:
                print(f"Page created for {name}: {response}")

