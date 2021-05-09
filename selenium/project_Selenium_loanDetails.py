defaultScraper = True

#########################################

# Libraries
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from time import sleep
import pandas as pd
import time
import datetime
import csv
import re

# record starting time
start = datetime.datetime.now()
#########################################
# Functions
def trim(string):                                                           # clean collected string from redundant spaces, tabs and line breaks
    try:
        return re.sub('[\s]{2,}','',re.sub('[\t\n]|\s+',' ',string))
    except:
        return string

def convertAmount(amountStr):                                               # convert collected values from string form into number value
    if amountStr == '':
        return 0
    else:
        return float(re.sub('[^\d|\.]','',amountStr))

def convertPercentage(percentageStr):                                       # convert strings of percentage into float type 
    if percentageStr == 'Funded':
        return 100
    elif percentageStr == 'Expired':
        return 0
    else:
        return float(re.sub('[^\d|\.]','',percentageStr))

#########################################

# Parameters and files
gecko_path = '/usr/local/bin/geckodriver'  
URLDir = 'loanURLs.csv'                                   
outputDir = 'loanDetails_Selenium.csv'                          # the crawling output's directory
infoFieldList = ['borrowerName','loanAmount','fundingStatus','percentageFunded','timeLeft','amountToGo','country','sector',
'loanBrief','noLenders','loanLength','repaymentSchedule','disbursedDate','fundingModel','partnerCoverCurLoss','fieldPartner','whySpecial',
'payInterest','borrowerStory','moreAbout','url']

try:                                                            # read the list of loan URLs crawled using Selenium
    with open(URLDir, "rt") as f:
        loanURLs = [url.strip() for url in f.readlines()]
except:
    loanURLs = []

#########################################

# Collect loan information for collected URLs
print('Start crawling loan details from collected URLs...')
options = webdriver.firefox.options.Options()
options.headless = True                                         # not show the browser when crawling

loanDict = dict()                                               # generate a empty data frame to save loan details
for col in infoFieldList:
    loanDict[col] = []
loanDF = pd.DataFrame(loanDict)

for url in loanURLs:                                            # read all URLs
    loan = dict()                                               # generate a new dictionary to save crawled info
    driver = webdriver.Firefox(options = options, executable_path = gecko_path)
    driver.get(url)
    while len(driver.find_elements_by_xpath('//h1[text()= "Work with us"]')) == 0: # wait until theh page is fully loaded
        time.sleep(2)

    try: # name of borrowers
        borrowerName = trim(driver.find_element_by_xpath('//h1').text)
    except:
        borrowerName = ''

    try: # amount of loan
        loanAmount = convertAmount(driver.find_element_by_xpath('//div[@class = "loan-total"]').text.replace('Total loan: ',''))
    except:
        loanAmount = 0

    try: # percentage raised
        percentageFunded = convertPercentage(trim(driver.find_element_by_xpath('//h2[@class = "green-bolded inline"]').text))
    except:
        percentageFunded = 0

    # funding status
    if percentageFunded == 0:
        fundingStatus = 'Expired'
    elif percentageFunded == 100:
        fundingStatus = 'Funded'
    else:
        fundingStatus = 'Funding'
    
    try: # number of days/hours left for the campaign
        timeLeft = trim(driver.find_element_by_xpath('//div[contains(@class,"days-left-stat")]').text)
    except:
        timeLeft = ''

    try: # amount to meet the loan target
        amountToGo = convertAmount(trim(driver.find_element_by_xpath('//div[@class = "amount-to-go-stat"]').text.replace(' to go','')))
    except:
        amountToGo = 0

    try: # borrower's country
        country = trim(driver.find_element_by_xpath('//section[@id ="country-section"]//h2').text).replace('Country: ','')
    except:
        country = ''

    try: # sector of the loan
        sector = trim(driver.find_element_by_xpath('//span[@class ="typeName"]').text)
    except:
        sector = ''

    try: # a brief description of the loan
        loanBrief = trim(driver.find_element_by_xpath('//div[@class = "loan-use"]//h2').text)
    except:
        loanBrief = ''

    try: # number of lenders support the campaign
        noLenders = trim(driver.find_element_by_xpath('//a[@class = "lender-count black-underlined"]').text)
    except:
        noLenders = ''

    try: # loan term in months
        loanLength = trim(driver.find_element_by_xpath('//a[text() = "Loan length"]/../..//following-sibling::div').get_attribute('innerHTML'))
    except:
        loanLength = ''

    try: # repayment schedule type
        repaymentSchedule = trim(driver.find_element_by_xpath('//a[text() = "Repayment schedule"]//following-sibling::strong').get_attribute('innerHTML'))
    except:
        repaymentSchedule = ''

    try: # disbursement date
        disbursedDate = trim(driver.find_element_by_xpath('//a[text() = "Disbursed date"]//following-sibling::strong').get_attribute('innerHTML'))
    except:
        disbursedDate = ''

    try: # funding model
        fundingModel = trim(driver.find_element_by_xpath('//a[text() = "Funding model"]//following-sibling::strong').get_attribute('innerHTML'))
    except:
        fundingModel = ''

    try: # whether partner Covers Currency Loss
        partnerCoverCurLoss = trim(driver.find_element_by_xpath('//a[text() = "Partner covers currency loss"]//following-sibling::strong').get_attribute('innerHTML'))
    except:
        partnerCoverCurLoss = ''

    try: # name of the field partner
        fieldPartner = trim(driver.find_element_by_xpath('//a[text() = "Facilitated by Field Partner"]//following-sibling::strong').get_attribute('innerHTML'))
    except:
        fieldPartner = ''

    try: # the special features of the loan
        whySpecial = trim(driver.find_element_by_xpath('//section[@class = "why-special"]//div[2]//div').text)
    except:
        whySpecial = ''

    try: # whether borrowers have to pay interest
        payInterest = trim(driver.find_element_by_xpath('//a[text() = "Is borrower paying interest"]//following-sibling::strong').get_attribute('innerHTML'))
    except:
        payInterest = ''

    try: # the description of borrowers
        borrowerStory = trim(driver.find_element_by_xpath('//section[@class = "loan-description"]').text)
    except:
        borrowerStory = ''

    try: # more info about the loan
        moreAbout = trim(driver.find_element_by_xpath('//div[@id = "ac-more-loan-info-body"]').get_attribute('innerText'))
    except:
        moreAbout = ''

    url = url

    # save crawled data into the dictionary and append into loan data frame
    for col in infoFieldList: 
        loan[col] = locals()[col]
    loanDF = loanDF.append(loan, ignore_index = True)
    print(url,' crawling completed!')
    driver.quit()

#########################################
# Save output URLs into a csv file
outputFile = open(URLDir, "w")
for url in loanURLs:
    outputFile.write(url+'\n')
outputFile.close()

loanDF.to_csv(outputDir, sep = ';')
print('Crawling partner details by Selenium completed')

print('Crawling loan details by BeautifulSoup completed')
print('Total crawling time:', int((datetime.datetime.now()- start).seconds)//60, ' minutes')
