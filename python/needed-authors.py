r""" 
This script processes a list of author names from the file needed-authors.txt in this format:

Created author Lydia G. Wentworth (Q821)
Created author Ethel Nash Crane (Q822)

and outputs them in a format that can be used by the pywikibot script pagefromfile.py

Usage: python needed-authors.py
"""

def process_line(line):
    # Extracting the author's name and identifier
    parts = line.strip().split()
    name = ' '.join(parts[2:-1])
    identifier = parts[-1][1:-1]  # Removes parentheses
    return name, identifier

def format_author_block(name, identifier):
    # Formatting the output for each author
    return f"""{{{{-start-}}}}
'''Author:{name}'''
{{{{author2|wb={identifier}}}}}

===Articles===
====World Order====
<section begin=wo_article/>
{{{{#invoke:WorldOrder|getArticlesByAuthor|{identifier}}}}}
<section end=wo_article/>
__NOTOC__
{{{{-stop-}}}}\n"""

def main():
    input_file = 'needed-authors.txt'
    output_file = 'needed-authors-ready.txt'

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            if line.strip():
                name, identifier = process_line(line)
                author_block = format_author_block(name, identifier)
                outfile.write(author_block)

if __name__ == "__main__":
    main()
