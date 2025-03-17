r"""
This script is in progress, it's not ready to be used yet 

It's purpose is to access a BWNS article, download all the images and associated captions, rename the files
using the first few words of the caption, and separately save the caption in a .txt file that follows
the bahai.media format for automatic importing of images following the download process.
 
Usage: python scraper.py <article number>

"""

import os
import sys
import time
import requests
from bs4 import BeautifulSoup
import re

def sanitize_filename(text, max_length=55):
    """Sanitize filename by keeping only alphanumeric and common punctuation."""
    # We're always adding an extension later, so we shouldn't look for one in the text
    # Sanitize the text
    text = re.sub(r'[^a-zA-Z0-9 _.,()\'"-]', '', text)
    text = text.replace(' ', '_')

    # Calculate available space for text (assuming .jpg extension will be added later)
    extension_length = 4  # Length of ".jpg"
    available_length = max_length - extension_length

    # If text needs truncation
    if len(text) > available_length:
        # Find the last space before the limit
        last_space = text[:available_length].rfind('_')
        if last_space > 0:
            text = text[:last_space]
        else:
            # If no space found, just truncate
            text = text[:available_length]

    # Remove trailing periods and spaces
    text = text.rstrip('. ')

    return text

def download_images_and_captions(story_id):
    """Download images and captions from slideshow."""
    base_url = f"https://news.bahai.org/story/{story_id}/slideshow/"
    output_dir = os.path.join("output", str(story_id))
    os.makedirs(output_dir, exist_ok=True)

    slide_number = 1
    while True:
        url = f"{base_url}{slide_number}/"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Stopping: No slide found at {url}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract from meta tags first
        meta_desc = soup.find("meta", attrs={"name": "description"})
        meta_image = soup.find("meta", attrs={"property": "og:image"})
        caption = meta_desc["content"].strip() if meta_desc else None
        image_url = meta_image["content"].split("?")[0] if meta_image else None

        # Fallback to .narrative div
        if not caption or not image_url:
            narrative = soup.find("div", class_="narrative")
            if narrative:
                caption_tag = narrative.find("p")
                download_link = narrative.find("p", class_="download-hires")
                if caption_tag:
                    caption = caption_tag.get_text(strip=True)
                if download_link and download_link.a:
                    image_url = download_link.a["href"].split("?")[0]

        if not caption or not image_url:
            print(f"Skipping slide {slide_number}: Missing caption or image.")
            slide_number += 1
            time.sleep(8)
            continue

        # Create filenames
        filename_base = sanitize_filename(caption)
        image_filename = os.path.join(output_dir, f"{filename_base}.jpg")
        text_filename = os.path.join(output_dir, f"{filename_base}.txt")

        # Download the image
        img_response = requests.get(image_url)
        if img_response.status_code == 200:
            with open(image_filename, "wb") as img_file:
                img_file.write(img_response.content)
            print(f"Saved image: {image_filename}")
        else:
            print(f"Failed to download image: {image_url}")

        # Format and save caption text in the required format
        formatted_text = f"""== File info ==
{{{{cs
| caption = {caption}
| source = {{{{bwn|{story_id}}}}}
}}}}

==File license==
{{{{Baha'i World News Service}}}}"""

        with open(text_filename, "w", encoding="utf-8") as text_file:
            text_file.write(formatted_text)
        print(f"Saved caption: {text_filename}")

        slide_number += 1
        time.sleep(5)  # Delay between slides

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <story_id>")
        sys.exit(1)

    story_id = sys.argv[1]
    download_images_and_captions(story_id)
