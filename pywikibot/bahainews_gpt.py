#!/usr/bin/env python3
r"""
This script is adapted from replace.py, however text and a prompt are 
sent to ChatGPT who will make corrections and write them to the wiki.

The section below after " {"role": "system", "content":..." is where you define
the prompt that you want ChatGPT to follow while making corrections.

run with: pwb bahainews_gpt.py -cat:"Baha'i News No 331"

Responsible for edits like this: https://bahai.media/index.php?title=File:Steel_shafts_for_concrete_pillars_of_Kampala_Temple,_1958.jpg&curid=15878&diff=135612&oldid=60149

This script was written by ChatGPT also. 
"""
#
# (C) Pywikibot team, 2004-2023
#
# Distributed under the terms of the MIT license.
#
import requests
import pywikibot
from pywikibot import pagegenerators

API_KEY = 'your-chat-gpt-api-key-here'

def get_chatgpt_response(api_key, message):
    """Interact with ChatGPT API to process text correction or modification."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4-turbo",
        "messages": [
            {"role": "system", "content": "The assistant is helping format image captions. First, the assistant places the following information at the top of the page: \"== File info ==\n{{cs\n| caption =\n| source =\n}}\n\n== File license ==\n{{Bn-excerpt}}\n\n\". Second, locate the caption and if it exists put it in the caption field. Third, locate the source and if it exists, place it in the source field. In the caption field, ensure correct transliterations for Bahá’í terms:  - Replace \"Baha'u'llah\" with \"Bahá’u’lláh.\"\n  - Replace \"Baha'is\" with \"Bahá’ís.\"\n  - Replace \"Bahá'í\" with \"Bahá’í.\"\n  - Replace \"Bahji\" with \"Bahjí.\"\n- If the caption is wrapped in quotation marks, remove them.\n\nFor the source field: If the source is in the format \"From BN [number] p [number],\" wrap it in the template {{bns|[number]|[number]}}.\n\nCategory Management:\n- Remove tags like [[Category:Baha'i News No xxx]] but preserve other category tags at the bottom of the page."},
            {"role": "user", "content": message}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return message  # Fallback to original content if API fails

class ReplaceBot:
    """A bot that processes replacements using ChatGPT."""
    def __init__(self, generator, summary: str = None):
        self.generator = generator
        self.summary = summary
        self.site = pywikibot.Site()
        self.auto_confirm = False  # Set to True if user chooses 'a' (automatic)

    def confirm_continue(self, message):
        """Prompt the user to confirm whether to continue, skip, or proceed automatically."""
        if self.auto_confirm:
            return "y"

        choice = input(f"{message} (y/n/a): ").strip().lower()
        if choice == 'y':
            return "y"
        elif choice == 'a':
            self.auto_confirm = True
            return "y"
        elif choice == 'n':
            return "n"  # Skip the current page
        else:
            print("Invalid choice. Defaulting to 'y'.")
            return "y"

    def apply_chatgpt_modification(self, text: str, page_title: str) -> str:
        """Apply modifications via ChatGPT API."""
        print(f"Requesting ChatGPT modification for page '{page_title}'")
        return get_chatgpt_response(API_KEY, text)

    def run(self):
        """Run the replacement bot."""
        pages_processed = 0
        for page in self.generator:
            decision = self.confirm_continue(f"Would you like to proceed with processing page '{page.title()}'?")
            if decision == "n":
                print(f"Skipping page: {page.title()}")
                continue  # Skip to the next page
            elif decision != "y":
                print("Stopping the bot.")
                break

            try:
                print(f"Processing page: {page.title()}")
                original_text = page.text
                new_text = self.apply_chatgpt_modification(original_text, page.title())
                if new_text != original_text:
                    self.save_page(page, new_text)
                    pages_processed += 1
            except Exception as e:
                print(f"Error processing page {page.title()}: {e}")

        if pages_processed == 0:
            print("No pages were modified.")
        else:
            print(f"Successfully processed {pages_processed} page(s).")

    def save_page(self, page, new_text):
        """Save changes to the page."""
        page.text = new_text
        try:
            page.save(summary=self.summary)
            print(f"Saved changes to page: {page.title()}")
        except Exception as e:
            print(f"Error saving page {page.title()}: {e}")

def list_category_pages(category):
    """Print a list of pages in the given category."""
    print(f"Listing pages in category: {category.title()}")
    pages = []
    try:
        generator = pagegenerators.CategorizedPageGenerator(category, recurse=False)
        for page in generator:
            print(f" - Found page: {page.title()}")
            pages.append(page)
    except Exception as e:
        print(f"Error retrieving pages from category: {e}")
    
    if not pages:
        print("No pages found in this category.")
    
    return pages

def main(*args: str) -> None:
    """Run the bot with category targeting and detailed debugging."""
    # Extract category from arguments if provided
    category_name = None
    for arg in args:
        if arg.startswith("-cat:"):
            category_name = arg[5:]

    if not category_name:
        print("Error: Please specify a category with -cat:\"CategoryName\"")
        return

    # Set up the Pywikibot site and category generator
    site = pywikibot.Site()
    category = pywikibot.Category(site, category_name)

    try:
        # List and retrieve pages in the category
        pages = list_category_pages(category)
        
        if not pages:
            print("No pages found in the specified category.")
            return

        print(f"Found {len(pages)} page(s) in category: {category_name}")
        
        # Confirm with the user before proceeding
        if input("Would you like to proceed with processing these pages? (y/n): ").strip().lower() != 'y':
            print("Operation cancelled by user.")
            return

        print("Processing pages...")

        bot = ReplaceBot(pages, summary="Applying ChatGPT-assisted modifications")
        bot.run()

    except Exception as e:
        print(f"Error: Unable to access category '{category_name}': {e}")

if __name__ == '__main__':
    import sys
    main(*sys.argv[1:])
