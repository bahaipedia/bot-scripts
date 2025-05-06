r"""
Purpose: Import books from bahai.works into bahaidata.org to help with automatic citation creation. 

Requires: books.cvs with UTF-8 encoding with columns TITLE,FULL_TITLE,AUTHOR,COVER_IMAGE,TRANSLATOR,EDITOR,PUBLISHER,COUNTRY,PUBYEAR,PAGES,ISBN10,ISBN13

Usage: python add-books.py

After this script then https://github.com/bahaipedia/bot-scripts/blob/main/python/api_addsitelinks_data-bookformat.py to create the sitelinks from bahaidata back to bahai.works
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
    # Check that at least one of author, editor, or translator exists
    has_creator = bool(row['AUTHOR'] or row['EDITOR'] or row['TRANSLATOR'])
    
    # Check required fields and return True/False
    required_columns = [row['TITLE'], row['COVER_IMAGE'], row['PUBLISHER'], row['COUNTRY'], row['PUBYEAR'], row['PAGES']]
    if any(not col for col in required_columns) or not has_creator:
        return False
    return True

def check_or_create_person(person_name, role):
    """Generic function to check or create a person entity (author, editor, translator)"""
    search_result = wbi_helpers.search_entities(person_name)
    
    if search_result:
        return search_result[0]
    else:
        person_item = wbi.item.new()
        person_item.labels.set(language='en', value=person_name)
        person_item.write()
        new_person_id = person_item.id
        print(f"Created {role} {person_name} ({new_person_id})")
        return new_person_id

def check_or_create_author(author_name):
    return check_or_create_person(author_name, "author")

def check_or_create_editor(editor_name):
    return check_or_create_person(editor_name, "editor")

def check_or_create_translator(translator_name):
    return check_or_create_person(translator_name, "translator")

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

def link_book_to_person(book_item_id, person_item_id, property_id):
    """Generic function to link a book to a person with the specified property"""
    person_item = wbi.item.get(entity_id=person_item_id)
    new_claim = Item(value=book_item_id, prop_nr=property_id)
    person_item.claims.add(new_claim, action_if_exists=ActionIfExists.APPEND_OR_REPLACE)
    person_item.write()

def link_book_to_author(book_item_id, author_item_id):
    link_book_to_person(book_item_id, author_item_id, 'P11')  # has authored

def link_book_to_editor(book_item_id, editor_item_id):
    link_book_to_person(book_item_id, editor_item_id, 'P15')  # has edited

def link_book_to_translator(book_item_id, translator_item_id):
    link_book_to_person(book_item_id, translator_item_id, 'P33')  # has translated

def process_row(row, output_file):
    # Map CSV columns to Wikibase properties and create/update the book item
    label = row['TITLE']
    title = row['FULL_TITLE'] if row['FULL_TITLE'] else row['TITLE']
    
    # Process authors
    author_ids = []
    if row['AUTHOR']:
        authors = row['AUTHOR'].split(',')  # Assuming authors are separated by commas
        author_ids = [check_or_create_author(author.strip()) for author in authors]
    
    # Process editors
    editor_ids = []
    if row['EDITOR']:
        editors = row['EDITOR'].split(',')  # Assuming editors are separated by commas
        editor_ids = [check_or_create_editor(editor.strip()) for editor in editors]
    
    # Process translators
    translator_ids = []
    if row['TRANSLATOR']:
        translators = row['TRANSLATOR'].split(',')  # Assuming translators are separated by commas
        translator_ids = [check_or_create_translator(translator.strip()) for translator in translators]
    
    image = row['COVER_IMAGE']
    publication_year = row['PUBYEAR']
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
    
    # Add authors
    for author_id in author_ids:
        book_item.claims.add(Item(value=author_id, prop_nr='P10'),
                             action_if_exists=ActionIfExists.APPEND_OR_REPLACE)
    
    # Add editors
    for editor_id in editor_ids:
        book_item.claims.add(Item(value=editor_id, prop_nr='P14'),
                             action_if_exists=ActionIfExists.APPEND_OR_REPLACE)
    
    # Add translators
    for translator_id in translator_ids:
        book_item.claims.add(Item(value=translator_id, prop_nr='P32'),
                             action_if_exists=ActionIfExists.APPEND_OR_REPLACE)
    
    book_item.claims.add(String(value=image, prop_nr='P35'))  # Image

    # Add publication year with year precision
    year = int(publication_year)
    book_item.claims.add(Time(time=f'+{year:04}-00-00T00:00:00Z', prop_nr='P29', precision=9))

    book_item.claims.add(Item(value=publisher_id, prop_nr='P26'))  # Publisher ID
    book_item.claims.add(Item(value=country_id, prop_nr='P48'))  # Country ID
    book_item.claims.add(String(value=pages, prop_nr='P6'))  # Pages
    if isbn_10:
        book_item.claims.add(String(value=isbn_10, prop_nr='P31'))  # ISBN-10
    if isbn_13:
        book_item.claims.add(String(value=isbn_13, prop_nr='P49'))  # ISBN-13

    book_item.write()

    # Link the book to each author
    for author_id in author_ids:
        link_book_to_author(book_item.id, author_id)
        
    # Link the book to each editor
    for editor_id in editor_ids:
        link_book_to_editor(book_item.id, editor_id)
        
    # Link the book to each translator
    for translator_id in translator_ids:
        link_book_to_translator(book_item.id, translator_id)

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
