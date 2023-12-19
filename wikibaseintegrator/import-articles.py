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
from wikibaseintegrator import wbi_login, WikibaseIntegrator, wbi_helpers
from wikibaseintegrator.datatypes import String, Item
from wikibaseintegrator.datatypes.extra.localmedia import LocalMedia
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator.wbi_enums import ActionIfExists

# Configuration
wbi_config['MEDIAWIKI_API_URL'] = 'https://bahaidata.org/api.php'
wbi_config['USER_AGENT'] = 'MyWikibaseBot/1.0 (https://bahaidata.org/User:David)'
login_instance = wbi_login.Clientlogin(user='David', password='replaceme')

# Initialize Wikibase Integrator
wbi = WikibaseIntegrator(login=login_instance)

def validate_json_format(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        articles_data = json.load(file)

    for article in articles_data:
        # Check for required keys
        required_keys = ["title", "page_range"]
        if not all(key in article for key in required_keys):
            raise ValueError("Missing required keys in article entry.")

        # Check for author, editor, translator, or instanceof
        if not any(key in article for key in ["author", "editor", "translator", "instanceof"]):
            raise ValueError(f"Article '{article['title']}' must have either an author, an editor, a translator, or an 'instanceof' value.")

        # Validate author format
        if 'author' in article and not isinstance(article["author"], list):
            raise ValueError(f"Author for '{article['title']}' is not formatted as a list.")

        # Validate editor format
        if 'editor' in article and not isinstance(article["editor"], list):
            raise ValueError(f"Editor for '{article['title']}' is not formatted as a list.")
                
        # Validate translator format
        if 'translator' in article and not isinstance(article["translator"], list):
            raise ValueError(f"Translator for '{article['title']}' is not formatted as a list.")

        # Validate title and page range format
        if not isinstance(article["title"], str) or not isinstance(article["page_range"], str):
            raise ValueError(f"Title or Page Range for '{article['title']}' is not a string.")

        # Validate instanceof format
        if 'instanceof' in article and not isinstance(article["instanceof"], str):
            raise ValueError(f"Instance of for '{article['title']}' is not formatted as a string.")

    print("JSON file is valid.")
        
def handle_instanceof_items(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        articles_data = json.load(file)

    for article in articles_data:
        if 'instanceof' in article:
            instance_type = article['instanceof']
            search_result = wbi_helpers.search_entities(instance_type)
            if not search_result:
                print(f"'{instance_type}' does not exist.")
                create_new = input(f"Would you like to create '{instance_type}'? (yes/no): ").strip().lower()
                if create_new == "yes":
                    create_new_item(instance_type)
                else:
                    print("Script terminated due to missing 'instanceof' item.")
                    sys.exit(1)

    print("All 'instanceof' items are valid.")
        
def process_articles_from_file(file_name, magazine_issue_id):
    with open(file_name, 'r', encoding='utf-8') as file:
        articles_data = json.load(file)

    for article in articles_data:
        title, page_range = article['title'], article['page_range']
        person_item_ids = {
            "author": [],
            "editor": [],
            "translator": []
        }
        instance_of_label = article.get('instanceof', None)
        instance_of_value = None

        if instance_of_label:
            search_result = wbi_helpers.search_entities(instance_of_label)
            instance_of_value = search_result[0]

        if 'author' in article:
            for author_name in article['author']:
                person_item_id = check_or_create_author(author_name)
                person_item_ids["author"].append(person_item_id)
        if 'editor' in article:
            for editor_name in article['editor']:
                person_item_id = check_or_create_editor(editor_name)
                person_item_ids["editor"].append(person_item_id)
        if 'translator' in article:
            for translator_name in article['translator']:
                person_item_id = check_or_create_translator(translator_name)
                person_item_ids["translator"].append(person_item_id)

        article_item_id = create_article_item(title, page_range, person_item_ids, magazine_issue_id, instance_of_value)

        for role, ids in person_item_ids.items():
            for person_item_id in ids:
                if role == 'author':
                    link_article_to_author(article_item_id, person_item_id)
                elif role == 'editor':
                    link_article_to_editor(article_item_id, person_item_id)
                elif role == 'translator':
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
        
def create_article_item(title, page_range, person_item_ids, magazine_issue_id, instance_of_value):
    article_item = wbi.item.new()
    article_item.labels.set(language='en', value=title)
    article_item.claims.add(Item(value=magazine_issue_id, prop_nr='P7'))

    # Use the instance_of_value directly, as it has already been validated
    if instance_of_value:
        article_item.claims.add(Item(value=instance_of_value, prop_nr='P12'))

    if 'author' in person_item_ids:
        for person_item_id in person_item_ids['author']:
            article_item.claims.add(Item(value=person_item_id, prop_nr='P10'), action_if_exists=ActionIfExists.APPEND_OR_REPLACE)
    if 'editor' in person_item_ids:
        for person_item_id in person_item_ids['editor']:
            article_item.claims.add(Item(value=person_item_id, prop_nr='P14')) 
    if 'translator' in person_item_ids:
        for person_item_id in person_item_ids['translator']:
            article_item.claims.add(Item(value=person_item_id, prop_nr='P32')) 

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

def create_new_item(instance_type):
    # Function to create a new item
    new_item = wbi.item.new()
    new_item.labels.set(language='en', value=instance_type)
    new_item.write()
    new_item_id = new_item.id
    print(f"Created new item '{instance_type}' with ID {new_item_id}")
    return new_item_id

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Incorrect usage: python import-articles.py <MagazineIssueID>")
        sys.exit(1)

    magazine_issue_id = sys.argv[1]
    
    try:
        # Attempt to validate JSON format
        validate_json_format('import.json')
    except json.JSONDecodeError as e:
        print(f"Error processing JSON file, check syntax, also ensure the last item in the series does not have a comma. Error is: {e}")
        sys.exit(1)

    # Handle 'instanceof' items
    handle_instanceof_items('import.json')

    # Process articles
    process_articles_from_file('import.json', magazine_issue_id)
