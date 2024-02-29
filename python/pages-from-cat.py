r""" 
This script is used to generate the [[Authors]] page on bahai.works. 

Usage: 
	$ python pages-from-cat.py (Saves a formatted list of authors A-Z to pages-from-cat-output.txt)
	$ python pages-from-cat.py H (Only saves authors in Category:Authors-H)
	$ python pages-from-cat.py -type:plain (only outputs a list of category members, no formatting)

Used with: pages-from-cat-exclusion-list.txt. This is a list of author pages to exclude 
from pages-from-cat-output.txt
"""

import requests
import sys

# Function to load exclusion list from a file
def load_exclusion_list(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"Warning: '{file_name}' not found. No exclusions will be applied.")
        return []

# Load exclusion list from 'pages-from-cat-exclusion-list.txt'
exclusion_list = load_exclusion_list('pages-from-cat-exclusion-list.txt')

def process_name(page_title):
    name_parts = page_title.split()
    
    # Known suffixes and connectors
    suffixes = {"Jr.": True, "Sr.": True, "III": True, "II": True}
    connectors = {"de": True, "dos": True, "da": True, "do": True, "von": True, "van": True, "den": True}

    # Function to determine if the name contains connectors
    def contains_connector(parts):
        return any(connectors.get(part.lower()) for part in parts)

    # Function to determine if the name contains suffixes
    def contains_suffix(parts):
        return any(suffixes.get(part) for part in parts)

    has_connector = contains_connector(name_parts)
    has_suffix = contains_suffix(name_parts)
    
    # Adjusting process based on presence of connectors and suffixes
    if has_connector:
        connector_index = next((i for i, part in enumerate(name_parts) if connectors.get(part.lower())), len(name_parts))
        last_part = " ".join(name_parts[connector_index:])
        first_part = " ".join(name_parts[:connector_index])
    elif has_suffix:
        suffix_index = next((i for i, part in enumerate(name_parts) if suffixes.get(part)), len(name_parts))
        last_part = " ".join(name_parts[suffix_index - 1:suffix_index + 1])  # Include the suffix in the last part
        first_part = " ".join(name_parts[:suffix_index - 1])
    else:
        last_part = name_parts[-1]
        first_part = " ".join(name_parts[:-1])

    # Handling comma placement correctly
    if first_part:
        return f"{last_part}, {first_part}"
    else:
        return last_part

def get_category_members(category, endpoint):
    params = {
        'action': 'query',
        'list': 'categorymembers',
        'cmtitle': f'Category:{category}',
        'format': 'json',
        'cmlimit': 'max'
    }

    pages = []
    while True:
        response = requests.get(endpoint, params=params)
        data = response.json()
        pages.extend([page['title'] for page in data['query']['categorymembers']])
        
        if 'continue' not in data:
            break

        params['cmcontinue'] = data['continue']['cmcontinue']

    return pages

def collect_authors_category(letter, endpoint, output_file, output_type):
    category = f'Authors-{letter}'
    members = get_category_members(category, endpoint)

    with open(output_file, 'a', encoding='utf-8') as file:  # Append mode
        if members:  # Check if the category is not empty
            if output_type != 'plain':
                file.write(f"==== {letter} ====\n")  # Header for formatted type

            for member in members:
                if member not in exclusion_list:
                    if output_type == 'plain':
                        file.write(member + '\n')
                    else:
                        processed_name = process_name(member.split(":", 1)[-1])
                        file.write(f"* [[{member}|{processed_name}]]\n")
            
            if output_type != 'plain':
                file.write('\n\n')  # Two line breaks for formatted type

    print(f"Processed category '{category}'.")

def collect_all_authors_categories(endpoint, output_file, output_type):
    for letter in map(chr, range(ord('A'), ord('Z') + 1)):
        collect_authors_category(letter, endpoint, output_file, output_type)

# Main script execution
if __name__ == "__main__":
    endpoint = 'https://bahai.works/api.php'
    output_file = 'pages-from-cat-output.txt'

    if len(sys.argv) >= 2 and sys.argv[-1].startswith('-type:'):
        output_type = sys.argv[-1].split(':', 1)[1]
    else:
        output_type = 'formatted'

    if len(sys.argv) >= 2 and len(sys.argv[1]) == 1 and sys.argv[1].isalpha():
        letter = sys.argv[1].upper()
        collect_authors_category(letter, endpoint, output_file, output_type)
    else:
        collect_all_authors_categories(endpoint, output_file, output_type)
