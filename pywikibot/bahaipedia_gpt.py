#!/usr/bin/env python3
r"""
This script is adapted from replace.py, however text and a prompt are 
sent to ChatGPT who will extract data and write the output to a json file.

The section below after " {"role": "system", "content":..." is where you define
the prompt that you want ChatGPT to follow while making corrections.

run with: pwb bahaipediagpt -cat:Biographies
or run: pwb bahaipediagpt -page:Peter_Khan

This script was written by ChatGPT also. 
"""
#
# (C) Pywikibot team, 2004-2023
#
# Distributed under the terms of the MIT license.
#
#!/usr/bin/env python3
import os
import time
import json
import requests
import pywikibot
from pywikibot import pagegenerators
from requests.exceptions import RequestException
import sys
import re

API_KEY = 'sk-xxxx'

def get_chatgpt_response(api_key, message, max_retries=3, retry_delay=30):
    """Interact with ChatGPT API to extract structured JSON."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4-turbo",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are extracting structured Baha’i-related biographical data from Wikipedia-style articles. "
                    "Your goal is to return a JSON object with any of the following fields **if identifiable from the text**. "
                    "Even if the article doesn't have a template, you should analyze the full text carefully and infer data when appropriate. "
                    "Do not guess—only include fields that are clearly supported by the text, either explicitly or by strong implication.\n\n"
                    "Your output must be a single valid JSON object and contain only the following keys if relevant:\n"
                    "- birth_name (Source page specifcally mentions a different birth name)\n"
                    "- birth_date\n"
                    "- birth_place\n"
                    "- declaration_date (when the person became a Bahá’í, if known)\n"
                    "- declaration_place\n"
                    "- death_date\n"
                    "- death_place\n"
                    "- nationality\n"
                    "- lsa_member (list of places/years if known)\n"
                    "- abm (location and/or years if known)\n"
                    "- nsa_member (list of Assemblies/years if known)\n"
                    "- counsellor (region/years)\n"
                    "- itc_member (years of service)\n"
                    "- uhj_member (years of service)\n"
                    "- custodian (years years of service)\n"
                    "- appointedby (Only used in conjunction with the position Hand of the Cause of God)\n\n"
                    "Examples:\n"
                    "- If the article says someone 'was elected to the National Spiritual Assembly of Canada in 1953', return:\n"
                    "\"nsa_member\": [{\"assembly\": \"Canada\", \"start_date\": \"1953\"}] "
                    "- If the article says they were a 'counsellor for Africa from 1981 to 1986', return:\n"
                    "\"counsellor\": [{\"region\": \"Africa\", \"start_date\": \"1981\", \"end_date\": \"1986\"}] "
                    "- If it says they were a member of a Local Spiritual Assembly of Manchester, return:\n"
                    "\"lsa_member\": [{\"assembly\": \"Manchester\"}] "
                    "- If no info is available on a field, omit it.\n\n"
                    "Output only the JSON object and nothing else."
                )
            },
            {
                "role": "user",
                "content": message
            }
        ]
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                print(f"API error {response.status_code}: {response.text}")
                break  # Avoid retrying on bad request
        except RequestException as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Giving up.")
    return "{}"  # Fallback to empty JSON

class ExtractJSONBot:
    def __init__(self, generator, output_dir="bios_output"):
        self.generator = generator
        self.site = pywikibot.Site()
        self.auto_confirm = False
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def confirm_continue(self, message):
        """Ask user whether to proceed with the current page."""
        if self.auto_confirm:
            return "y"

        choice = input(f"{message} (y/n/a/q): ").strip().lower()
        if choice == 'y':
            return "y"
        elif choice == 'a':
            self.auto_confirm = True
            return "y"
        elif choice == 'n':
            return "n"
        elif choice == 'q':
            return "q"  # Quit
        else:
            print("Invalid choice. Defaulting to 'y'.")
            return "y"

    def extract_json(self, text: str, title: str) -> dict:
        """Send full article to ChatGPT and return extracted JSON."""
        print(f"Sending article '{title}' to ChatGPT...")
        gpt_output = get_chatgpt_response(API_KEY, text)
        try:
            return json.loads(gpt_output)
        except json.JSONDecodeError:
            print("⚠️ ChatGPT returned invalid JSON. Saving raw response.")
            return {"raw_response": gpt_output}

    def run(self):
        """Run the bot over pages."""
        pages_processed = 0

        for page in self.generator:
            decision = self.confirm_continue(f"Process page '{page.title()}'?")
            if decision == "n":
                continue
            elif decision == "q":
                print("Quitting the bot.")
                break
            elif decision != "y":
                print("Exiting.")
                break

            try:
                original_text = page.text
                if not original_text.strip():
                    print(f"⚠️ Page '{page.title()}' is empty.")
                    continue

                json_data = self.extract_json(original_text, page.title())

                # Create a safe filename by replacing spaces and removing special characters
                filename = re.sub(r'[^\w.-]', '_', page.title().lower()) + ".json"
                filepath = os.path.join(self.output_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)

                pages_processed += 1
                print(f"✅ Saved: {filename}")
            except Exception as e:
                print(f"Error on '{page.title()}': {e}")

        print(f"\nDone. Processed {pages_processed} page(s).")

if __name__ == "__main__":
    site = pywikibot.Site()

    if len(sys.argv) < 2:
        print("Usage: pwb bahaipediagpt -cat:\"Biographies\" or -page:\"Page Title\"")
        sys.exit(1)

    arg = sys.argv[1]

    if arg.startswith("-cat:"):
        category_name = arg[len("-cat:"):]
        cat = pywikibot.Category(site, f"Category:{category_name}")
        gen = pagegenerators.CategorizedPageGenerator(cat)
    elif arg.startswith("-page:"):
        page_title = arg[len("-page:"):]
        page = pywikibot.Page(site, page_title)
        gen = iter([page])  # Create a generator with a single page
    else:
        print("Invalid argument. Use -cat:\"CategoryName\" or -page:\"Page Title\"")
        sys.exit(1)

    bot = ExtractJSONBot(gen)
    bot.run()
