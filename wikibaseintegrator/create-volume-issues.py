r"""
This script is intended to add Volume and Issue pair items to Bahaidata.org.  
The input is publication title, number of volumes, and number of issues per volume.
The script should create all the items and link them to bahai.works.

Note that wbi_login.Clientlogin is not the preferred way to log in but I wanted to 
quickly test this and so I used it. 

Note, this script was written by ChatGPT. In its current form this script doesn't work very well.
"""

from wikibaseintegrator import wbi_login, WikibaseIntegrator, wbi_config
from wikibaseintegrator.datatypes import String, Item, Sitelink

# Configuration
wbi_config['MEDIAWIKI_API_URL'] = 'https://bahaidata.org/api.php'
wbi_config['USER_AGENT'] = 'MyWikibaseBot/1.0 (https://bahaidata.org/User:David)'
login_instance = wbi_login.Clientlogin(user='Username', password='Password')

# Initialize Wikibase Integrator
wbi = WikibaseIntegrator(login=login_instance)

def add_sitelink_to_item(item_id, site, title):
    item = wbi.item.get(entity_id=item_id)
    site_link = Sitelink(site=site, title=title)
    item.sitelinks.set(site_link)
    item.write()

def create_volume_and_issue_items(publication_title, total_volumes, issues_per_volume, start_volume):
    for volume_number in range(int(start_volume), int(total_volumes) + 1):
        volume_title = f"{publication_title} Volume {volume_number}"
        volume_item = wbi.item.new()
        volume_item.labels.set(language='en', value=volume_title)
        volume_response = volume_item.write()
        volume_item_id = volume_item.id
        print(f"Created Volume: {volume_title} ({volume_item_id})")

        for issue_number in range(1, int(issues_per_volume) + 1):
            issue_title = f"{publication_title} Vol.{volume_number} No.{issue_number}"
            issue_item = wbi.item.new()
            issue_item.labels.set(language='en', value=issue_title)
            issue_item.claims.add(Item(value=volume_item_id, prop_nr='P8'))  # Link to volume
            issue_response = issue_item.write()
            issue_item_id = issue_item.id
            print(f"Created Issue: {issue_title} ({issue_item_id})")

            sitelink_title = f"{publication_title.replace(' ', '_')}/Volume_{volume_number}/Issue_{issue_number}/Text"
            add_sitelink_to_item(issue_item_id, 'works', sitelink_title)

# Example usage
title = 'World Order'
volumes = '14'
issues = '12'
start = '3'
create_volume_and_issue_items(title, volumes, issues, start)
