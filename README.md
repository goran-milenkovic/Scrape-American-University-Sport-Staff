# Scrape

Command line tool for scraping an University Staff Directory pages and printing out the staff contact information for the specified sport. 

Contact information is contained in HTML table rows and cells ("tr" and "td" elements). The tool takes two required input parameters for a page to be scraped and sport to be filtered, as well as optional parameters to help with locating the table rows and cells.

Input format:

    python scrape.py --url=page_url --sport=sport_name

or:

    python scrape.py --url=page_url --sport=sport_name --html-element=element_name --html-element-id=element_id

or:

    python scrape.py --url=page_url --sport=sport_name --html-element=element_name --html-element-index=element_index 

or:

    python scrape.py --url=page_url --sport=sport_name --html-element=element_name --html-element-class=element_class

Input parameters:

- (required) page_url - the Staff Directory page URL to be scraped (e.g. each one of the Test URLs below)
- (required) sport_name - the sport name to be filtered (case insensitive, e.g. "volleyball")
- (optional) element_name - the name of the HTML element to be searched for (e.g. "tr" or "table")
- (optional, mutually exclusive) element_id, element_index, or element_class - the id, index, or HTML style class of the specified HTML element to be searched for (e.g. id "Table1", or index 1, or HTML style class "sport-name")

Test URLs:

- Seattle University Staff Directory (http://www.goseattleu.com/StaffDirectory.dbml)
- Arkansas State Red Wolves Athletic Staff Directory (http://www.astateredwolves.com/ViewArticle.dbml?ATCLID=207138)
- Arizona Wildcats Athletics Staff Directory (https://athletics.arizona.edu/StaffDirectory/index.asp)

The output is in JSON format, e.g. for the first Test URL and "volleyball" as a sport:

    [
        {
            "sport": "volleyball",
            "name": "Michelle Cole",
            "position": "Head Coach",
            "phone": "(206) 296-6426",
            "email": "mcole1@seattleu.edu"
        },
        {
            "sport": "volleyball",
            "name": "Michael Hobson",
            "position": "Assistant Coach",
            "phone": "",
            "email": "mhobson@seattleu.edu"
        },
        {
            "sport": "volleyball",
            "name": "Amber Cannady",
            "position": "Assistant Coach",
            "phone": "",
            "email": "acannady@seattleu.edu"
        }      
    ]

## Bonus Option

URL might point to the page that has an iframe HTML element, with the Staff Directory page loaded as a sub-page. The tool is able to recognize such situation (i.e. if no results have been found and the page contains iframe elements), proceed with loading the iframe source, and repeat the search. URL below is to test this functionality.

Bonus Option Test URL:
- Arizona Wildcats Athletics Staff Directory (https://arizonawildcats.com/sports/2007/8/1/207969432.aspx)
