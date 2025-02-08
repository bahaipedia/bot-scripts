Steps to create article/author items on Bahaidata.org from a list of articles in (for example) World Order magazine.

1. Create an item on bahaidata.org for the particular issue you want to work on (create-volume-issues.py can do this automatically)
2. Copy article details from one issue into a json file for import. See import.json for example formatting
   - Note: I use ChatGPT to quickly take lists of article/author/page details and format it approprately for import.json
   - If you have ChatGPT plus you can use this link https://chat.openai.com/g/g-Ipzj7gTcs-json-formatter and give it the data in any format you want
     - It will assume and add page ranges so you don't need to specify anything other then the starting page of an article unless the ending page is shared with the start of a new article, then you need to specify the page range manually. 
     - If there are OCR errors in the titles or authors you can use ChatGPT to correct those also
3. run "python import-articles.py Qxxx" replacing the Q number with the item for the issue you are working on
   - If the script outputs something like *Created author Lydia G. Wentworth (Q821)* copy that into a file called needed-authors.txt and refer to bot-scripts/python/README.md for the next steps.
