r"""
This script uses the bahai.org/library api to retreive a list of quotes for a certain keyword 

Create an "output" folder where this script exists

To fill in the <REPLACEME> sections below 
 1: navigate to https://www.bahai.org/library/authoritative-texts/search#q=faith
 2: Find the "Network" tab in the browser developer console, highlight "Fetch/XHR"
 3: Click on a search result or anything
 4: Find "_search" then right click > copy > copy as cURL
 5: Look for "-H 'authorization: Basic...."
 6. You may want to change the URL endpoint also...
 
Usage: python search_api.py <keyword>

"""

import requests
import json
import sys
import time
import random
import os

# API Endpoint
url = "https://f4e3b80fb962746a74ba859b4b27e7d6.us-east-1.aws.found.io/library/_search"

# Authorization
headers = {
    "Authorization": "Basic <REPLACEME>",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

# Function to perform search with rate limiting
def search_bahai_library(query, keyword_filter, batch_size=50, max_retries=5):
    all_results = []
    from_index = 0

    while True:
        payload = {
            "query": {
                "bool": {
                    "must": {
                        "query_string": {
                            "query": query,
                            "fields": ["content_en.en_norm^10", "content_en.en_norm_stem"],
                            "default_operator": "AND"
                        }
                    },
                    "should": {
                        "multi_match": {
                            "query": query,
                            "type": "phrase",
                            "operator": "and",
                            "fields": ["content_en.en_norm^100", "content_en.en_norm_stem^50"]
                        }
                    },
                    "filter": {
                        "term": {"unit": "para"}
                    }
                }
            },
            "post_filter": {
                "bool": {
                    "filter": [{"term": {"keywords": keyword_filter}}]
                }
            },
            "sort": {"_score": "desc"},
            "from": from_index,
            "size": batch_size
        }

        retries = 0
        while retries < max_retries:
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                results = response.json().get("hits", {}).get("hits", [])
                if not results:
                    return all_results  # No more results, stop fetching

                for hit in results:
                    source = hit["_source"]
                    all_results.append({
                        "title": source.get("title"),
                        "location": source.get("location"),
                        "quote": source.get("content_en")
                    })

                from_index += batch_size  # Move to the next batch

                # Randomized delay (10 to 30 seconds) to prevent rate limiting
                time.sleep(random.uniform(10, 30))
                break

            elif response.status_code == 429:
                # Too many requests - exponential backoff
                wait_time = (2 ** retries) + random.uniform(0, 1)
                print(f"Rate limit hit. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
                retries += 1
            else:
                print(f"Error {response.status_code} for keyword '{keyword_filter}': {response.text}")
                return all_results

    return all_results

# Read keyword filters from file
def load_keyword_filters(filename="keyword_filter.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        sys.exit(1)

# Command-line input handling
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_api.py <query>")
        sys.exit(1)

    query = sys.argv[1]
    keyword_filters = load_keyword_filters()

    for keyword in keyword_filters:
        results = search_bahai_library(query, keyword)

        if results:
            filename = os.path.join('output', f"{query}_{keyword}.txt")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"Saved results to {filename}")

        # Additional delay between keyword requests (to prevent excessive API calls)
        time.sleep(random.uniform(15, 20))
