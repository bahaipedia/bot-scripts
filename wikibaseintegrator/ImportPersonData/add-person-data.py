r"""
Usage: python add-person-data.py

This script reads a 'persondetails.csv' file to update details for existing items in Wikibase.
It will FAIL FAST and TERMINATE if it encounters any data it cannot parse, preventing partial imports.

**REQUIRED LIBRARY:**
You must install python-dateutil: pip install python-dateutil

The script will:
1. Find the person by the 'Name' column.
2. Ensure the 'instance of' (P12) -> 'human' (Q100) claim exists, adding it if missing.
3. Parse and add image, birth date, and death date. It handles various date formats
   (e.g., "1982", "May 18, 1982", "1963-04-23").
4. Parse and add up to 7 'position held' claims with start/end date qualifiers.

The CSV file must have the following columns:
- Name: The label of the person's item in Wikibase.
- image: The image file name (optional, maps to P35).
- birth date: Date of birth (optional, maps to P16).
- death date: Date of death (optional, maps to P17).
- pos1_label, pos1_start, pos1_end: Details for the first position (optional).
- ... up to pos7.
"""
import csv
import sys
from wikibaseintegrator import wbi_login, WikibaseIntegrator, wbi_helpers
from wikibaseintegrator.datatypes import String, Item, Time
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator.wbi_enums import ActionIfExists

try:
    from dateutil.parser import parse as date_parse
except ImportError:
    print("Error: 'python-dateutil' library not found.")
    print("Please install it by running: pip install python-dateutil")
    sys.exit(1)

# --- Configuration ---
# Update with your bot's credentials and Wikibase URL
wbi_config['MEDIAWIKI_API_URL'] = 'https://bahaidata.org/api.php'
wbi_config['USER_AGENT'] = 'MyWikibaseBot/1.0 (https://bahaidata.org/User:YOUR_USERNAME)'
login_instance = wbi_login.Clientlogin(user='Sarah', password='YOUR_PASSWORD')
wbi = WikibaseIntegrator(login=login_instance)

MAX_POSITIONS = 7 # Maximum number of position columns to check

def get_item_id(item_label):
    """Searches for an item by its label and returns the QID, or None if not found."""
    if not item_label:
        return None
    search_result = wbi_helpers.search_entities(item_label.strip(), language='en')
    if search_result:
        return search_result[0]
    return None

def parse_wikibase_time(date_string, field_name_for_error):
    """
    Parses a date string into a Wikibase-compatible time format and precision.
    Handles year-only ("1982") and full dates ("May 18, 1982").
    Raises ValueError if the date format is invalid.
    """
    if not date_string or not date_string.strip():
        return None, None # Field is optional and empty

    clean_date_str = date_string.strip()

    # Try to parse as a year first
    try:
        if len(clean_date_str) == 4 and clean_date_str.isdigit():
            year = int(clean_date_str)
            return f'+{year:04}-00-00T00:00:00Z', 9 # Precision 9 for Year
    except ValueError:
        pass # Not a simple year, proceed to full date parsing

    # Try to parse as a full date
    try:
        dt = date_parse(clean_date_str)
        # Assuming day precision if it's not just a year
        return dt.strftime('+%Y-%m-%dT00:00:00Z'), 11 # Precision 11 for Day
    except (ValueError, TypeError) as e:
        # This is a hard failure as requested
        raise ValueError(f"Invalid format for '{field_name_for_error}': '{date_string}'")

