r"""
This script was written by ChatGPT and it adds an article item to bahaidata. The article will have
properties "part of issue", "author" and "pages". After the article has been created it will be
added to the items for the magazine issue and the author. 
"""

from wikibaseintegrator import wbi_login, WikibaseIntegrator, wbi_helpers
from wikibaseintegrator.datatypes import String, Item
from wikibaseintegrator.wbi_config import config as wbi_config

# Configuration
wbi_config['MEDIAWIKI_API_URL'] = 'https://bahaidata.org/api.php'
wbi_config['USER_AGENT'] = 'MyWikibaseBot/1.0 (https://bahaidata.org/User:David)'
login_instance = wbi_login.Clientlogin(user='David', password='something')

# Initialize Wikibase Integrator
wbi = WikibaseIntegrator(login=login_instance)

def check_or_create_author(author_name):
    search_result = wbi_helpers.search_entities(author_name)
    
    if search_result:
        return search_result[0]
    else:
        author_item = wbi.item.new()
        author_item.labels.set(language='en', value=author_name)
        author_item.write()
        return author_item.id

def create_article_item(title, page_range, author_item_id):
    article_item = wbi.item.new()
    article_item.labels.set(language='en', value=title)
    magazine_issue_id = 'Q213'  # Magazine issue item ID
    article_item.claims.add(Item(value=magazine_issue_id, prop_nr='P7'))
    article_item.claims.add(Item(value=author_item_id, prop_nr='P10'))
    article_item.claims.add(String(value=page_range, prop_nr='P6'))
    article_item.write()
    return article_item.id  

def link_article_to_author(article_item_id, author_item_id):
    author_item = wbi.item.get(entity_id=author_item_id)

    # Check if the property exists, if not initialize an empty list
    if 'P11' in author_item.claims:
        existing_claims = author_item.claims.get('P11')
    else:
        existing_claims = []

    new_claim = Item(value=article_item_id, prop_nr='P11')
    existing_claims.append(new_claim)
    author_item.write()

def link_article_to_magazine_issue(article_item_id, magazine_issue_id):
    magazine_issue_item = wbi.item.get(entity_id=magazine_issue_id)

    # Check if the property exists, if not initialize an empty list
    if 'P4' in magazine_issue_item.claims:
        existing_claims = magazine_issue_item.claims.get('P4')
    else:
        existing_claims = []

    new_claim = Item(value=article_item_id, prop_nr='P4')
    existing_claims.append(new_claim)
    magazine_issue_item.write()


# Example workflow
author_name = 'Charles Frink'
article_title = 'Spiritual and Material Healing'
page_range = '452-457'

author_item_id = check_or_create_author(author_name)
article_item_id = create_article_item(article_title, page_range, author_item_id)
link_article_to_author(article_item_id, author_item_id)
link_article_to_magazine_issue(article_item_id)
