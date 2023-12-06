#!/usr/bin/env python3
r"""
This script is adapted from replace.py, however text and a prompt are 
sent to ChatGPT who will make corrections and write them to the wiki.

The section below after " {"role": "system", "content":..." is where you define
the prompt that you want ChatGPT to follow while making corrections.

Be sure to experiment with different ChatGPT models.

This script was written by ChatGPT also. 
"""
#
# (C) Pywikibot team, 2004-2023
#
# Distributed under the terms of the MIT license.
#
import re
import requests
import pywikibot
from pywikibot import pagegenerators, textlib
from pywikibot.bot import ExistingPageBot, SingleSiteBot
from pywikibot.exceptions import InvalidPageError
from pywikibot.backports import List, Tuple

api_key = 'enter-your-api-key'

docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}

def get_chatgpt_response(api_key, message):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Correct mistakes that were introduced because of OCR software errors. Fix diacritic marks in Persian translitarted words. Do not make any corrections to text between two curly brackets. Be sure to correct 'Abdu'l-Bahá or any variations to ‘Abdu’l-Bahá. Use ‘ and ’ characters where appropriate and not '. Bahá’í is correct but Bahá'í is not."},
            message
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None

class ReplaceRobot(SingleSiteBot, ExistingPageBot):

    def __init__(self, generator, site, **kwargs):
        self.available_options.update({
            'addcat': None,
            'allowoverlap': False,
            'quiet': False,
            'recursive': False,
            'sleep': 0.0,
            'summary': None,
        })
        super().__init__(generator=generator, site=site, **kwargs)

    def treat(self, page) -> None:
        try:
            original_text = page.text
        except InvalidPageError as e:
            pywikibot.error(e)
            return

        # ChatGPT integration
        chatgpt_message = {"role": "user", "content": original_text}
        chatgpt_response = get_chatgpt_response(api_key, chatgpt_message)
        if chatgpt_response:
            new_text = chatgpt_response  # Replace or modify this line as needed
        else:
            pywikibot.error("Failed to get response from ChatGPT")
            return

        if new_text != original_text:
            self.userPut(page, original_text, new_text,
                         summary="Text modified using ChatGPT")

def main(*args):
    local_args = pywikibot.handle_args(args)
    genFactory = pagegenerators.GeneratorFactory()
    local_args = genFactory.handle_args(local_args)

    gen = genFactory.getCombinedGenerator(preload=True)
    if not gen:
        pywikibot.bot.suggest_help(missing_generator=True)
        return

    site = pywikibot.Site()
    bot = ReplaceRobot(gen, site)
    bot.run()

if __name__ == '__main__':
    main()
