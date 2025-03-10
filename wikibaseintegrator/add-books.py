r"""
Purpose: Import books from bahai.works into bahaidata.org to help with automatic citation creation. 

Requires: books.cvs with UTF-8 encoding with columns TITLE,FULL_TITLE,AUTHOR,COVER_IMAGE,TRANSLATOR,EDITOR,PUBLISHER,COUNTRY,PUBYEAR,PAGES,ISBN10,ISBN13

Usage: python add-books.py
"""

import csv
import sys
from wikibaseintegrator import wbi_login, WikibaseIntegrator, wbi_helpers
from wikibaseintegrator.datatypes import String, Item, MonolingualText, Time
from wikibaseintegrator.datatypes.extra.localmedia import LocalMedia
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator.wbi_enums import ActionIfExists

# Configuration
wbi_config['MEDIAWIKI_API_URL'] = 'https://bahaidata.org/api.php'
wbi_config['USER_AGENT'] = 'MyWikibaseBot/1.0 (https://bahaidata.org/User:David)'
login_instance = wbi_login.Clientlogin(user='changeme', password='changeme')
wbi = WikibaseIntegrator(login=login_instance)

def validate_row(row):
    # Check required fields and return True/False
    required_columns = [row['TITLE'], row['AUTHOR'], row['COVER_IMAGE'], row['PUBLISHER'], row['COUNTRY'], row['PUBYEAR'], row['PAGES']]
    if any(not col for col in required_columns) or (not row['ISBN10'] and not row['ISBN13']):
        return False
    return True

def check_or_create_author(author_name):
    search_result = wbi_helpers.search_entities(author_name)
    
    if search_result:
        return search_result[0]
    else:
        author_item = wbi.item.new()
        author_item.labels.set(language='en', value=author_name)
        author_item.write()
        new_author_id = author_item.id
        print(f"Created author {author_name} ({new_author_id})")
        return new_author_id

def check_or_create_publisher(publisher_name):
    search_result = wbi_helpers.search_entities(publisher_name)
    
    if search_result:
        return search_result[0]
    else:
        publisher_item = wbi.item.new()
        publisher_item.labels.set(language='en', value=publisher_name)
        publisher_item.write()
        new_publisher_id = publisher_item.id
        print(f"Created publisher {publisher_name} ({new_publisher_id})")
        return new_publisher_id

def check_or_create_country(country_name):
    search_result = wbi_helpers.search_entities(country_name)
    
    if search_result:
        return search_result[0]
    else:
        country_item = wbi.item.new()
        country_item.labels.set(language='en', value=country_name)
        country_item.write()
        new_country_id = country_item.id
        print(f"Created country {country_name} ({new_country_id})")
        return new_country_id

def process_row(row, output_file):
    # Map CSV columns to Wikibase properties and create/update the book item
    label = row['TITLE']
    title = row['FULL_TITLE'] if row['FULL_TITLE'] else row['TITLE']
    author_name = row['AUTHOR']
    author_id = check_or_create_author(author_name)
    image = row['COVER_IMAGE']
    publication_date = row['PUBYEAR']
    publisher_name = row['PUBLISHER']
    publisher_id = check_or_create_publisher(publisher_name)
    country_name = row['COUNTRY']
    country_id = check_or_create_country(country_name)
    pages = row['PAGES']
    isbn_10 = row['ISBN10']
    isbn_13 = row['ISBN13']

    # Create a new item and add required claims
    book_item = wbi.item.new()
    book_item.labels.set(language='en', value=label)
    book_item.claims.add(Item(value='Q4581', prop_nr='P12'))  # Instance of written work
    book_item.claims.add(MonolingualText(text=title, language='en', prop_nr='P47'))  # Title
    book_item.claims.add(Item(value=author_id, prop_nr='P10'))  # Author ID
    book_item.claims.add(String(value=image, prop_nr='P35'))  # Image
    
    # Parse and add publication date
    if publication_date:
        try:
            date_parts = publication_date.split('-')
            year = int(date_parts[0])
            month = int(date_parts[1]) if len(date_parts) > 1 else 1
            day = int(date_parts[2]) if len(date_parts) > 2 else 1
            book_item.claims.add(Time(time=f'+{year:04}-{month:02}-{day:02}T00:00:00Z', prop_nr='P29'))
        except ValueError:
            print(f"Invalid date format for publication date: {publication_date}")

    book_item.claims.add(Item(value=publisher_id, prop_nr='P26'))  # Publisher ID
    book_item.claims.add(Item(value=country_id, prop_nr='P48'))  # Country ID
    book_item.claims.add(String(value=pages, prop_nr='P6'))  # Pages
    if isbn_10:
        book_item.claims.add(String(value=isbn_10, prop_nr='P31'))  # ISBN-10
    if isbn_13:
        book_item.claims.add(String(value=isbn_13, prop_nr='P49'))  # ISBN-13

    book_item.write()

    # Write the confirmation message to the file
    output_file.write(f"Created {label} ({book_item.id})\n")

if __name__ == "__main__":
    with open('books.csv', mode='r', encoding='utf-8-sig') as file, open('needed-books.txt', mode='a', encoding='utf-8') as output_file:
        reader = csv.DictReader(file)
        
        for row in reader:
            if not validate_row(row):
                continue

            try:
                process_row(row, output_file)
            except Exception as e:
                print(f"Failed to process row: {e}")
