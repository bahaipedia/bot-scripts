Steps to create article/author items on Bahaidata.org from a list of articles in (for example) World Order magazine.

1. Create an item on bahaidata.org for the issue you want to work on (create-volume-issues.py can do this automatically)
2. Copy article details from one issue into a json file for import. See import.json for example formatting.
  - Note: I use ChatGPT to quickly take lists of article/author/page details and format it approprately for import.json
  - If you have ChatGPT plus you can use this link https://chat.openai.com/g/g-Ipzj7gTcs-json-formatter and you just need to give it the data in any format you want
  - If there are OCR errors in the titles or authors you can use ChatGPT to correct those also
3. run "python import-articles.py Qxxx" replacing the Q number with the item for the issue you are working on
