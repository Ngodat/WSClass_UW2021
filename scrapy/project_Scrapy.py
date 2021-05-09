import scrapy
import re
import datetime
import os
from scrapy.exporters import CsvItemExporter

###################################
URLname = 'loanURLs.csv'
try:
    URLdir = os.path.join(os.getcwd(),'../../../',URLname)                          # please change to relative links to the loanURLs.csv file if necessary
except:
    URLdir = URLname
# starting time
start = datetime.datetime.now()

###################################


# define function to manipulate the raw data
def trim(string):                                                              # remove tabs, line breaks and redundant spaces in a string
    try:
        return re.sub('[\s]{2,}','',re.sub('[\t\n\,]|\s+',' ',string))
    except:
        return ''

def concat(listOfStrings):                                                     # join a list of strings into a string
    try:
        return trim(' '.join(listOfStrings))
    except:
        return ''

def convertAmount(amountStr):                                                  # convert strings of amounts into float type
    if amountStr == '':
        return 0
    else:
        return float(re.sub('[^\d|\.]','',amountStr))

def convertPercentage(percentageStr):                                          # convert strings of percentage into float type 
    if percentageStr == 'Funded':
        return 100
    elif percentageStr == 'Expired':
        return 0
    else:
        return float(re.sub('[^\d|\.]','',percentageStr))


###################################
# define Scrapy class
class loan(scrapy.Item):
    borrowerName = scrapy.Field()
    loanAmount = scrapy.Field()
    fundingStatus = scrapy.Field()
    percentageFunded = scrapy.Field()
    timeLeft = scrapy.Field()
    amountToGo = scrapy.Field()
    country = scrapy.Field()
    sector = scrapy.Field()
    loanBrief = scrapy.Field()
    noLenders = scrapy.Field()
    loanLength = scrapy.Field()
    repaymentSchedule = scrapy.Field()
    disbursedDate = scrapy.Field()
    fundingModel = scrapy.Field()
    partnerCoverCurLoss = scrapy.Field()
    fieldPartner = scrapy.Field()
    whySpecial = scrapy.Field()
    payInterest = scrapy.Field()
    borrowerStory = scrapy.Field()
    moreAbout = scrapy.Field()
    url = scrapy.Field()

class LinksSpider(scrapy.Spider):
    name = 'kivaLoans'
    delimiter = ';'
    allowed_domains = ['kiva.org']
    try:
        with open(URLdir, "rt") as f:
            start_urls = [url.strip() for url in f.readlines()]
    except:
        start_urls = []

###################################
# design the scraper
    def parse(self, response):
        l = loan()
        borrowerName_xpath = '//h1/text()'
        loanAmount_xpath = '//div[@class = "loan-total"]/text()'
        percentageFunded_xpath = '//h2[@class = "green-bolded inline"]/text()'
        timeLeft_xpath = '//div[re:match(@class, "^days-left-stat.*")]/text()'
        amountToGo_xpath = '//div[@class = "amount-to-go-stat"]/text()'
        country_xpath = '//h2[re:match(text(),".*Country.*")]/text()'
        sector_xpath = '//span[@class = "typeName"]/text()'
        loanBrief_xpath = '//div[@class = "loan-use"]/h2/text()'
        noLenders_xpath = '//a[@class = "lender-count black-underlined"]/text()'
        loanLength_xpath = '//a[text() = "Loan length"]/../following-sibling::div[1]/text()'
        repaymentSchedule_xpath = '//a[text() = "Repayment schedule"]/following-sibling::strong[1]/text()'
        disbursedDate_xpath = '//a[text() = "Disbursed date"]/following-sibling::strong[1]/text()'
        fundingModel_xpath = '//a[text() = "Funding model"]/following-sibling::strong[1]/text()'
        partnerCoverCurLoss_xpath = '//a[text() = "Partner covers currency loss"]/following-sibling::strong[1]/text()'
        fieldPartner_xpath = '//a[text() = "Facilitated by Field Partner"]/following-sibling::strong[1]/text()'
        whySpecial_xpath = '//section[@class = "why-special"]/div[2]/div/text()'
        payInterest_xpath = '//a[text() = "Is borrower paying interest"]/following-sibling::strong[1]/text()'
        borrowerStory_xpath = '//section[@class = "loan-description"]//text()'
        moreAbout_xpath = '//div[@id = "ac-more-loan-info-body"]//text()'

        l['url'] = response.request.url
        l['borrowerName'] = response.xpath(borrowerName_xpath).get()
        l['loanAmount']  = convertAmount(trim(response.xpath(loanAmount_xpath).get()).replace('Total loan: ',''))
        l['percentageFunded'] = convertPercentage(trim(response.xpath(percentageFunded_xpath).get()))
        l['timeLeft'] = trim(response.xpath(timeLeft_xpath).get())
        l['amountToGo'] = convertAmount(trim(response.xpath(amountToGo_xpath).get()).replace(' to go',''))
        l['country'] = trim(response.xpath(country_xpath).get()).replace('Country: ','')
        l['sector'] = trim(response.xpath(sector_xpath).get())
        l['loanBrief'] = trim(response.xpath(loanBrief_xpath).get())
        l['noLenders'] = convertAmount(trim(response.xpath(noLenders_xpath).get()))
        l['loanLength'] = trim(response.xpath(loanLength_xpath).get())
        l['repaymentSchedule'] = trim(response.xpath(repaymentSchedule_xpath).get())
        l['disbursedDate'] = trim(response.xpath(disbursedDate_xpath).get())
        l['fundingModel'] = trim(response.xpath(fundingModel_xpath).get())
        l['partnerCoverCurLoss'] = trim(response.xpath(partnerCoverCurLoss_xpath).get())
        l['fieldPartner'] = trim(response.xpath(fieldPartner_xpath).get())
        l['whySpecial'] = trim(response.xpath(whySpecial_xpath).get())
        l['payInterest'] = trim(response.xpath(payInterest_xpath).get())
        l['borrowerStory'] = concat(response.xpath(borrowerStory_xpath).getall())
        l['moreAbout'] = concat(response.xpath(moreAbout_xpath).getall())
        if l['percentageFunded'] == 0:
            l['fundingStatus'] = 'Expired'
        elif l['percentageFunded'] == 100:
            l['fundingStatus'] = 'Funded'
        else:
            l['fundingStatus'] = 'Funding'
        yield l

print('Crawling loan details by BeautifulSoup completed')
print('Total crawling time:', int((datetime.datetime.now()- start).seconds)//60, ' minutes')
