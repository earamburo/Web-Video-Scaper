from __future__ import print_function
from __future__ import unicode_literals
import csv, time, gspread, os, sys, shutil, httplib2, requests
from oauth2client.service_account import ServiceAccountCredentials
from apiclient import discovery, http
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


# import pyscreenshot as ImageGrab
import os
import string


# chromedriver folder

chromedriver = '/Users/edwinaramburo/Desktop/Projects/Web-Video-Scaper/chromedriver'
driver = webdriver.Chrome(chromedriver)

# credential folder
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# credentials location         #
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "/Users/edwinaramburo/Desktop/Projects/Web-Video-Scaper/credentials.json", scope)
client = gspread.authorize(creds)



# Creates array of college names
def getCollegeNames(sheet):
    CollegeArr = sheet.col_values(1)
    return CollegeArr

# Creates array of category names
def getCategories(sheet):
    CatArr = sheet.col_values(5)
    return CatArr

# Creates array of Video URLs
def getVideoURLS(sheet):
    URLArr = sheet.col_values(6)
    return URLArr

# function to remove all college name formatting
def stripFormat(str):
    # print("Strip Format\n")
    str = str.lower().replace("a","").replace("b","").replace("c", " ").replace("d", " ").replace("e", "").replace("f","").replace("g","").replace("h", " ")\
    .replace("i","").replace("j","").replace("k","").replace("l","").replace("m","").replace("n","")\
    .replace("o","").replace("p","").replace("q","").replace("r","").replace("s","")\
    .replace("t","").replace("u","").replace("v","").replace("w","").replace("x","").replace("y","").replace("z","").rstrip('.')
    return str.strip()

# Gets Title from Youtube
def gpa_stats(driver, sheet, row_count, college):

    print("Sport stats")
    try:
        driver.get("https://www.princetonreview.com/college-search/?majors=14.3501&page=2")
        search = driver.find_element_by_class_name("tt-input")
        search.send_keys(college)     # inputs video url
        search.send_keys(Keys.RETURN)
        # hs_gpa = driver.find_elements_by_class_name("number-callout")
        hs_gpa = driver.find_element_by_xpath("//*[@id='admissions']/div[1]/div[2]/div/div[3]/div[2]")
        # hs_gpa = driver.find_element_by_xpath("//*[@class='tab-pane']/div[1]/div[2]/div[4]/div[2]")
        hs_gpa = hs_gpa.text

        cell_reference = "E" + str(row_count)
        sheet.update_acell(cell_reference, hs_gpa)
        # update spreadsheet with video title
        # # if row_count is len(video_URLS):
        # #     break
        time.sleep(5)
    except NoSuchElementException:
        try:
            driver.get("https://www.google.com/")
            search = driver.find_element_by_xpath("//*[@id='tsf']/div[2]/div/div[1]/div/div[1]/input")
            search.send_keys(college + " high school average gpa")     # inputs video url
            search.send_keys(Keys.RETURN)
            hs_gpa = driver.find_element_by_xpath("//*[@id='rso']/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/div/span/span")
            hs_gpa = stripFormat(hs_gpa.text[0:45])
            print(hs_gpa)
            cell_reference = "E" + str(row_count)
            sheet.update_acell(cell_reference, hs_gpa)
            time.sleep(3)
        except NoSuchElementException:
            pass


# Main Function
def format(sheetname):
    print("Active\n")

    # saves spreadsheet being used
    sheet = client.open(sheetname).sheet1

    # creates arrays for video urls and college names
    college_names = getCollegeNames(sheet)
    video_URLS = getVideoURLS(sheet)
    video_categories = getCategories(sheet)
    # video_categories = formatCategories(sheet)

    # # creates array of video titles
    # video_titles = getVideoTitles(sheet)
    #
    # # creates array for file name
    # file_name = getFileName(sheet)



#############FUNCTIONS###################
    row_count=1
    # transcodeVideos(driver,sheet)
    for college in college_names:

        gpa_stats(driver,sheet,row_count,college)

        row_count+=1



format("GPA_Sports_DB")
