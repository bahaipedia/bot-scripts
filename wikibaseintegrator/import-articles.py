r"""
This file is used to import article/author pairs into bahaidata.org. Items that
 are created will be connected using the appropriate properties. New author
 items created will be printed to console since those likely need special
 handling (adding language links, adding or modifying the Author page on
 bahai.works to use bahaidata etc.)

Usage: python import-articles.py Q224 (representing the Issue item where
 articles will be organized). The script accommodates both editorials and
 articles with more than one author, or an editor/translator instead of an 
 author. See import.json for how to structure your data. Note: author or 
 editor/translator must be passed as a list even for single authors.

"""

import json
import sys
import re
from wikibaseintegrator import wbi_login, WikibaseIntegrator, wbi_helpers
from wikibaseintegrator.datatypes import String, Item
from wikibaseintegrator.datatypes.extra.localmedia import LocalMedia
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator.wbi_enums import ActionIfExists

# Configuration
wbi_config['MEDIAWIKI_API_URL'] = 'https://bahaidata.org/api.php'
wbi_config['USER_AGENT'] = 'MyWikibaseBot/1.0 (https://bahaidata.org/User:David)'
login_instance = wbi_login.Clientlogin(user='David', password='hunter2')

# Initialize Wikibase Integrator
wbi = WikibaseIntegrator(login=login_instance)

def validate_json_format(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        try:
            articles_data = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            sys.exit(1)

        for article in articles_data:
            # Check for required keys
            required_keys = ["title", "page_range"]
            if not all(key in article for key in required_keys):
                raise ValueError("Missing required keys in article entry.")

            # Check for author, editor, translator, or editorial
            if ('author' not in article and 
                'editor' not in article and 
                'translator' not in article and 
                'editorial' not in article):
                raise ValueError(f"Article '{article['title']}' must have either an author, an editor, a translator, or be marked as editorial.")

            # Validate author format
            if 'author' in article and not isinstance(article["author"], list):
                raise ValueError(f"Author for '{article['title']}' is not formatted as a list.")

            # Validate editorial format
            if 'editorial' in article and not isinstance(article["editorial"], bool):
                raise ValueError(f"Editorial field for '{article['title']}' is not a boolean.")

            # Validate title and page range format
            if not isinstance(article["title"], str) or not isinstance(article["page_range"], str):
                raise ValueError(f"Title or Page Range for '{article['title']}' is not a string.")

            # Validate editor format (expecting a single editor as a string)
            if 'editor' in article and not isinstance(article["editor"], list):
                raise ValueError(f"Editor for '{article['title']}' is not formatted as a list.")
                
            # Validate translator format
            if 'translator' in article and not isinstance(article["translator"], list):
                raise ValueError(f"Translator for '{article['title']}' is not formatted as a list.")

        print("JSON file is valid.")
        
def process_articles_from_file(file_name, magazine_issue_id):
    with open(file_name, 'r', encoding='utf-8') as file:
        articles_data = json.load(file)

    for article in articles_data:
        title, page_range = article['title'], article['page_range']
        person_item_ids = []
        person_role = None
        is_editorial = article.get('editorial', False)

        if 'author' in article:
            for author_name in article['author']:
                person_item_id = check_or_create_author(author_name)
                person_item_ids.append(person_item_id)
            person_role = 'author'
        elif 'editor' in article:
            for editor_name in article['editor']:
                person_item_id = check_or_create_editor(editor_name)
                person_item_ids.append(person_item_id)
            person_role = 'editor'
        elif 'translator' in article:
            for translator_name in article['translator']:
                person_item_id = check_or_create_translator(translator_name)
                person_item_ids.append(person_item_id)
            person_role = 'translator'
        elif is_editorial:
            # Handle unnamed editorial
            person_role = 'editorial'

        article_item_id = create_article_item(title, page_range, person_item_ids, magazine_issue_id, person_role)

        for person_item_id in person_item_ids:
            if person_role == 'author':
                link_article_to_author(article_item_id, person_item_id)
            elif person_role == 'editor':
                link_article_to_editor(article_item_id, person_item_id)
            elif person_role == 'translator':
                link_article_to_translator(article_item_id, person_item_id)

        link_article_to_magazine_issue(article_item_id, magazine_issue_id)

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

def check_or_create_editor(editor_name):
    search_result = wbi_helpers.search_entities(editor_name)
    
    if search_result:
        return search_result[0]
    else:
        editor_item = wbi.item.new()
        editor_item.labels.set(language='en', value=editor_name)
        editor_item.write()
        new_editor_id = editor_item.id
        print(f"Created editor {editor_name} ({new_editor_id})")
        return new_editor_id

def check_or_create_translator(translator_name):
    search_result = wbi_helpers.search_entities(translator_name)
    
    if search_result:
        return search_result[0]
    else:
        translator_item = wbi.item.new()
        translator_item.labels.set(language='en', value=translator_name)
        translator_item.write()
        new_translator_id = translator_item.id
        print(f"Created translator {translator_name} ({new_translator_id})")
        return new_translator_id
        
def create_article_item(title, page_range, person_item_ids, magazine_issue_id, person_role):
    article_item = wbi.item.new()
    article_item.labels.set(language='en', value=title)
    article_item.claims.add(Item(value=magazine_issue_id, prop_nr='P7'))

    if person_role == 'author':
        for person_item_id in person_item_ids:
            article_item.claims.add(Item(value=person_item_id, prop_nr='P10'), action_if_exists=ActionIfExists.APPEND_OR_REPLACE)
    elif person_role == 'editor':
        article_item.claims.add(Item(value=person_item_ids[0], prop_nr='P14')) 
    elif person_role == 'translator':
        article_item.claims.add(Item(value=person_item_ids[0], prop_nr='P32')) 
    elif person_role == 'editorial':
        editorial_id = 'Q19'
        article_item.claims.add(Item(value=editorial_id, prop_nr='P12')) 

    article_item.claims.add(String(value=page_range, prop_nr='P6'))
    article_item.write()
    return article_item.id

def link_article_to_author(article_item_id, author_item_id):
    author_item = wbi.item.get(entity_id=author_item_id)
    new_claim = Item(value=article_item_id, prop_nr='P11')
    author_item.claims.add(new_claim, action_if_exists=ActionIfExists.APPEND_OR_REPLACE)
    author_item.write()
    
def link_article_to_editor(article_item_id, editor_item_id):
    editor_item = wbi.item.get(entity_id=editor_item_id)
    new_claim = Item(value=article_item_id, prop_nr='P15')
    editor_item.claims.add(new_claim, action_if_exists=ActionIfExists.APPEND_OR_REPLACE)
    editor_item.write()
    
def link_article_to_translator(article_item_id, translator_item_id):
    translator_item = wbi.item.get(entity_id=translator_item_id)
    new_claim = Item(value=article_item_id, prop_nr='P33')
    translator_item.claims.add(new_claim, action_if_exists=ActionIfExists.APPEND_OR_REPLACE)
    translator_item.write()

def link_article_to_magazine_issue(article_item_id, magazine_issue_id):
    magazine_issue_item = wbi.item.get(entity_id=magazine_issue_id)
    new_claim = Item(value=article_item_id, prop_nr='P4')
    magazine_issue_item.claims.add(new_claim, action_if_exists=ActionIfExists.APPEND_OR_REPLACE)
    magazine_issue_item.write()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add-articles-file.py <MagazineIssueID>")
        sys.exit(1)

    magazine_issue_id = sys.argv[1]
    
    # Validate JSON before processing
    validate_json_format('import.json')

    # Main processing
    process_articles_from_file('import.json', magazine_issue_id)