def process_row(row, output_file):
    """
    Validates all data in a row and then updates the Wikibase item.
    Throws ValueError on any validation failure.
    """
    person_name = row.get('Name', '').strip()
    if not person_name:
        return # Skip rows with no name

    person_id = get_item_id(person_name)
    if not person_id:
        raise ValueError(f"Person '{person_name}' not found in Wikibase.")

    # --- 1. PRE-VALIDATION AND DATA PREPARATION ---
    # All data for the row is parsed here. If any parse_wikibase_time call fails,
    # it will raise an exception and none of the data will be written.

    birth_date_str, birth_precision = parse_wikibase_time(row.get('birth date'), 'birth date')
    death_date_str, death_precision = parse_wikibase_time(row.get('death date'), 'death date')

    positions_data = []
    for i in range(1, MAX_POSITIONS + 1):
        pos_label = row.get(f'pos{i}_label', '').strip()
        if pos_label:
            position_id = get_item_id(pos_label)
            if not position_id:
                raise ValueError(f"Position '{pos_label}' not found for '{person_name}'.")

            start_str, start_prec = parse_wikibase_time(row.get(f'pos{i}_start'), f'pos{i}_start')
            end_str, end_prec = parse_wikibase_time(row.get(f'pos{i}_end'), f'pos{i}_end')

            positions_data.append({
                'id': position_id,
                'start_str': start_str, 'start_prec': start_prec,
                'end_str': end_str, 'end_prec': end_prec
            })

    # --- 2. WIKIBASE ITEM MODIFICATION ---
    # This section only runs if all data above was validated successfully.

    person_item = wbi.item.get(entity_id=person_id)

    # Ensure 'instance of' (P12) -> 'human' (Q100)
    instance_of_claims = person_item.claims.get('P12')
    is_human = any(claim.mainsnak.datavalue['value']['id'] == 'Q100' for claim in instance_of_claims) if instance_of_claims else False
    if not is_human:
        person_item.claims.add(Item(value='Q100', prop_nr='P12'), action_if_exists=ActionIfExists.APPEND_OR_REPLACE)

    # Add simple claims
    if row.get('image') and row['image'].strip():
        person_item.claims.add(String(value=row['image'].strip(), prop_nr='P35'), action_if_exists=ActionIfExists.REPLACE_ALL)
    if birth_date_str:
        person_item.claims.add(Time(time=birth_date_str, prop_nr='P16', precision=birth_precision), action_if_exists=ActionIfExists.REPLACE_ALL)
    if death_date_str:
        person_item.claims.add(Time(time=death_date_str, prop_nr='P17', precision=death_precision), action_if_exists=ActionIfExists.REPLACE_ALL)

    # Add 'position held' claims
    for pos in positions_data:
        qualifiers = []
        if pos['start_str']:
            qualifiers.append(Time(time=pos['start_str'], prop_nr='P56', precision=pos['start_prec']))
        if pos['end_str']:
            qualifiers.append(Time(time=pos['end_str'], prop_nr='P57', precision=pos['end_prec']))

        claim = Item(value=pos['id'], prop_nr='P55', qualifiers=qualifiers)
        person_item.claims.add(claim, action_if_exists=ActionIfExists.APPEND_OR_REPLACE)

    # Write all changes to Wikibase
    person_item.write()
    message = f"Success: Updated {person_name} ({person_id})"
    print(message)
    output_file.write(message + '\n')

if __name__ == "__main__":
    try:
        with open('persondetails.csv', mode='r', encoding='utf-8-sig') as file, \
             open('person_update_log.txt', mode='a', encoding='utf-8') as output_file:

            reader = csv.DictReader(file)
            # Use enumerate to get the row number for accurate error reporting
            for i, row in enumerate(reader):
                row_num = i + 2 # Account for header row and 0-based index
                person_name = row.get('Name', 'N/A').strip()
                try:
                    process_row(row, output_file)
                except ValueError as e:
                    # Catch data validation errors, print a fatal error, and terminate.
                    error_message = f"\nFATAL ERROR on row {row_num} ('{person_name}'): {e}"
                    print(error_message)
                    output_file.write(error_message + '\n')
                    print("Script terminated to prevent partial data import.")
                    sys.exit(1)
                except Exception as e:
                    # Catch other exceptions like network issues
                    error_message = f"\nUNEXPECTED ERROR on row {row_num} ('{person_name}'): {e}"
                    print(error_message)
                    output_file.write(error_message + '\n')
                    print("Script terminated.")
                    sys.exit(1)

            print("\nScript finished successfully.")
    except FileNotFoundError:
        print("FATAL ERROR: 'persondetails.csv' not found. Please ensure the file is in the same directory.")
        sys.exit(1)
