defaultScraper = True

#########################################

# Libraries
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from time import sleep
import pandas as pd
import time
import csv
import re

#########################################
# Functions
def properText(string):                                             # convert string to proper form (to match kiva's format)
    return ' '.join(list(map(lambda x: x.capitalize(),string.split(' '))))

def checkItemList(list1, list2):                                    # check whether user's input included in the filter options on Kiva.org page
    result = True
    if len(list1) == 0 or list1 == ['']:
        return (result, 0)
    else:    
        for i in list1:
            if i not in list2:
                result = False
                break
    return (result, i)

#########################################

# Parameters and files
gecko_path = '/usr/local/bin/geckodriver'                           #path to gecko driver
url = 'https://www.kiva.org/lend?page=1'                            #starting URL to crawling data
countryListFile = 'countries.csv'                                   #file contains all countries in kiva's list of filter options
sectorListFile = 'sectors.csv'                                      #file contains all sectors in kiva's list of filter options                  
genderDict = {'1': 'Women','2':'Men'}                               #dictionary of borrower gender options
typeDict = {'1': ('Individual','false'),'2':('Group','true')}       #dictionary of loan type options
statusDict = {'1': 'fundRaising','2':'funded','': 'all'}            #dictionary of loan status options
lengthDict = {'1': ('8 mths or less','0,8'),
                '2':('16 mths or less','0,16'),                     #dictionary of loan length options
                '3': ('2 yrs or less','0,24'),
                '4': ('2 yrs or more','24,400')}
dfCountryList = pd.read_csv(countryListFile).astype(str)            #read the list of country options 
dfSectorList = pd.read_csv(sectorListFile).astype(str)              #read the list of sector options 
URLDir = 'loanURLs.csv'                                             #the crawling output's directory
loanDetailDir = 'loanDetails_Selenium.csv'
infoFieldList = ['borrowerName','loanAmount','fundingStatus','percentageFunded','timeLeft','amountToGo','country','sector',
'loanBrief','noLenders','loanLength','repaymentSchedule','disbursedDate','fundingModel','partnerCoverCurLoss','fieldPartner','whySpecial',
'payInterest','borrowerStory','moreAbout','url']

#########################################

# User's loan filter input
## Ask user to crawl by default (all loans)
defaultSelect = input("Do you want to crawl by default (all loans) Y/N? ")

if defaultSelect.lower() == "y" or defaultSelect.lower() == "yes":  #the default option, all loans
    selectedCountryNames = ''
    selectedSectorNames = ''
    genderOption = ''
    typeOption = ''
    statusOption = ''
    loanLength = ''
    keyWords = ''
else:                                                               #ask users to input filters
    ## 1. Borrower's countries
    print("Please select ID of countries on the following list. For all countries, please press Enter")
    print(dfCountryList.to_string(index=False))
    print("Example: 1,2")
    time.sleep(1)
    selectedCountryIDs = list(input("Loan countries: ").replace(' ','').split(','))
    while not checkItemList(selectedCountryIDs,dfCountryList.ID.tolist())[0]:
        print(checkItemList(selectedCountryIDs,dfCountryList.ID.tolist())[1], " is not in the country list to select, please input again")
        selectedCountryIDs = list(input("Loan countries: ").replace(' ','').split(','))
    selectedCountryNames = list(dfCountryList[dfCountryList.ID.isin(selectedCountryIDs)].Country)

    ## 2. Loan sectors
    print("Please select ID of sectors on the following list. For all sectors, please press Enter")
    print(dfSectorList.to_string(index=False))
    print("Example: 1,2")
    time.sleep(1)
    selectedSectorIDs = list(input("Loan sectors: ").replace(' ','').split(','))
    while not checkItemList(selectedSectorIDs,dfSectorList.ID.tolist())[0]:
        print(checkItemList(selectedSectorIDs,dfSectorList.ID.tolist())[1], " is not in the sector list to select, please input again")
        selectedSectorIDs = list(input("Loan Sectors: ").replace(' ','').split(','))
    selectedSectorNames = list(dfSectorList[dfSectorList.ID.isin(selectedSectorIDs)].Sector)
        
    ## 3. Borrower Gender
    print("\nPlease select ID of borrower's gender. For all genders, please press Enter")
    print("1 Women\n2 Men")
    genderOption = input("Borrower's gender option:")
    while genderOption not in ['1','2','']:
        print(genderOption, 'is not in the list, please select again!')
        genderOption = input("Borrower's gender option:")
        
    ## 4. Loan type (individual or group)
    print("\nPlease select ID of loan type (individual or group). For all loan types, please press Enter")
    print("1 Individual\n2 Group")
    typeOption = input("Loan type option:")
    while typeOption not in ['1','2','']:
        print(typeOption, 'is not in the list, please select again!')
        typeOption = input("Loan type option:")

    ## 5. Loan length
    print("\nPlease select ID of loan length. For all loan length values, please press Enter")
    print("1 8 months or less\n2 16 months or less\n3 2 years or less\n4 2 years or more")
    loanLength = input("Loan length option:")
    while loanLength not in ['1','2','3','4','']:
        print(loanLength, 'is not in the list, please select again!')
        loanLength = input("Loan length option:")
        
    ## 6. Keywords input
    keyWords = input('Please input keywords to search loans: ')

    ## 7. Loan status
    print("\nPlease select ID of loan status (fundraising or funded). For both statuses, please press Enter")
    print("1 Fundraising\n2 Funded")
    statusOption = input("Loan status option:")
    while statusOption not in ['1','2','']:
        print(statusOption, 'is not in the list, please select again!')
        statusOption = input("Loan status option:")
        

