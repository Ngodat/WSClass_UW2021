
# Load libraries
from bs4 import BeautifulSoup as BS
from urllib import request
import re
import datetime
import pandas as pd

###################################
# starting time
start = datetime.datetime.now()

# Define functions
def bsParse(url):                                                                               # parse the url string for scraping 
    return BS(request.urlopen(url).read(), 'html.parser')

def trim(string):                                                                               # clean collected string from redundant spaces, tabs and line breaks
    try:
        return re.sub('[\s]{2,}','',re.sub('[\t\n]|\s+',' ',string))
    except:
        return string

def convertAmount(amountStr):                                                                   # convert collected values from string form into number value
    if amountStr == '':
        return 0
    else:
        return float(re.sub('[^\d|\.]','',amountStr))

def convertPercentage(percentageStr):                                                           # convert strings of percentage into float type 
    if percentageStr == 'Funded':
        return 100
    elif percentageStr == 'Expired':
        return 0
    else:
        return float(re.sub('[^\d|\.]','',percentageStr))

###################################

# Set parameters to crawl data
URLDir = 'loanURLs.csv'
outputDir = 'loanDetails_BS.csv'                                                                  # the output file name
infoFieldList = ['borrowerName','loanAmount','fundingStatus','percentageFunded','timeLeft','amountToGo','country','sector',
'loanBrief','noLenders','loanLength','repaymentSchedule','disbursedDate','fundingModel','partnerCoverCurLoss','fieldPartner','whySpecial',
'payInterest','borrowerStory','moreAbout','url']  #list of fields to crawl on each lending partner's page

try:
    with open(URLDir, "rt") as f:
        loanURLs = [url.strip() for url in f.readlines()]
except:
    loanURLs = []

loanDict = dict()
for col in infoFieldList:
    loanDict[col] = []
loanDF = pd.DataFrame(loanDict)

###################################

# Crawling data
print("Start crawling loan info")
for url in loanURLs:
    loan = dict()
    bs = bsParse(url)
    try:  # name of borrower
        borrowerName = trim(bs.find('h1').get_text())
    except:
        borrowerName = ''
    
    try: # loan amount
        loanAmount = convertAmount(bs.find('div',{'class': "loan-total"}).get_text())
    except:
        loanAmount = 0  
    
    try: # percentage of funded
        percentageFunded = convertPercentage(bs.find('h2',{'class': "green-bolded inline"}.get_text()))
    except:
        percentageFunded = 0

    # funding status
    if percentageFunded == 0:
        fundingStatus = 'Expired'
    elif percentageFunded == 100:
        fundingStatus = 'Funded'
    else:
        fundingStatus = 'Funding'
    
    try: # timeLeft
        timeLeft = trim(bs.find('div',{'class':'goal-stats'}).find(lambda tag: tag.name == 'div' and 'left' in tag.text).get_text())
    except:
        timeLeft = ''

    try: # amount to go 
        amountToGo = convertAmount(bs.find('div',{'class':'amount-to-go-stat'}).get_text())
    except:
        amountToGo = ''

    try: # country of borrowers
        country = trim(bs.find(lambda tag: tag.name == 'h2' and 'Country' in tag.text).get_text().replace('Country: ',''))
    except:
        country = ''

    try: # loan sector
        sector = trim(bs.find('span',{'class':'typeName'}).get_text())
    except:
        sector = ''

    try: # loan brief description
        loanBrief = trim(bs.find('div',{'class':'loan-use'}).h2.get_text())
    except:
        loanBrief = ''

    try: # number of lenders
        noLenders = convertAmount(bs.find('a',{'class':'lender-count black-underlined'}).get_text())
    except:
        noLenders = 0

    try: #loan term by months
        loanLength = trim(bs.find('a', string = 'Loan length').parent.findNextSibling('div').get_text())
    except:
        loanLength = ''

    try: # repayment schedule
        repaymentSchedule = trim(bs.find('a', string = 'Repayment schedule').findNextSibling('strong').get_text())
    except:
        repaymentSchedule = ''

    try: # disbursement Date
        disbursedDate = trim(bs.find('a', string = 'Disbursed date').findNextSibling('strong').get_text())
    except:
        disbursedDate = ''

    try: # funding Model
        fundingModel = trim(bs.find('a', string = 'Funding model').findNextSibling('strong').get_text())
    except:
        fundingModel = ''

    try: # whether partner Covers Currency Loss
        partnerCoverCurLoss = trim(bs.find('a', string = 'Partner covers currency loss').findNextSibling('strong').get_text())

    except:
        partnerCoverCurLoss = ''

    try: # field Partner name
        fieldPartner = trim(bs.find('a', string = 'Facilitated by Field Partner').findNextSibling('strong').get_text())
    except:
        fieldPartner = ''

    try: # the loan's special features
        whySpecial = trim(bs.find('section',{'class':'why-special'}).find_all('div')[1].find('div').get_text())
    except:
        whySpecial = ''

    try: # whether the borrowers have to pay interest
        payInterest = trim(bs.find('a', string = 'Is borrower paying interest').findNextSibling('strong').get_text())
    except:
        payInterest = ''

    try: # borrower's story
        borrowerStory = trim(bs.find('section',{'class':'loan-description'}).get_text())
    except:
        borrowerStory = ''

    try: # more info about the loan
        moreAbout = trim(bs.find('div',{'id':'ac-more-loan-info-body'}).get_text())
    except:
        moreAbout = ''

    url = url

    ### save the crawled data into a dictionary and append into the dataframe 
    for col in infoFieldList:
        loan[col] = locals()[col]
    loanDF = loanDF.append(loan, ignore_index = True)
    print(loan['url'],' crawling completed!')

## 3. save the dataframe into a csv file
loanDF.to_csv(outputDir, sep = ';')
print('Crawling loan details by BeautifulSoup completed')
print('Total crawling time:', int((datetime.datetime.now()- start).seconds)//60, ' minutes')














