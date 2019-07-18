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




# chromedriver location

chromedriver = '/Users/edwinaramburo/Desktop/Projects/Web-Video-Scaper/chromedriver'

driver = webdriver.Chrome(chromedriver)

# use credentials to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "/Users/edwinaramburo/Desktop/Projects/Web-Video-Scaper/client_secret.json", scope)
client = gspread.authorize(creds)


# Creates array of college names
def getCollegeNames(sheet):
    CollegeArr = sheet.col_values(1)
    return CollegeArr


# Creates array of Video URLs
def getVideoURLS(sheet):
    URLArr = sheet.col_values(6)
    return URLArr


# Creates array of Video Titles
def getVideoTitles(sheet):
    TitleArr = sheet.col_values(4)
    return TitleArr


def getFileName(sheet):
    titles = sheet.col_values(4)
    fileArr = []
    count = 0
    for title in titles:
        fileArr.append(stripFormat(title))
        count += 1
    return fileArr


# function to remove all college name formatting
def stripFormat(str):
    # print("Strip Format\n")
    str = str.replace(";", "").replace(":", "").replace("-", " ").replace("|", " ").replace(" | ", "").replace("| ","").replace("'","").replace(",", " ")\
    .replace("?", " ").replace("/", " ").replace("\"", " ").replace("(","").replace(")","").replace("@"," ")\
    .replace("&"," ").replace(".","").replace("!","").replace("#","").replace("  ","")\
    .replace("1","").replace("1 ","").replace("2","").replace("2 ","").replace("3","").replace("3 ","").replace("4","").replace("4 ","")\
    .replace("5","").replace("5 ","").replace("6","").replace("6 ","").replace("7","").replace("7 ","").replace("8","").replace("8 ","")\
    .replace("9","").replace("9 ","").replace("0","").replace("0 ","")\
    .replace("Video","").replace("video","")\
    .replace("Promo","").replace("promo","")\
    .replace("Intro","").replace("intro ","")\
    .replace("trailer","").replace("Trailer","")\
    .replace("Fall","").replace("fall","").replace("Fall%","").replace("fall ","")\
    .replace("Commercial","").replace("commercial","").replace("`","").replace("~","").replace("Hype","")\
    .replace("HYPE","").replace("hype","")\
    .replace(" - ","").replace("'","").replace("–","").replace("’","").replace("｜","")\
    .replace("Preview","").replace("preview","").replace("PREVIEW","")\
    .replace("+","").replace("[","").replace("]","").replace("@","")\
    .replace(")","").replace("(","").replace("seconds","").replace("SECONDS","")
    return str.lstrip()

# function to remove all college name formatting
def formatSchool(str):
    # print("Strip Format\n")
    str = str.replace(" ", "_").replace("-","#")
    return str

# Function to first paragraph on Wikipedia
def getDescription(sheet, college_names):
    print("Getting description...\n")
    row_count = 1
    # goes through every school in the array
    for college in college_names:
        college = formatSchool(college)
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
            sheet.update_acell(cell_reference, "ERROR")
            row_count+=1



# Main Function
def automate(sheetname):
    print("Active\n")

    # saves spreadsheet being used
    sheet = client.open(sheetname).sheet1

    # creates arrays for video urls and college names
    # video_URLS = getVideoURLS(sheet)
    college_names = getCollegeNames(sheet)
    print(college_names)


    # creates array of video titles
    # video_titles = getVideoTitles(sheet)

    # creates array of video categories
    # video_categories = formatCategories(sheet)

    # creates array for file name
    # file_name = getFileName(sheet)



#############FUNCTIONS#####################

    #1 -> Uses spread sheet to acquire all iped ids
    getDescription(sheet, college_names)

automate("Wikipedia DB")
