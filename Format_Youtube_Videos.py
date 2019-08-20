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


    return str.lstrip()

# Function to get all ipeds data
def getSchoolID(sheet,college,row_count):
    print("\n")
    print("Getting School ID...")
    # print(college)
    # # goes through every school in the array
    #
    # time.sleep(2)
    #
    #         # ipeds spreadsheet location
    f = open(Path(r'/Users/edwinaramburo/Desktop/Projects/Web-Video-Scaper')/"school_ids.csv")
    school_id_data = csv.reader(f)

    for school_id in school_id_data:
    # if ipeds matches update cell
        if school_id[1] == college:
            print("Found")
            cell_reference = "B" + str(row_count)
            print(row_count)
            sheet.update_acell(cell_reference, school_id[0])
            time.sleep(2)


    f.close()

# Function to get all ipeds data
def getIpeds(sheet, college,row_count):
    print("\n")
    print("Getting IPEDs...")


    # ipeds spreadsheet location
    f = open(Path(r'/Users/edwinaramburo/Desktop/Projects/Web-Video-Scaper')/"ipeds_ids.csv")
    ipeds_data = csv.reader(f)

    for ipeds_id in ipeds_data:
        # if ipeds matches update cell
        if ipeds_id[1] == college:
            print("Found\n")
            cell_reference = "C" + str(row_count)
            sheet.update_acell(cell_reference, ipeds_id[0])
            time.sleep(2)

    row_count += 1

    f.close()

# Gets Title from Youtube
def getTitleFromYouTube(driver, sheet, row_count):
    print("Getting title")
    url = sheet.acell('F'+str(row_count)).value
    # print(url)

    driver.get(url)  # goes to video url

    time.sleep(5)

    try:
        elem = driver.find_element_by_tag_name("h1")  # finds video title
        title = elem.text
        title = stripFormat(title)
        print(title)
    except NoSuchElementException:
        try:
            driver.get(url)
            time.sleep(5)
            elem = driver.find_element_by_tag_name("h1")
            title = elem.text
        except NoSuchElementException:
            elem = "No Video Title Found"
            title =  elem
    cell_reference = "D" + str(row_count)
    sheet.update_acell(cell_reference, title)  # update spreadsheet with video title
    # if row_count is len(video_URLS):
    #     break
    time.sleep(5)

# Will get Youtube Thumbnails
def getThumb(driver, sheet,row_count):
    url = sheet.acell('F'+str(row_count)).value
    # print(url)
    print("Downloading Thumbnails\n")
    # count = 0
    # row_count=1
    # for x in video_URLS:
    driver.get("https://youtubethumbnailimage.com/") # goes to  website for downloading thumbnails
    search = driver.find_element_by_class_name("urlinput")
    search.send_keys(url)     # inputs video url
    search.send_keys(Keys.RETURN)
    download = driver.find_element_by_xpath("//*[@id='im']/div[4]/div[2]/form/input")
    download.click()   # downloads url
    time.sleep(5)

    # # downloads folder
    for filename in os.listdir("/Users/edwinaramburo/Downloads/"):

        if filename ==".DS_Store": # Handles the first hidden file in the folder
            print("1111-DS_Store file encountered\n")
            pass
        else:
            print(filename)

            # uses the os.stat functions for file sizing
            file = os.stat("/Users/edwinaramburo/Downloads/" + filename)


            if(file.st_size) == 0:
                os.unlink("/Users/edwinaramburo/Downloads/" + filename) #deletes files
                print('EMPTY THUMBNAIL ERROR') #notifies me of error

    #             ###### Updates the spreadsheet with the error ########
    #             # cell_reference = "I" + str(row_count)
    #             # sheet.update_acell(cell_reference, 'THUMBNAIL ERROR')
    #             ########################################################
    #
                download = driver.find_element_by_xpath("//*[@id='im']/div[1]/div[2]/form/input")
                download.click()   # downloads url
                time.sleep(5)

                for filename in os.listdir("/Users/edwinaramburo/Downloads/"):

                    if filename == ".DS_Store":
                        print("2222-DS_Store file encountered\n")
                        pass

                    else:
                        src = '/Users/edwinaramburo/Downloads/' + (filename)
                        dst = '/Users/edwinaramburo/Desktop/Thumbnails/' + (filename)
                        # print("Renaming thumbnail")
                        os.rename(src, dst)
    # #
    # #
            else:
                if filename ==".DS_Store":
                    print("3333-DS_Store file encountered\n")
                    pass
                else:
                    src = '/Users/edwinaramburo/Downloads/' + (filename)
                    dst = '/Users/edwinaramburo/Desktop/Thumbnails/' + (filename)
                    # print("Renaming thumbnail")

                    # This will rename the downloaded thumbnail
                    os.rename(src, dst)

            time.sleep(5)
            cell_reference = "I" + str(row_count)
            sheet.update_acell(cell_reference, filename)

