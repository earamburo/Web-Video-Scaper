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
    str = str.replace("-", "_").replace(" ","_")
    return str



def stripDescription(str):
    # print("Strip Format\n")
    str = re.sub('\[.*?\]','', str)
    str = str.rstrip();
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
            description = driver.find_element_by_xpath("//*[@class='mw-parser-output']/p[1]")
            description = stripDescription(description.text)
            # print(description.text+"\n")
            # print(description+"\n")


            # Handling Errors

            if 'to:' in description:
                description = 'CAMPUS ERROR'
            
            elif description == "":
                print('NONE ERROR')
                description = driver.find_element_by_xpath("//*[@class='mw-parser-output']/p[2]")
                description = stripDescription(description.text)
                # print(description)

            elif description == " ":
                print('SPACE ERROR')
                description = driver.find_element_by_xpath("//*[@class='mw-parser-output']/p[2]")
                description = stripDescription(description.text)
                # print(description)

            elif 'Coordinates:' in description:
                
                description = driver.find_element_by_xpath("//*[@class='mw-parser-output']/p[2]")
                # print(description.text)
                description = stripDescription(description.text)
                # print('\nCoordinate ERROR')
                # print (len(description))

            # elif len(description) <= 125:
            #      description = 'SCHOOL NOT FOUND'
            #      # print (len(description))

            print(description)
            cell_reference = "C" + str(row_count)
            sheet.update_acell(cell_reference, description)

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
            sheet.update_acell(cell_reference, "ELEMENT NOT FOUND")
            row_count+=1
            pass

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

def downloadImages(sheet, college_names):
    row_count = 1 
    for college in college_names:
    # college_name = "University of Georgia"
        arguments = {"keywords": college +" campus", 
                     "format": "jpg", 
                     "limit":1, 
                     "print_urls":True, 
                     "size": "large", 
                     "aspect_ratio": "wide",
                     "no_directory": "/Users/admin/Downloads/header_images",
                     "no_numbering": True
                      } 
        try: 
            response.download(arguments) 
          
        # Handling File NotFound Error     
        except FileNotFoundError:  
            arguments = {"keywords": college +" campus", 
                         "format": "jpg", 
                         "limit":1, 
                         "print_urls":True, 
                         "size": "large", 
                         "aspect_ratio": "wide",
                         "no_directory": "/Users/admin/Downloads/header_images",
                         "no_numbering": True
                         } 
                           
            # Providing arguments for the searched query 
            try: 
                # Downloading the photos based 
                # on the given arguments 
                response.download(arguments)  
            except: 
                pass

        for filename in os.listdir("/Users/admin/Desktop/Github-Projects/Web-Video-Scaper/downloads"):
            # print(filename)
            if not filename.startswith('.'):
                print(filename)
                src = '/Users/admin/Desktop/Github-Projects/Web-Video-Scaper/downloads/' + (filename)       
                dst = '/Users/admin/Desktop/Github-Projects/Web-Video-Scaper/images/' +college+".jpg" 
                # # print("Renaming thumbnail")            
                os.rename(src, dst)

                

                time.sleep(5)
                cell_reference = "H" + str(row_count)
                # sheet.update_acell(cell_reference,college+ "-campus.jpg")
                sheet.update_acell(cell_reference,college+".jpg")
                print("RENAMED")
                # print("DESTINATION: " +dst)
                # src = '/Users/admin/Downloads/' + (filename)
                # dst = '/Users/admin/Desktop/Thumbnails/' +college_names[row_count]+video_titles[row_count]+".jpg"
                # os.rename(src, dst)
                time.sleep(5)
                row_count += 1       

def quickFix(sheet, college_names):
    row_count = 1 
    for college in college_names:
        cell_reference = "G" + str(row_count)
        sheet.update_acell(cell_reference,college+".jpg")
        row_count+=1
        time.sleep(5)


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
    getDescription(sheet, college_names)
    # 2
    # downloadImages(sheet, college_names)
    # 3
    # quickFix(sheet, college_names)


automate("Wiki TEST")
