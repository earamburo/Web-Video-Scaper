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


def gpa_stats(driver, sheet, row_count, college):

    print("GPA stats")
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
            time.sleep(1)
            # hs_gpa = driver.find_element_by_xpath("//*[@id='rso']/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/div/span/span")
            # PREP SCHOLAR
            # hs_gpa = driver.find_element_by_xpath("//*[@id='rso']/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/div/span/span")
            # COLLEGE SIMPLY
            # hs_gpa = driver.find_element_by_xpath("//*[@id='rso']/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/div/span/span")
            # MAGOOSH
            hs_gpa = driver.find_element_by_xpath("//*[@id='rso']/div[1]/div/div[1]/div/div[1]/div[2]/div[2]/div/span[1]/span")
            # THOUGHTCO
            # hs_gpa = driver.find_element_by_xpath("//*[@id='rso']/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/div/span/span")

            ##################################
            hs_gpa = stripFormat(hs_gpa.text)
            print(hs_gpa)
            cell_reference = "E" + str(row_count)
            sheet.update_acell(cell_reference, hs_gpa)
            time.sleep(3)
        except NoSuchElementException:
            pass

def sport_stats(driver, sheet, row_count, college):

    print("\nGetting Sport stats...\n")
    if row_count == 1:
        driver.get("https://secure.princetonreview.com/account/signin")

        username = driver.find_element_by_xpath("//*[@id='Username']")
        username.click()
        username.send_keys("earamburo@studentbridge.com")

        username = driver.find_element_by_xpath("//*[@id='Password']")
        username.click()
        username.send_keys("Colombia17$")

        sign_in = driver.find_element_by_xpath("//*[@id='registrationContainer']/div[2]/input")
        sign_in.click()
        time.sleep(2)

        driver.execute_script("window.open('');")



            # search_bar = driver.find_element_by_xpath("//*[@id='siteSearchHref']")
            # search_bar.click()

        # search_results = driver.find_element_by_xpath("//*[@id='siteSearchText2']")
        # search_results.click()
        # search_results.send_keys("American University")


    driver.switch_to.window(driver.window_handles[0])
    driver.get("https://www.princetonreview.com/college-search/?majors=14.3501&page=2")
    search = driver.find_element_by_class_name("tt-input")
    search.send_keys(college)     # inputs video url
    search.send_keys(Keys.RETURN)
    time.sleep(2)

    url = driver.current_url

    if '?search' in url:
        VIEW_SCHOOL = driver.find_element_by_xpath("//*[@id='filtersForm']/div[2]/div[3]/div[2]/div[1]/div[2]/a")
        VIEW_SCHOOL.click()
        new_url = driver.current_url+"#!campuslife"
        driver.switch_to.window(driver.window_handles[1])
        driver.get(new_url)
        time.sleep(2)

    else:
        url = url+"#!campuslife"
        driver.switch_to.window(driver.window_handles[1])
        driver.get(url)
        time.sleep(2)

        print(college+"\n")


    try:
        print("TEST 1 INITIALIZED")
        DIVISION_SPORTS_CLASS = driver.find_element_by_xpath("//*[@id='campuslife']/div[8]/div[2]/div[1]/div[2]/div")
        print(DIVISION_SPORTS_CLASS.text)
        DIVISION_SPORTS_CLASS = DIVISION_SPORTS_CLASS.text
        cell_reference = "F" + str(row_count)
        sheet.update_acell(cell_reference, DIVISION_SPORTS_CLASS)
        print("TEST 1: DIVISION FOUND")

        MALE_SPORTS = driver.find_element_by_xpath("//*[@id='campuslife']/div[8]/div[2]/div[4]/div[1]/div[3]")
        print(MALE_SPORTS.text)
        MALE_SPORTS = MALE_SPORTS.text
        cell_reference = "G" + str(row_count)
        sheet.update_acell(cell_reference, MALE_SPORTS)
        print("TEST 1: MALE SPORTS FOUND")
        time.sleep(2)

        FEMALE_SPORTS = driver.find_element_by_xpath("//*[@id='campuslife']/div[8]/div[2]/div[4]/div[2]/div[3]")
        print(FEMALE_SPORTS.text)
        FEMALE_SPORTS = FEMALE_SPORTS.text
        cell_reference = "H" + str(row_count)
        sheet.update_acell(cell_reference, FEMALE_SPORTS)
        print("TEST 1: FEMALE SPORTS FOUND")
        time.sleep(2)



    except NoSuchElementException:
            print("\n")
            print("TEST 2 INITIALIZED\n")
            try:
                time.sleep(3)
                DIVISION_SPORTS_CLASS = driver.find_element_by_xpath("//*[@id='campuslife']/div[7]/div[2]/div[1]/div[2]/div")
                print(DIVISION_SPORTS_CLASS.text)
                DIVISION_SPORTS_CLASS = DIVISION_SPORTS_CLASS.text
                cell_reference = "F" + str(row_count)
                sheet.update_acell(cell_reference, DIVISION_SPORTS_CLASS)
                print("TEST 2: DIVISION FOUND")


                MALE_SPORTS = driver.find_element_by_xpath("//*[@id='campuslife']/div[7]/div[2]/div[4]/div[1]/div[3]")
                print(MALE_SPORTS.text)
                MALE_SPORTS = MALE_SPORTS.text
                cell_reference = "G" + str(row_count)
                sheet.update_acell(cell_reference, MALE_SPORTS)
                print("TEST 2: MALE SPORTS FOUND")
                time.sleep(2)

                FEMALE_SPORTS = driver.find_element_by_xpath("//*[@id='campuslife']/div[7]/div[2]/div[4]/div[2]/div[3]")
                print(FEMALE_SPORTS.text)
                FEMALE_SPORTS = FEMALE_SPORTS.text
                cell_reference = "H" + str(row_count)
                sheet.update_acell(cell_reference, FEMALE_SPORTS)
                print("TEST 2: FEMALE SPORTS FOUND")
                time.sleep(2)
            except NoSuchElementException:
                print("\n")
                print("TEST 3 INITIALIZED\n")
                try:
                    time.sleep(3)
                    DIVISION_SPORTS_CLASS = driver.find_element_by_xpath("//*[@id='campuslife']/div[8]/div[2]/div[1]/div[2]/div")
                    print(DIVISION_SPORTS_CLASS.text)
                    DIVISION_SPORTS_CLASS = DIVISION_SPORTS_CLASS.text
                    cell_reference = "F" + str(row_count)
                    sheet.update_acell(cell_reference, DIVISION_SPORTS_CLASS)
                    print("TEST 3: DIVISION FOUND")


                    MALE_SPORTS = driver.find_element_by_xpath("//*[@id='campuslife']/div[8]/div[2]/div[3]/div[1]/div[3]")
                    print(MALE_SPORTS.text)
                    MALE_SPORTS = MALE_SPORTS.text
                    cell_reference = "G" + str(row_count)
                    sheet.update_acell(cell_reference, MALE_SPORTS)
                    print("TEST 3: MALE SPORTS FOUND")
                    time.sleep(2)

                    FEMALE_SPORTS = driver.find_element_by_xpath("//*[@id='campuslife']/div[8]/div[2]/div[3]/div[2]/div[3]")
                    print(FEMALE_SPORTS.text)
                    FEMALE_SPORTS = FEMALE_SPORTS.text
                    cell_reference = "H" + str(row_count)
                    sheet.update_acell(cell_reference, FEMALE_SPORTS)
                    print("TEST 3: FEMALE SPORTS FOUND")
                    time.sleep(2)

                except NoSuchElementException:
                    print("\nTEST 4 INITIALIZED\n")

                    try:
                        time.sleep(3)
                        DIVISION_SPORTS_CLASS = driver.find_element_by_xpath("    //*[@id='campuslife']/div[7]/div[2]/div[1]/div[2]/div")
                        print(DIVISION_SPORTS_CLASS.text)
                        DIVISION_SPORTS_CLASS = DIVISION_SPORTS_CLASS.text
                        cell_reference = "F" + str(row_count)
                        sheet.update_acell(cell_reference, DIVISION_SPORTS_CLASS)
                        print("TEST 4: DIVISION FOUND")


                        MALE_SPORTS = driver.find_element_by_xpath("//*[@id='campuslife']/div[7]/div[2]/div[3]/div[1]/div[3]")
                        print(MALE_SPORTS.text)
                        MALE_SPORTS = MALE_SPORTS.text
                        cell_reference = "G" + str(row_count)
                        sheet.update_acell(cell_reference, MALE_SPORTS)
                        print("TEST 4: MALE SPORTS FOUND")
                        time.sleep(2)

                        FEMALE_SPORTS = driver.find_element_by_xpath("//*[@id='campuslife']/div[7]/div[2]/div[3]/div[2]/div[3]")
                        print(FEMALE_SPORTS.text)
                        FEMALE_SPORTS = FEMALE_SPORTS.text
                        cell_reference = "H" + str(row_count)
                        sheet.update_acell(cell_reference, FEMALE_SPORTS)
                        print("TEST 4: FEMALE SPORTS FOUND")
                        time.sleep(2)

                    except NoSuchElementException:
                        print("\nTEST 5 INITIALIZED\n")

                        try:
                            time.sleep(3)
                            DIVISION_SPORTS_CLASS = driver.find_element_by_xpath("//*[@id='campuslife']/div[8]/div[2]/div[1]/div[2]/div")
                            print(DIVISION_SPORTS_CLASS.text)
                            DIVISION_SPORTS_CLASS = DIVISION_SPORTS_CLASS.text
                            cell_reference = "F" + str(row_count)
                            sheet.update_acell(cell_reference, DIVISION_SPORTS_CLASS)
                            print("TEST 5: DIVISION FOUND")


                            MALE_SPORTS = driver.find_element_by_xpath("//*[@id='campuslife']/div[8]/div[2]/div[2]/div[1]/div[3]")
                            print(MALE_SPORTS.text)
                            MALE_SPORTS = MALE_SPORTS.text
                            cell_reference = "G" + str(row_count)
                            sheet.update_acell(cell_reference, MALE_SPORTS)
                            print("TEST 5: MALE SPORTS FOUND")
                            time.sleep(2)

                            FEMALE_SPORTS = driver.find_element_by_xpath("//*[@id='campuslife']/div[8]/div[2]/div[2]/div[2]/div[3]")
                            print(FEMALE_SPORTS.text)
                            FEMALE_SPORTS = FEMALE_SPORTS.text
                            cell_reference = "H" + str(row_count)
                            sheet.update_acell(cell_reference, FEMALE_SPORTS)
                            print("TEST 5: FEMALE SPORTS FOUND")
                            time.sleep(2)
                        except NoSuchElementException:
                            if 'Other' in DIVISION_SPORTS_CLASS:
                                print("DNE")
                                pass

            # except NoSuchElementException:
            #     print("TEST 3 INITIALIZED\n")
            #     try:
            #         if not 'Division' in DIVISION_SPORTS_CLASS:
            #             print("DIVISION NOT FOUND\n")
            #             time.sleep(3)
            #             DIVISION_SPORTS_CLASS = driver.find_element_by_xpath("//*[@id='campuslife']/div[7]/div[2]/div[1]/div[2]/div")
            #             print(DIVISION_SPORTS_CLASS.text)
            #             DIVISION_SPORTS_CLASS = DIVISION_SPORTS_CLASS.text
            #
            #         MALE_SPORTS = driver.find_element_by_xpath("//*[@id='campuslife']/div[7]/div[2]/div[4]/div[1]/div[3]")
            #         print(MALE_SPORTS.text)
            #         MALE_SPORTS = MALE_SPORTS.text
            #         cell_reference = "G" + str(row_count)
            #         sheet.update_acell(cell_reference, MALE_SPORTS)
            #         time.sleep(2)
            #
            #         FEMALE_SPORTS = driver.find_element_by_xpath("//*[@id='campuslife']/div[7]/div[2]/div[4]/div[2]/div[3]")
            #         print(FEMALE_SPORTS.text)
            #         FEMALE_SPORTS = FEMALE_SPORTS.text
            #         cell_reference = "H" + str(row_count)
            #         sheet.update_acell(cell_reference, FEMALE_SPORTS)
            #         time.sleep(2)



        # if not 'Division' in DIVISION_SPORTS_CLASS:
        #     print('ERROR-Student Activity')
        #     DIVISION_SPORTS_CLASS = driver.find_element_by_xpath("//*[@id='campuslife']/div[8]/div[2]/div[1]/div[2]/div")
        #     print(DIVISION_SPORTS_CLASS.text)
        #     DIVISION_SPORTS_CLASS = DIVISION_SPORTS_CLASS.text
        #     time.sleep(2)
        #
        #     MALE_SPORTS = driver.find_element_by_xpath("//*[@id='campuslife']/div[8]/div[2]/div[4]/div[1]/div[3]")
        #     print(MALE_SPORTS.text)
        #     MALE_SPORTS = MALE_SPORTS.text
        #     cell_reference = "G" + str(row_count)
        #     sheet.update_acell(cell_reference, MALE_SPORTS)
        #     time.sleep(2)
        #
        #
        #     FEMALE_SPORTS = driver.find_element_by_xpath("//*[@id='campuslife']/div[8]/div[2]/div[4]/div[2]/div[3]")
        #     print(FEMALE_SPORTS.text)
        #     FEMALE_SPORTS = FEMALE_SPORTS.text
        #     cell_reference = "H" + str(row_count)
        #     sheet.update_acell(cell_reference, FEMALE_SPORTS)
        #     time.sleep(2)



    # cell_reference = "F" + str(row_count)
    # sheet.update_acell(cell_reference, DIVISION_SPORTS_CLASS)
    # time.sleep(2)



    # driver.execute_script("window.close('');")

    #
    # MALE_SPORTS = driver.find_element_by_xpath("//*[@id='campuslife']/div[7]/div[2]/div[2]/div[1]/div[3]")
    # print(MALE_SPORTS.text)
    # MALE_SPORTS = MALE_SPORTS.text
    # cell_reference = "G" + str(row_count)
    # sheet.update_acell(cell_reference, MALE_SPORTS)
    # time.sleep(2)
    #
    #
    # FEMALE_SPORTS = driver.find_element_by_xpath("//*[@id='campuslife']/div[7]/div[2]/div[2]/div[2]/div[3]")
    # print(FEMALE_SPORTS.text)
    # FEMALE_SPORTS = FEMALE_SPORTS.text
    # cell_reference = "H" + str(row_count)
    # sheet.update_acell(cell_reference, FEMALE_SPORTS)
    # time.sleep(2)



    driver.switch_to.window(driver.window_handles[0])




    # driver.get(url)





    # cell_reference = "E" + str(row_count)
    # sheet.update_acell(cell_reference, hs_gpa)
    # update spreadsheet with video title
    # # if row_count is len(video_URLS):
    # #     break
    # time.sleep(5)


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

    # college = "American University"
    # transcodeVideos(driver,sheet)
    for college in college_names:

        # gpa_stats(driver,sheet,row_count,college)
        sport_stats(driver, sheet, row_count, college)

        row_count+=1



format("GPA_Sports_DB")
