These scripts are used as part of a workflow that involves several different steps, websites and frameworks. Scripts from this folder are marked with bold below.

1. Import a list of article/author pairs into bahaidata.org using bot-scripts/wikibaseintegrator/import-articles.py
   - The script outputs to console when a new author item is added, for example: *Created author Lydia G. Wentworth (Q821)*. A new author means extra work: Adding a page on bahai.works, then adding a sitelink on bahaidata.org
   - Double check the author is not already listed on [bahai.works](https://bahai.works/Authors), then save that line to a file called needed-authors.txt
2. **run "python api_addpages_works.py"** which uses needed-authors.txt to create author pages on bahai.works when none existed before.
3. **run "python api_addsitelinks_data.py"** which uses needed-authors.txt to add sitelinks from bahaidata.org to the newly created bahai.works pages
4. **run "python pages-from-cat.py"** which creates a file called pages-from-cat-output.txt
   - Copy the contents of pages-from-cat-output.txt into [[Authors]] on bahai.works, it should be adding all the authors from needed-authors.txt
5. Cleanup: Delete *pages-from-cat-output.txt* and remove all content from needed-authors.txt for next time.
