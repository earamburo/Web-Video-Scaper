from __future__ import print_function
import csv, time, gspread, os, sys, shutil, httplib2, requests
from oauth2client.service_account import ServiceAccountCredentials
from apiclient import discovery, http
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
from urllib.error import HTTPError
from http.client import RemoteDisconnected
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pytube import YouTube
from pytube.exceptions import VideoUnavailable
from stat import S_ISREG, ST_CTIME, ST_MODE
from pathlib import Path




# chromedriver location

chromedriver = 'C:\\Users\\StudentBridge\\Desktop\\Campus Compare Scrapers\\chromedriver.exe'
driver = webdriver.Chrome(chromedriver)

# use credentials to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "C:\\Users\\StudentBridge\\Desktop\\Campus Compare Scrapers\\Automation-scraper\\client_secret.json", scope)
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
    return str.replace(";", "_").replace(":", "_").replace("-", "_").replace("|", "_").replace("'","_").replace(",", "_").replace("?", "_").replace("-", "_").replace("/", "_").replace("\"", "_").replace("(","").replace(")","").replace("@","_").replace("&","_").replace(".","").replace("!","").replace("#","")


# Function to get all ipeds data
def getIpeds(sheet, college_names):
    row_count = 1

    # goes through every school in the array
    for school in college_names:
        time.sleep(2)
        # searches through every school in ipeds
        f = open(Path(r'C:/Users/StudentBridge/Desktop/Campus Compare Scrapers/Automation-scraper/')/"ipeds_ids.csv")
        ipeds_data = csv.reader(f)

        for ipeds_id in ipeds_data:
            # if ipeds matches update cell
            if ipeds_id[1] == school:
                cell_reference = "C" + str(row_count)
                sheet.update_acell(cell_reference, ipeds_id[0])

        row_count += 1

        f.close()

# title function that loops through URLS
def getPytubeTitle(video_URLS, driver, sheet):
    row_count = 1

    # gets title for every video in sheet
    for x in video_URLS:
        try:
            yt = YouTube(x)
            title = yt.title
            title = stripFormat(title)
        except VideoUnavailable:
            title = "Video Unavailable"
        except KeyError:
            pass
        cell_reference = "D" + str(row_count)
        sheet.update_acell(cell_reference, title)
        row_count += 1


# #
# #   ONLY USE IF getPytubeTitle() IS NOT WORKING
# #
# def getTitleFromYouTube(url, driver, row_count, sheet):
#     driver.get(url)  # goes to video url

#     time.sleep(5)

#     try:
#         elem = driver.find_element_by_tag_name("h1")  # finds video title
#         title = elem.text
#     except NoSuchElementException:
#         try:
#             driver.get(url)
#             time.sleep(5)
#             elem = driver.find_element_by_tag_name("h1")
#             title = elem.text
#         except NoSuchElementException:
#             elem = "No Video Title Found"
#             title =  elem

#     cell_reference = "D" + str(row_count)

#     sheet.update_acell(cell_reference, title)  # update spreadsheet with video title


# # title function that loops through URLS
# def getTitle(video_URLS, driver, sheet):
#     row_count = 1

#     # gets title for every video in sheet
#     for x in video_URLS:
#         getTitleFromYouTube(x, driver, row_count, sheet)
#         row_count += 1




# function to get thumbnails
def getThumb(video_URLS, file_name, college_names, driver):
    for x in video_URLS:
        driver.get("https://youtubethumbnailimage.com/") # goes to  website for downloading thumbnails
        search = driver.find_element_by_class_name("urlinput")
        search.send_keys(x)     # inputs video url
        search.send_keys(Keys.RETURN)
        download = driver.find_element_by_xpath("//*[@id='im']/div[4]/div[2]/form/input")
        download.click()   # downloads url
        

def renameThumbs(file_name, college_names):
    count = 0
    dirPath = Path(r'C:/Users/StudentBridge/Downloads')
    os.chdir(dirPath)
    entries = ((os.stat(files), files) for files in os.listdir(dirPath))
    entries = ((stat[ST_CTIME], files) for stat, files in entries)
    for cdate, files in sorted(entries):
        src = dirPath / files
        dst = dirPath / (file_name[count]+ "___" + college_names[count]  + ".jpg")
        os.rename(src, dst)
        count += 1

