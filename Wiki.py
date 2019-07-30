from __future__ import print_function
from __future__ import unicode_literals
import csv, time, gspread, os, sys, shutil, httplib2, requests
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery, http
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoAlertPresentException
from urllib.error import HTTPError
from http.client import RemoteDisconnected
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pytube import YouTube
from pytube.exceptions import VideoUnavailable, RegexMatchError
from stat import S_ISREG, ST_CTIME, ST_MODE
from pathlib import Path

import youtube_dl
from youtube_dl import YoutubeDL

import re




# chromedriver location

chromedriver = '/Users/edwinaramburo/Desktop/Projects/Web-Video-Scaper/chromedriver'

driver = webdriver.Chrome(chromedriver)

# use credentials to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "/Users/edwinaramburo/Desktop/Projects/Web-Video-Scaper/credentials.json", scope)
client = gspread.authorize(creds)


# Creates array of college names
def getCollegeNames(sheet):
    CollegeArr = sheet.col_values(1)
    return CollegeArr


# Creates array of College Descriptions
def getVideoDescriptions(sheet):
    URLArr = sheet.col_values(3)
    return URLArr


# Creates array of Video Titles
def getVideoTitles(sheet):
    TitleArr = sheet.col_values(4)
    return TitleArr


# function to remove all college name formatting
# def stripFormat(str):
#     # print("Strip Format\n")
#     str = str.replace("[", "").replace("]","").replace("1","").replace("1 ","").replace("2","").replace("2 ","").replace("3","").replace("3 ","").replace("4","").replace("4 ","")\
#     .replace("5","").replace("5 ","").replace("6","").replace("6 ","").replace("7","").replace("7 ","").replace("8","").replace("8 ","")\
#     .replace("9","").replace("9 ","").replace("0","").replace("0 ","")\
#     return str

# function to remove all college name formatting
def stripCollegeName(str):
    str = str.replace("-", " ")
    return str



def stripDescription(str):
    # print("Strip Format\n")
    str = re.sub('\[.*?\]','', str)
    return str

# Function to first paragraph on Wikipedia
def getDescription(sheet, college_names):
    print("Getting description...\n")
    row_count = 1
    # goes through every school in the array
    for college in college_names:
        college = stripCollegeName(college)
        print(college+"\n")
        driver.get("https://en.wikipedia.org/wiki/"+ college)
        time.sleep(3)

        try:
            # Grabs getDescription
            description = driver.find_element_by_xpath("//*[@class='mw-parser-output']/p[2]")
            print(description.text+"\n")
            cell_reference = "C" + str(row_count)
            sheet.update_acell(cell_reference, description.text)

            # Clicks APA Citation link
            citation_link = driver.find_element_by_xpath("//*[@id='t-cite']/a")
            # print(citation_link.text)
            citation_link.click()
            time.sleep(3)

            # Copies APA Citation
            citation = driver.find_element_by_xpath("//*[@id='mw-content-text']/div[3]/p[1]")
            print("\n")
            print(citation.text)


            cell_reference = "D" + str(row_count)
            sheet.update_acell(cell_reference, citation.text)
            row_count+=1

        except NoSuchElementException:
            # Handles the campus error
            cell_reference = "C" + str(row_count)
            sheet.update_acell(cell_reference, "CAMPUS ERROR")
            row_count+=1

def formatDescription(sheet, descriptions):
    print("Formatting description\n")
    row_count=1
    # descriptions = sheet.col_values(3)
    for d in descriptions:
        d = stripDescription(d)
        print(d)
        # print("Checking categories")
        time.sleep(10)
        cell_reference = "C" + str(row_count)
        # print(cell_reference)
        sheet.update_acell(cell_reference,d)
        # time.sleep(3)
        row_count+=1
        # print("MATCH")
    print("FINISHED AUDITING description")

def getHeaderImage(sheet, college_names):
    # for college in college_names:
    driver.get("https://www.google.com/imghp?hl=en")
    time.sleep(3)
    search = driver.find_element_by_name("q")
    search.send_keys("University of Georgia")
    search.send_keys(Keys.RETURN)
    time.sleep(5)

    tools = driver.find_element_by_id("hdtb-tls")
    tools.click()

    more_tools = driver.find_element_by_xpath("/html/body/div[@id='main']/div[@id='cnt']/div[@id='rshdr']/div[@id='top_nav']/div[1]//div[@id='hdtbMenus']/div[@class='hdtb-mn-cont']/div[2]")
    # size = more_tools[1]
    print(more_tools.text)
    more_tools.click()



# Main Function
def automate(sheetname):
    print("Active\n")

    # saves spreadsheet being used
    sheet = client.open(sheetname).sheet1

    descriptions = getVideoDescriptions(sheet)
    # print(descriptions)

    # creates arrays for video urls and college names
    # video_URLS = getVideoURLS(sheet)
    college_names = getCollegeNames(sheet)
    # print(college_names)


    # creates array of video titles
    # video_titles = getVideoTitles(sheet)

    # creates array of video categories
    # video_categories = formatCategories(sheet)

    # creates array for file name
    # file_name = getFileName(sheet)



#############FUNCTIONS#####################

    #1 -> Uses spread sheet to acquire all iped ids
    # getDescription(sheet, college_names)
    # 2
    # formatDescription(sheet, descriptions)
    #3
    getHeaderImage(sheet, college_names)


automate("Wikipedia DB")