def downloadVideos(driver,sheet,row_count):
    print("Downloading Videos\n")
    # count = 0
    # row_count= 0
    # cell_count = 1
    #
    # name_counter = 1250

    url = sheet.acell('F'+str(row_count)).value
    college_name = sheet.acell('A'+str(row_count)).value
    category= sheet.acell('E'+str(row_count)).value


    state = 'TEST'

    # os.mkdir('/Users/admin/Downloads/Videos')
    # print("test1")
    ydl_opts = {
        'outtmpl' :'/Users/edwinaramburo/Downloads/Videos/%(title)s.%(ext)s'
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:

        print(url + " downloading\n")
        ydl.download([url])
        time.sleep(13)
        print("\n")
        for filename in os.listdir("/Users/edwinaramburo/Downloads/Videos/"):
            print(filename+"\n")
            if filename ==".DS_Store":
                print("SKIPPED")
            else:
                # print("ELSE")
                src = '/Users/edwinaramburo/Downloads/Videos/' + (filename)
                print("SOURCE: "+ src)
                ########REMEMBER TO CHANGE STATE NAME########
                dst = '/Users/edwinaramburo/Desktop/Videos/'+ str(row_count) +"_" +college_name+ "_" + category +"_"+ (filename)
                # print(college_names[row_count]+"\n")
                print('DESTINATION: '+ dst+"\n")
                os.rename(src,dst)
                # cell_reference = "K" + str(cell_count)
                # sheet.update_acell(cell_reference, stripFormat(filename))
                # cell_count+=1
                print("RENAMED\n")
                # row_count+=1
                time.sleep(3)

# function to transcode url
def transcodeVideos(driver, sheet):
    print("Transcoding Videos\n")
    # count = 1

    # for filename in os.listdir("/Users/admin/Desktop/Renamed/"):
    #     print(filename[count])
    #     count+=1
    wait = WebDriverWait(driver, 200)
    downloaded_Videos = os.listdir("/Users/edwinaramburo/Desktop/Videos/")

#######TESTING PURPOSES######
    # for filename in downloaded_Videos:
    #     print(filename)
###############################
    # log in to transcoder
    driver.get("https://transcoder.studentbridge.com/admin/")
    email = driver.find_element_by_id("email")
    password = driver.find_element_by_id("password")
    login = driver.find_element_by_tag_name("button")
    #
    email.send_keys("earamburo@studentbridge.com")
    password.send_keys("admin123")
    login.click()

    # count = 0

    # uploads videos to transcoder
    for filename in downloaded_Videos:
        print(filename)
        if filename ==".DS_Store":
            print("DS_STORE FILE SKIPPED")
        else:
            print(filename)
            time.sleep(3)

            # if count % 10 == 0:
            #     time.sleep(10)

            # driver.get("https://transcoder.studentbridge.com/admin/")

            # goes to encode video page
            encode_button = driver.find_element_by_link_text('Encode Video')
            encode_button.click()

            # upload video file
            file_upload = driver.find_element_by_id('file_upload')
            # print("Here")
            file_upload.send_keys("/Users/edwinaramburo/Desktop/Videos/" + filename)

            # print(video)
            # select campus compare as encoder profile
            attempts = 0
            max_attempts = 5
            while(1 == 1):
                time.sleep(3)
                try:
                    el = driver.find_element(By.XPATH, '//*[@id="s2id_encoder_profile"]')
                    el.click()
                    option = driver.find_element(By.XPATH, '//*[@id="s2id_autogen1_search"]')
                    option.send_keys("campus compare")
                    option.send_keys(Keys.RETURN)
                    break
                except ElementNotVisibleException:
                    if(attempts == max_attempts):
                        print("Could not transcode " + video)
                    else:
                        attempts +=1
                        pass

            # Submit
            sub = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='submit']")))
            sub.click()
            os.rename("/edwinaramburo/Desktop/Videos/" + filename,"/Users/edwinaramburo/Desktop/Videos/Done/" + filename)
            # count += 1

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
        # print(college)
        #1 match school ids
        getSchoolID(sheet,college,row_count)

        #2 Uses spread sheet to acquire all iped ids
        getIpeds(sheet, college,row_count)

        #3 -> This has a limitation on calls, used for errors that happen in the pytube api
        getTitleFromYouTube(driver, sheet,row_count)


        #4 Downloads videos
        downloadVideos(driver,sheet,row_count)



        # 5
        # transcodeVideos(driver,sheet)


        #5 -> downloads, renames and transfer thumbnails from youtube to spreadsheet
        # getThumb(driver, sheet,row_count)


        #6 -> downloads, renames and transfer thumbnails from youtube to spreadsheet
        # getThumb(video_URLS,video_titles, file_name, college_names, driver, sheet)

        #7
        # time.sleep(10)

        #8 -> downloads all videos and saves them in "College Name___ Video Title"
        # downloadVideos(video_URLS,college_names,sheet)


        #9 -> downloads all videos and saves them in "College Name___ Video Title"
        # downloadVideos(video_URLS,college_names,sheet)


        #10 -> transcodes every video
        # transcodeVideos(driver, video_titles)

        #11-> transfer transcoded urls to spreadsheet
        # transferURLS(video_titles,college_names,driver,sheet);

        #12 -> deletes videos in downloaded video folders
        #deleteVideos()

        row_count+=1

        #4 -> format categories
        # formatCategories(sheet)


format("Specific imports")
