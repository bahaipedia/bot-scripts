These scripts are used as part of a workflow that involves several different steps, websites and frameworks. In general the steps are (scripts/steps in this folder are marked with bold):

1. Import a list of article/author pairs into bahaidata.org using bot-scripts/wikibaseintegrator/import-articles.py
   - The script outputs to console when a new author item is added, for example: *Created author Lydia G. Wentworth (Q821)*. A new author means extra work: Adding a page on bahai.works, then adding a sitelink on bahaidata.org
   - Double check the author doesn't exist, then save that line to a file called needed-authors.txt
2. **run "python needed-authors.py" which uses needed-authors.txt to create needed-authors-ready.txt**
   - The script gets the list of author names and item numbers ready to be imported into bahai.works using pywikibot's pagefromfile.py
3. run "pwb pagefromfile.py -notitle -file:needed-authors-ready.txt" (you may call pywikibot differently, paths may be different too)
   - Now bahai.works should have author pages for all the authors originally listed in needed-authors.txt.
   - They should also be categorized appropriately based on last name.
4. **run "python pages-from-cat.py" which creates a file called pages-from-cat-output.txt**
   - Copy the contents of pages-from-cat-output.txt into [[Authors]] on bahai.works, it should be adding all the authors from needed-authors.txt
5. Add sitelinks from bahaidata.org back to bahai.works author pages just created.
   - run "python api_addsitelinks.py" with your "needed-authors.txt" from before. You'll need to update your own username/password in this file.
