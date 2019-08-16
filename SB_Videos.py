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

from google_images_download import google_images_download

import PIL
from PIL import Image

# chromedriver location

chromedriver = '/Users/admin/Desktop/Github-Projects/Web-Video-Scaper/chromedriver'

driver = webdriver.Chrome(chromedriver)

# use credentials to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "/Users/admin/Desktop/Github-Projects/Web-Video-Scaper/credentials.json", scope)
client = gspread.authorize(creds)

# Needed Google images download
response = google_images_download.googleimagesdownload()

driver.set_page_load_timeout(15)
driver.maximize_window()


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

def getResultURLS(sheet):
    RURLArr = sheet.col_values(6)
    return RURLArr

# Creates array of Video URLs
def getVideoURLS(sheet):
    URLArr = sheet.col_values(6)
    return URLArr



def formatURLs(sheet, result_urls):
    row_count = 1
    for result in result_urls:
        # strips URL of all <>
        result = re.sub('\<.*?\>','', result)
        cell_reference = "F" + str(row_count)
        sheet.update_acell(cell_reference,result)
        row_count+=1
        time.sleep(3)

# function to remove all college name formatting
def stripCollegeName(str):
    str = str.replace("_", " ").title()
    return str

def stripTitle(str):
    str = str.replace(".mp4","").replace("_"," ").replace("1","").replace("1 ","").replace("2","").replace("2 ","").replace("3","").replace("3 ","").replace("4","").replace("4 ","")\
    .replace("5","").replace("5 ","").replace("6","").replace("6 ","").replace("7","").replace("7 ","").replace("8","").replace("8 ","")\
    .replace("9","").replace("9 ","").replace("0","").replace("0 ","").replace("etc","").replace("-"," ").replace("  ","").replace("   "," ").replace(".-","").replace(".","").strip().title()
    return str

def formatCollege(str):
    str = str.replace("_", " ").replace("south carolina law","University of South Carolina School of Law").replace("carthage","Carthage College").replace("florida southwestern","Florida Southwestern State College")\
    .replace("uf warrington mba","University of Florida").replace("uw stevens point","University of Wisconsin - Stevens Point").replace("grand valley state university","Grand Valley State University")
    return str


def getSchoolName(sheet, result_urls):
    row_count = 1
    for url in result_urls:
        url = url.split("/")
        school_name = url[3]
        school_name = formatCollege(school_name)
        print(school_name)
        cell_reference = "A" + str(row_count)
        sheet.update_acell(cell_reference,school_name)
        row_count+=1
        time.sleep(3)

def getTitle(sheet, result_urls):
    row_count = 1
    for url in result_urls:
        url = url.split("/")
        video_title = url[4]
        print(video_title)
        video_title = stripTitle(video_title)
        print(video_title+"\n")
        cell_reference = "D" + str(row_count)
        sheet.update_acell(cell_reference,video_title)
        row_count+=1
        time.sleep(3)


def getCategory(sheet,video_titles):
    row_count = 1
    for title in video_titles:
        if "Academics" or "academics" in title:
            print(title)
            cell_reference = "E" + str(row_count)
            sheet.update_acell(cell_reference,"Academics")
            time.sleep(5)
        row_count+=1
def formatTitle(sheet):
    print("Formatting Titles\n")
    row_count=1
    titles = sheet.col_values(4)
    for title in titles:

        title = str.strip(title).lower().title()
        print(title)

        cell_reference = "D" + str(row_count)
        # print(cell_reference)
        sheet.update_acell(cell_reference,title)
        time.sleep(3)
        row_count+=1
        # print("MATCH")
        # print("End")

    print("Format Titles complete")


def getScreenshot(sheet, video_URLS,college_names):
    array_count=0
    row_count=598
    screenshot_count=598
    for url in video_URLS:
        print(url)
        f = open('Test.html','w')
        message ="""<!DOCTYPE html>
        <html>
        <body>
        <video width="800" height="720" muted autoplay controls>
          <source src="""+url+""" type="video/mp4">
          Your browser does not support the video tag.
        </video>

        </body>
        </html>
        """
        f.write(message)
        f.close()
        file ='/Users/admin/Desktop/Github-Projects/Web-Video-Scaper/Test.html'
        filename = 'file://'+file
        driver.get(filename)
        time.sleep(7)

        # Takes screenshot
        print("Taking screenshot")
        element = driver.find_element_by_xpath("//video");
        location = element.location;
        size = element.size;
        print(size)
        # print(location)
        name = college_names[array_count]+str(screenshot_count)+'.png'
        driver.save_screenshot('/Users/admin/Downloads/'+name);
        x = location['x'];
        print(x)
        y = location['y'];
        #Cropping
        print("Cropping Image")
        im = Image.open('/Users/admin/Downloads/'+name)
        im = im.crop((20, 150, 700, 550))
        im.save('/Users/admin/Downloads/'+name)
        time.sleep(3)
        #
        # for filename in os.listdir("/Users/edwinaramburo/Downloads/"):
        #
        #     src = '/Users/edwinaramburo/Downloads/' + (filename)
        #     # dst = '/Users/admin/Desktop/Thumbnails/'+ college_names[count] +"___"+ video_titles[count]+".jpg"
        #     dst = '/Users/edwinaramburo//SB_Thumbnails/' + (filename)
        #
        #     if filename =="'/Users/edwinaramburo/Downloads/.DS_Store":
        #         print("pass")
        #         pass
        #     # print("Renaming thumbnail")
        #     os.rename(src, dst)
        #     # if filename ==".DS_Store":
        #     #     pass
        #     time.sleep(5)
        #     cell_reference = "I" + str(row_count)
        #     sheet.update_acell(cell_reference, filename)
        #     print("FILENAME: "+filename)
        #     # print("DESTINATION: " +dst)
        #     # src = '/Users/admin/Downloads/' + (filename)
        #     # dst = '/Users/admin/Desktop/Thumbnails/' +college_names[row_count]+video_titles[row_count]+".jpg"
        #     # os.rename(src, dst)
        #     time.sleep(5)




        screenshot_count+=1
        array_count+=1
        row_count+=1


# Main Function
def automate(sheetname):
    print("Active\n")

    # saves spreadsheet being used
    sheet = client.open(sheetname).sheet1

    descriptions = getVideoDescriptions(sheet)
    # print(descriptions)

    # creates arrays for video urls and college names
    video_URLS = getVideoURLS(sheet)
    college_names = getCollegeNames(sheet)
    # print(college_names)
    result_urls = getResultURLS(sheet)

    # creates array of video titles
    video_titles = getVideoTitles(sheet)

    # creates array of video categories
    # video_categories = formatCategories(sheet)

    # creates array for file name
    # file_name = getFileName(sheet)



#############FUNCTIONS#####################

    # formatURLs(sheet, result_urls)
    # getSchoolName(sheet, result_urls)
    # getTitle(sheet,result_urls)
    # getCategory(sheet, video_titles)
    getScreenshot(sheet,video_URLS,college_names)
    # formatTitle(sheet)

automate("Python Testing")