# Function to download youtube videos
def downloadVideos(videos_URLS,file_name, college_names):
    count = 0
    # print("test1")
    for url in videos_URLS:
        print(url)
        try:
            yt = YouTube(url)
            video_name = yt.streams.first().download('C:/Users/StudentBridge/Downloads/Videos')
            print("download test")
            print(yt.streams.first().default_filename)
            os.rename(video_name, 'C:/Users/StudentBridge/Downloads/Videos/' + college_names[count] +"___" + file_name[count]+".mp4")
            count +=1
            time.sleep(10)
        except:
            print('Error')
            pass
        # except KeyError:
        #     print('KeyError')
        #     pass
        # except HTTPError:
        #     print('HTTPError')
        #     pass
        # except RemoteDisconnected:
        #     print('RemoteError')
        #     pass
        # except VideoUnavailable:
        #     print('VideoDNEError')
        #     pass
            


# function to transcode url
def transcodeVideos(driver, video_titles):
    wait = WebDriverWait(driver, 200)
    downloaded_Videos = os.listdir(Path('C:/Users/StudentBridge/Downloads/Videos/'))

    # log in to transcoder
    driver.get("https://transcoder.studentbridge.com/admin/")
    email = driver.find_element_by_id("email")
    password = driver.find_element_by_id("password")
    login = driver.find_element_by_tag_name("button")

    email.send_keys("earamburo@studentbridge.com")
    password.send_keys("admin123")
    login.click()

    count = 0

    # uploads videos to transcoder
    for video in downloaded_Videos:
        time.sleep(3)

        if count % 10 == 0:
            time.sleep(10)

        driver.get("https://transcoder.studentbridge.com/admin/")

        # goes to encode video page
        encode_button = driver.find_element_by_link_text('Encode Video')
        encode_button.click()

        # upload video file
        file_upload = driver.find_element_by_id('file_upload')
        file_upload.send_keys("C:\\Users\\StudentBridge\\Downloads\\Videos\\" + video)
        print(video)
        # select campus compare as encoder profile
        attempts = 0
        max_attempts = 5
        while(1 == 1):
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

        count += 1

def transferURLS(video_titles, college_names, driver, sheet):
    # log in to transcoder
    driver.get("https://transcoder.studentbridge.com/admin/")
    email = driver.find_element_by_id("email")
    password = driver.find_element_by_id("password")
    login = driver.find_element_by_tag_name("button")

    email.send_keys("earamburo@studentbridge.com")
    password.send_keys("admin123")
    login.click()


    time.sleep(3) 
    driver.get("https://transcoder.studentbridge.com/admin/admin_jobs_outputs") 
    
    row_count = 1
    count = 0
    
    for title in video_titles:
        try:
            # print(college_names)
            search = driver.find_element_by_name('search')
            search.click()
            title = stripFormat(title)
            # print(college_names[count]+" "+title)
            college_name = college_names[count]
            college_name = stripFormat(college_name)
            print(college_name)
            print(title)
            # search.send_keys(college_name+" "+title)
            search.send_keys(title)
            # search.send_keys(college_names[count] +"_" + title)
            search.send_keys(Keys.RETURN)
            # print(title)
            time.sleep(3)
            url = driver.find_element_by_partial_link_text('http').text
            # url.click()
            
            # print(url)

            cell_reference = "F" + str(row_count)
            sheet.update_acell(cell_reference, url)
            row_count += 1
            count+=1
            print('Updated needs to clear')
            search = driver.find_element_by_name('search')
            search.click() 
            search.clear()
            print('Complete')
        except NoSuchElementException:
            search = driver.find_element_by_name('search')
            search.click() 
            search.clear()
            row_count += 1
            count+=1
            pass    

            

def deleteVideos():
    folder = Path("Downloads/Videos")
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


# Main Function
def automate(sheetname):
    # saves spreadsheet being used
    sheet = client.open(sheetname).sheet1

    # creates arrays for video urls and college names
    video_URLS = getVideoURLS(sheet)
    college_names = getCollegeNames(sheet)

    # gets ipeds data
    #getIpeds(sheet, college_names)

    # gets titles for videos
    #getPytubeTitle(video_URLS, driver, sheet)

    # creates array of video titles
    video_titles = getVideoTitles(sheet)

    # creates array for file name
    file_name = getFileName(sheet)

    # downloads thumbnails from youtube
    # getThumb(video_URLS, file_name, college_names, driver)

    time.sleep(10)

    # renames downloaded thumbnails
    # renameThumbs(file_name, college_names)

    # downloads all videos and saves them in "College Name___ Video Title"
    downloadVideos(video_URLS,file_name, college_names)

    # transcodes every video
    # transcodeVideos(driver, video_titles)

    # deletes videos in downloaded video folders
    #deleteVideos()
    # transferURLS(video_titles,college_names,driver,sheet);
    

automate("Maryland_Videos_Import_Format")