r"""
After running search_api.py open each file in the output folder, replace "title" 
with the mediawiki heading you want to use to group the quotes and reduce the quote down to one sentence, 
then save those files.

Running the script will process each text file in the output folder, grouping quotes by title and using the 
filenames and abbreviation_map to populate the wiki template correctly.

Usage: python process_quotes.py


"""

import json
import re
import os
from collections import defaultdict

# Define the mapping for file name components
abbreviation_map = {
    "days-remembrance": "DR",
    "epistle-son-wolf": "ESW",
    "gems-divine-mysteries": "GDM",
    "gleanings-writings-bahaullah": "GWB",
    "hidden-words": "HW",
    "kitab-i-aqdas": "KA",
    "kitab-i-iqan": "KI",
    "prayers-meditations-bahaullah": "PM",
    "call-divine-beloved": "CDB",
    "summons-lord-hosts": "SLH",
    "tabernacle-unity": "TU",
    "tablets-bahaullah": "TB",
    "additional-prayers-revealed-bahaullah": "APB",
    "additional-tablets-extracts-from-tablets-revealed-bahaullah": "ATB",
    "selections-writings-bab": "SWB",
    "memorials-faithful": "MF",
    "light-of-the-world": "LW",
    "paris-talks": "PT",
    "promulgation-universal-peace": "PUP",
    "secret-divine-civilization": "SDC",
    "selections-writings-abdul-baha": "SWAB",
    "some-answered-questions": "SAQ",
    "tablet-auguste-forel": "TAF",
    "tablets-divine-plan": "TDP",
    "tablets-hague-abdul-baha": "TTH",
    "travelers-narrative": "TN",
    "twelve-table-talks-abdul-baha": "TTT",
    "will-testament-abdul-baha": "WT",
    "prayers-abdul-baha": "TPR",
    "additional-tablets-extracts-talks-abdul-baha": "ATET",
    "additional-prayers-revealed-abdul-baha": "APR"
}

# Folder containing the text files
OUTPUT_FOLDER = "output"
OUTPUT_FILE = "output.txt"


def process_text_file(text_file, abbreviation, all_quotes):
    """Processes a text file if it exists, grouping quotes by title."""
    if not os.path.exists(text_file):
        print(f"Skipping missing file: {text_file}")
        return

    print(f"Processing text file: {text_file}")

    with open(text_file, "r", encoding="utf-8") as f:
        try:
            quotes = json.load(f)  # Expecting JSON format inside .txt files
        except json.JSONDecodeError:
            print(f"Error: Malformed JSON in {text_file}")
            return

    if not quotes:
        print(f"Warning: {text_file} is empty.")
        return

    print(f"→ Read {len(quotes)} quotes from {text_file}")

    for entry in quotes:
        title = entry["title"]
        quote_entry = f"{{{{q|{entry['quote']}|{entry['location']} |{abbreviation} }}}}"
        all_quotes[title].append(quote_entry)


def main():
    all_quotes = defaultdict(list)

    # Get all text files in the output folder
    text_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".txt")]

    if not text_files:
        print("No text files found in the output folder.")
        return

    print(f"Found {len(text_files)} text files.")

    for filename in text_files:
        # Extract everything after the first underscore
        match = re.match(r"[^_]+_(.+)\.txt", filename)
        if not match:
            print(f"Skipping invalid file: {filename}")
            continue

        key = match.group(1)  # Extracted filename part after the first underscore

        if key not in abbreviation_map:
            print(f"Warning: No abbreviation found for {key}")
            continue

        abbreviation = abbreviation_map[key]
        text_file_path = os.path.join(OUTPUT_FOLDER, filename)
        process_text_file(text_file_path, abbreviation, all_quotes)

    # Write to output file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for title, quotes in all_quotes.items():
            f.write(f"===={title}====\n")
            f.write("\n".join(quotes) + "\n\n")

    print(f"Output saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
import json
import re
import os
from collections import defaultdict

# Define the mapping for file name components
abbreviation_map = {
    "days-remembrance": "DR",
    "epistle-son-wolf": "ESW",
    "gems-divine-mysteries": "GDM",
    "gleanings-writings-bahaullah": "GWB",
    "hidden-words": "HW",
    "kitab-i-aqdas": "KA",
    "kitab-i-iqan": "KI",
    "prayers-meditations-bahaullah": "PM",
    "call-divine-beloved": "CDB",
    "summons-lord-hosts": "SLH",
    "tabernacle-unity": "TU",
    "tablets-bahaullah": "TB",
    "additional-prayers-revealed-bahaullah": "APB",
    "additional-tablets-extracts-from-tablets-revealed-bahaullah": "ATB",
    "selections-writings-bab": "SWB",
    "memorials-faithful": "MF",
    "light-of-the-world": "LW",
    "paris-talks": "PT",
    "promulgation-universal-peace": "PUP",
    "secret-divine-civilization": "SDC",
    "selections-writings-abdul-baha": "SWAB",
    "some-answered-questions": "SAQ",
    "tablet-auguste-forel": "TAF",
    "tablets-divine-plan": "TDP",
    "tablets-hague-abdul-baha": "TTH",
    "travelers-narrative": "TN",
    "twelve-table-talks-abdul-baha": "TTT",
    "will-testament-abdul-baha": "WT",
    "prayers-abdul-baha": "TPR",
    "additional-tablets-extracts-talks-abdul-baha": "ATET",
    "additional-prayers-revealed-abdul-baha": "APR"
}

# Folder containing the text files
OUTPUT_FOLDER = "output"
OUTPUT_FILE = "output.txt"


def process_text_file(text_file, abbreviation, all_quotes):
    """Processes a text file if it exists, grouping quotes by title."""
    if not os.path.exists(text_file):
        print(f"Skipping missing file: {text_file}")
        return

    print(f"Processing text file: {text_file}")

    with open(text_file, "r", encoding="utf-8") as f:
        try:
            quotes = json.load(f)  # Expecting JSON format inside .txt files
        except json.JSONDecodeError:
            print(f"Error: Malformed JSON in {text_file}")
            return

    if not quotes:
        print(f"Warning: {text_file} is empty.")
        return

    print(f"→ Read {len(quotes)} quotes from {text_file}")

    for entry in quotes:
        title = entry["title"]
        quote_entry = f"{{{{q|{entry['quote']}|{entry['location']} |{abbreviation} }}}}"
        all_quotes[title].append(quote_entry)


def main():
    all_quotes = defaultdict(list)

    # Get all text files in the output folder
    text_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".txt")]

    if not text_files:
        print("No text files found in the output folder.")
        return

    print(f"Found {len(text_files)} text files.")

    for filename in text_files:
        # Extract everything after the first underscore
        match = re.match(r"[^_]+_(.+)\.txt", filename)
        if not match:
            print(f"Skipping invalid file: {filename}")
            continue

        key = match.group(1)  # Extracted filename part after the first underscore

        if key not in abbreviation_map:
            print(f"Warning: No abbreviation found for {key}")
            continue

        abbreviation = abbreviation_map[key]
        text_file_path = os.path.join(OUTPUT_FOLDER, filename)
        process_text_file(text_file_path, abbreviation, all_quotes)

    # Write to output file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for title, quotes in all_quotes.items():
            f.write(f"===={title}====\n")
            f.write("\n".join(quotes) + "\n\n")

    print(f"Output saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
