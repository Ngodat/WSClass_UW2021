# WSClass_UW2021
The final project for class Webscraping, Faculty of Economic Sciences, Uni of Warsaw.
The project include 2 stages of scraping loan details from kiva.org
## Stage 1: Crawling loan URLs using selenium script: project_Selenium_URLs.py and the list of options in loan countries, borrower gender, loan type
To run the script using terminal: $ python project_Selenium_URLs.py
The output is file named 'loanURLs.csv'; would be use in stage 2.

## Stage 2: Crawling loan information from URLs in stage 1
Using Selenium
On the terminal: $ python project_Selenium_loanDetails.py
The output is 'loanDetails_Selenium.csv'

### Using Beautiful Soup
On the terminal: S python project_BeautifulSoup.py
The output is 'loanDetails_BS.csv'

### Using Scrapy
Before running the spider, please change the user_agent value in the setting.py file:
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0'

After that, run the script on the termnial $ scrapy crawl kivaLoans -O loanDetails_Scrapy.csv
The output is 'loanDetails_Scrapy.csv'

### Please look for the project description in the file "description.pdf"