#########################################

# Filter loans using webdriver
print ('\nPlease wait, crawling URLs from Kiva.org ...')
## 0. Access the webpage with webdriver
options = webdriver.firefox.options.Options()
options.headless = False
driver = webdriver.Firefox(options = options, executable_path = gecko_path)
driver.get(url)
time.sleep(3)

## 1. Accept cookies button to start crawling
try:
    acceptButton = driver.find_element_by_xpath("//button[@id = 'onetrust-accept-btn-handler']")
    acceptButton.click()
except:
    pass

## 2. Click the filter button
filterButton = driver.find_element_by_xpath("/html/body/div[4]/div[3]/div/div/div[1]/div[2]/div[2]/div[1]/a")
filterButton.click()

## 3. Select borrower countries
driver.find_element_by_xpath("//a[@data-reveal-id = 'countrySelectModal']").click()
time.sleep(3)
if len(selectedCountryNames) > 0:
    for i in range(len(selectedCountryNames)):
        checkBoxList = [driver.find_element_by_xpath("//div[contains(., '{0}')][@class = 'country filter checkbox-input']".format(countryName)) for countryName in selectedCountryNames]
        time.sleep(6)
        checkBoxList[i].find_element_by_xpath(".//input[@class = 'countryCheckbox']").click()
        time.sleep(6)
driver.find_element_by_id("filter-country-submit").click()
time.sleep(2)

## 4. Select loan sectors
if len(selectedSectorNames) > 0:
    for i in range(len(selectedSectorNames)):
        checkBoxList = [driver.find_element_by_xpath("//li[contains(., '{0}')][@class = 'filter checkbox-input']".format(sectorName)) for sectorName in selectedSectorNames]
        time.sleep(3)
        checkBoxList[i].find_element_by_xpath(".//input[@name = 'filter-sector']").click()
        time.sleep(3)
time.sleep(1)

## 5. Select Gender Filter
if genderOption in genderDict.keys():
    gender = driver.find_element_by_xpath("//div[@class = 'gender-button-box triple-state-buttons']").\
            find_element_by_xpath(".//*[text() = '{0}']".format(genderDict[genderOption][0]))
    gender.click()
time.sleep(1)

    
## 6. Select Borrower Type Filter
if typeOption in typeDict.keys():
    type = driver.find_element_by_xpath("//div[@class = 'isGroup-button-box triple-state-buttons']").\
            find_element_by_xpath(".//*[text() = '{0}']".format(typeDict[typeOption][0]))
    type.click()
time.sleep(1)

## 7. Select loan length 
if loanLength in lengthDict.keys():
    loanLengthDiv = driver.find_element_by_xpath("//div[@class = 'lenderTerm-button-box quintuple-state-buttons']")
    loanLengthDiv.find_element_by_xpath(".//label[text() = '{0}']".format(lengthDict[loanLength][0])).click()
time.sleep(1)

## 8. Input search keywords
driver.find_element_by_xpath("//input[@id = 'filter-keywords-search-box']").send_keys(keyWords)
time.sleep(1)


## 9. Select loan status
if statusOption in statusDict.keys():
    driver.find_element_by_id('filter-loan-status-dropdown').click()
    time.sleep(1)
    driver.find_element_by_xpath(".//option[@value = '{0}']".format(statusDict[statusOption])).click()
    time.sleep(3)
time.sleep(1)

#########################################

# Collect information of loans on pages
## 1. Collect loan URLs
loanURLs = []
pageno = 1                                  # number of page crawled
if defaultScraper:                          # the maximum number of URLs
    urlMax = 100
else:
    urlMax = 10**4

while True:
    try:
        while len(driver.find_elements_by_xpath("//a[@class = 'next button secondary ']")) == 0:        # if there is no next page button,wait until the page is fully loaded
            time.sleep(2)
            if len(driver.find_elements_by_xpath("//div[@class = 'paging hide']")) > 0\
            or (len(driver.find_elements_by_xpath("a[@class='last button secondary ']")) == 0\
            and len(driver.find_elements_by_xpath("//a[@class = 'next button secondary ']")) > 0):      # if the page has no loans or the page is the final page, stop waiting 
                break
        # crawl loan info
        loanURLs += [x.get_attribute('href')+'?minimal=false' for x in driver.find_elements_by_xpath("//a[@class = 'loan-card-2-borrower-name']")]   # crawling loan URLs
        print('Page no. {0} completed'.format(pageno))
        pageno += 1
        nextPage = driver.find_element_by_xpath("//a[@class = 'next button secondary ']")               # find and click the next page button
        nextPage.click()  
        time.sleep(1)
        if len(loanURLs) > urlMax:                                                                      # if the number of crawled loan is greater 100, stop crawling 
            break
    except Exception as e1:
        print("End of crawling!")
        break

if len(loanURLs) > urlMax:                                                                              # select at no more than 100 URLs
    loanURLs = loanURLs[:(urlMax - len(loanURLs))]

if len(loanURLs) == 0:
    print('No loan found!')
else:
    print('{0} URLs collected'.format(len(loanURLs)))

#########################################
# Save output URLs into a csv file
outputFile = open(URLDir, "w")
for url in loanURLs:
    outputFile.write(url+'\n')
outputFile.close()


