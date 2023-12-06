r"""
This file is used to import article/author pairs into bahaidata.org. Items that
 are created will be connected using the appropriate properties. New author
 items created will be printed to console since those likely need special
 handling (adding language links, adding or  modifying the Author page on
 bahai.works to use bahaidata etc.)

Usage: python import-articles.py Q220 (representing the Issue item where
 articles will be organized)
"""

import sys
from wikibaseintegrator import wbi_login, WikibaseIntegrator, wbi_helpers
from wikibaseintegrator.datatypes import String, Item
from wikibaseintegrator.wbi_config import config as wbi_config
import json
from wikibaseintegrator.wbi_enums import ActionIfExists

# Configuration
wbi_config['MEDIAWIKI_API_URL'] = 'https://bahaidata.org/api.php'
wbi_config['USER_AGENT'] = 'MyWikibaseBot/1.0 (https://bahaidata.org/User:David)'
login_instance = wbi_login.Clientlogin(user='David', password='hunter2')

# Initialize Wikibase Integrator
wbi = WikibaseIntegrator(login=login_instance)

def process_articles_from_file(file_name, magazine_issue_id):
    with open(file_name, 'r', encoding='utf-8') as file:
        articles_data = json.load(file)

    for article in articles_data:
        title, page_range = article['title'], article['page_range']
        person_item_ids = []
        person_role = None

        if 'author' in article:
            for author_name in article['author']:
                person_item_id = check_or_create_author(author_name)
                person_item_ids.append(person_item_id)
            person_role = 'author'
        elif 'editor' in article:
            person_item_id = check_or_create_editor(article['editor'])
            person_item_ids.append(person_item_id)
            person_role = 'editor'

        article_item_id = create_article_item(title, page_range, person_item_ids, magazine_issue_id, person_role)

        for person_item_id in person_item_ids:
            if person_role == 'author':
                link_article_to_author(article_item_id, person_item_id)
            elif person_role == 'editor':
                link_article_to_editor(article_item_id, person_item_id)

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

def create_article_item(title, page_range, person_item_ids, magazine_issue_id, person_role):
    article_item = wbi.item.new()
    article_item.labels.set(language='en', value=title)
    article_item.claims.add(Item(value=magazine_issue_id, prop_nr='P7'))

    if person_role == 'author':
        for person_item_id in person_item_ids:
            article_item.claims.add(Item(value=person_item_id, prop_nr='P10'), action_if_exists=ActionIfExists.APPEND_OR_REPLACE)
    elif person_role == 'editor':
        # Assuming only one editor, so no loop needed
        article_item.claims.add(Item(value=person_item_ids[0], prop_nr='P14'))

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
    process_articles_from_file('import.json', magazine_issue_id)
