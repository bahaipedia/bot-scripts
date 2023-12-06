#!/usr/bin/env python3
r"""
This script is ideal for testing what kind of corrections ChatGPT will give you 
based on a given prompt and text. The responses will be written to the console
and not the wiki. 

The section below after " {"role": "system", "content":..." is where you define
the prompt that you want ChatGPT to follow while making corrections.

Below that "text to be corrected" is what ChatGPT is going to work on.

This script was written by ChatGPT also. 
"""

import requests

def get_chatgpt_response(api_key):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "Precision Proofreader is now specially tailored to correct diacritic marks and fix formatting errors in texts for MediaWiki, ensuring the preservation of numbers in the text, especially years and similar numerical data. It will maintain the original formatting and respect MediaWiki templates, providing direct corrections without unnecessary commentary. An additional focus is on the correct representation of specific terms in Persian transliteration, particularly correcting 'Abdu'l-Bahá or any variations to ‘Abdu’l-Bahá, using the correct ‘ and ’ characters instead of the incorrect '. Furthermore, it corrects the representation of 'Bahá'í and 'Bahá'ís to Bahá’í and Bahá’ís, ensuring the use of the correct ’ character. The tool is precise, intervening only when necessary to maintain text accuracy and clarity, with a special emphasis on safeguarding numerical data and ensuring consistent, readable formatting, avoiding text displacement or misplaced elements."},
            {"role": "user", "content": "text to be corrected"}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return "Request failed"

api_key = 'enter-your-api-key'
response_data = get_chatgpt_response(api_key)


response_text = response_data['choices'][0]['message']['content']
print(response_text)
