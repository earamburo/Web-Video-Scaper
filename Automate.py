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




# chromedriver location

chromedriver = '/Users/admin/Desktop/Web-Scraper/chromedriver'
driver = webdriver.Chrome(chromedriver)

# use credentials to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "/Users/admin/Desktop/Web-Scraper/client_secret.json", scope)
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
    .replace("+","").replace("[","").replace("]","").replace("@","")
    return str.lstrip()


# Function to get all ipeds data
def getIpeds(sheet, college_names):
    print("Getting IPEDs...\n")
    row_count = 1

    # goes through every school in the array
    for school in college_names:
        time.sleep(2)
        # searches through every school in ipeds
        f = open(Path(r'/Users/admin/Desktop/Web-Scraper')/"ipeds_ids.csv")
        ipeds_data = csv.reader(f)

        for ipeds_id in ipeds_data:
            # if ipeds matches update cell
            if ipeds_id[1] == school:
                print("Found")
                cell_reference = "C" + str(row_count)
                sheet.update_acell(cell_reference, ipeds_id[0])

        row_count += 1

        f.close()

def getTitleFromYouTube(video_URLS, driver, sheet):
     print("Getting titles")
     row_count = 1
     for x in video_URLS:    
        driver.get(x)  # goes to video url

        time.sleep(5)

        try:
            elem = driver.find_element_by_tag_name("h1")  # finds video title
            title = elem.text
            title = stripFormat(title)
            print(title)
        except NoSuchElementException:
            try:
                driver.get(x)
                time.sleep(5)
                elem = driver.find_element_by_tag_name("h1")
                title = elem.text
               
            except NoSuchElementException:
                elem = "No Video Title Found"
                title =  elem
        if row_count is len(video_URLS):
            break
        cell_reference = "D" + str(row_count)
        sheet.update_acell(cell_reference, title)  # update spreadsheet with video title
        time.sleep(5)
        row_count += 1

def formatCategories(sheet):
    row_count=1
    categories = sheet.col_values(5)
    for category in categories:
        category = str.strip(category)
        if category in ['Admissions', 'Academics', 'About', 'Athletics', 'Student Life', 'Discover', 'Campus', 'Alumni']:
            # print("Checking categories")
            cell_reference = "E" + str(row_count)
            # print(cell_reference)
            sheet.update_acell(cell_reference,category)
            time.sleep(3)
            row_count+=1
            # print("MATCH")
        # print("End")
        else:
            sheet.update_acell("J"+str(row_count),'SPELLCHECK')
            row_count+=1
            print("No Match")
    print("FINISHED AUDITING CATEGORIES")        





def getThumb(video_URLS,video_titles, file_name, college_names, driver, sheet):
    print("Downloading Thumbnails\n")
    count = 0
    row_count=1
    for x in video_URLS:
        driver.get("https://youtubethumbnailimage.com/") # goes to  website for downloading thumbnails
        search = driver.find_element_by_class_name("urlinput")
        search.send_keys(x)     # inputs video url
        search.send_keys(Keys.RETURN)
        download = driver.find_element_by_xpath("//*[@id='im']/div[4]/div[2]/form/input")
        download.click()   # downloads url
        time.sleep(5)
        # print("Downloaded thumbnail\n")

        # This will rename the downloaded thumbnail
        for filename in os.listdir("/Users/admin/Downloads/"):
            if filename ==".DS_Store":
                pass
            src = '/Users/admin/Downloads/' + (filename)
            # dst = '/Users/admin/Desktop/Thumbnails/'+ college_names[count] +"___"+ video_titles[count]+".jpg"
            dst = '/Users/admin/Desktop/Thumbnails/' + (filename)
            # print("Renaming thumbnail") 
            os.rename(src, dst)
            if filename ==".DS_Store":
                pass
            time.sleep(5)
            cell_reference = "I" + str(row_count)
            sheet.update_acell(cell_reference, filename)
            print("FILENAME: "+filename)
            # print("DESTINATION: " +dst)
            # src = '/Users/admin/Downloads/' + (filename)
            # dst = '/Users/admin/Desktop/Thumbnails/' +college_names[row_count]+video_titles[row_count]+".jpg"
            # os.rename(src, dst)
            time.sleep(5)
            row_count += 1


        # dirPath = Path(r'/Users/admin/Downloads/')
        # os.chdir(dirPath)
        # entries = ((os.stat(files), files) for files in os.listdir(dirPath))
        # entries = ((stat[ST_CTIME], files) for stat, files in entries)
        # for cdate, files in sorted(entries):
        #     src = dirPath / files
        #     name = video_titles[count]+ "___" + college_names[count]  + ".jpg"
        #     dst = dirPath / ('/Users/admin/Desktop/Thumbnails/' + name)
        #     os.rename(src, dst)
        #     time.sleep(5)
        #     count += 1
        #     # this will transfer the new thumbnail name to the spreadsheet
        #     print("transferring thumbnail " + name)
        #     cell_reference = "I" + str(row_count)
        #     sheet.update_acell(cell_reference, name)
        #     row_count += 1
        # print(dst)    
    #         print("Done")
    #     except UnexpectedAlertPresentException:
    #         print("Hello")
    #         alert.accept()
    #         pass
    # # We need to handle the url invalid alert
    #     except NoAlertPresentException as e: 
    #         print("no alert")        
    #     except:
    #         print("IE: Done renaming") 
    #         pass

def downloadVideos(videos_URLS, college_names,sheet):
    print("Downloading Videos\n")
    count = 0
    row_count= 0
    name_counter = 3

    # os.mkdir('/Users/admin/Downloads/Videos')
    # print("test1")
    ydl_opts = {
        'outtmpl' :'/Users/admin/Downloads/Videos/%(title)s.%(ext)s'
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        for url in videos_URLS:
            print(url + " dowloading\n")
            ydl.download([url])
            time.sleep(3)
            print("\n")
            for filename in os.listdir("/Users/admin/Downloads/Videos/"):
                print(filename+"\n")
                if filename ==".DS_Store":
                    print("SKIPPED")
                else:
                    print("ELSE")
                    src = '/Users/admin/Downloads/Videos/' + (filename)
                    print("SOURCE: "+ src)
                    ########REMEMBER TO CHANGE STATE NAME########
                    dst = '/Users/admin/Desktop/Videos/DE__'+ str(name_counter) +"___" + college_names[row_count] +"___" + (filename)
                    # print(college_names[row_count]+"\n")
                    print('DESTINATION: '+ dst+"\n")
                    os.rename(src,dst)

                    print("RENAMED\n")
                    row_count=+1
                    time.sleep(3)
            name_counter+=1     
            print(name_counter)           
                # time.sleep(5)
            # os.rename(src,dst)    
            # print("Renamed\n")
            # count=+1
            # row_count=+1


            # ydl.extract_info([url])
           

    # print('Title of the extracted video/playlist: %s' % info['title'])
            # video_name = ydl.streams.first().download('/Users/admin/Downloads/Videos')
            # print(ydl_opts)

    # for url in videos_URLS:
    #     print(url)
    #     YoutubeDL.download(url)
        # yt = YouTube(url)
        # print(yt)
        # video_name = yt.streams.first().download('/Users/admin/Downloads/Videos')
        # new_name = yt.title +" "+ str(count)
        # print("download test")
        # print(yt.streams.first().default_filename)
        # new_name = "Hello" + "rename" + str(count) + ".mp4"
        # print(new_name)
        # os.rename(video_name, '/Users/admin/Downloads/Videos/' + college_names[count] +"___" + file_name[count] + ".mp4")
        # os.rename(video_name, college_names[count] +"___" + file_name[count]+ count + ".mp4")
        # print("renamed")
        # count +=1
        # time.sleep(3)
        # cell_reference = "D" + str(row_count)
        # sheet.update_acell(cell_reference, video_name)
        # row_count += 1
        
         
        # except: KeyError:
        #     print('KeyError')
        #     pass
        # except: HTTPError:
        #     print('HTTPError')
        #     pass
        # except: RemoteDisconnected:
        #     print('RemoteError')
        #     pass
        # except: VideoUnavailable:
        #     print('VideoDNEError')
        #     pass
            


# function to transcode url
def transcodeVideos(driver, video_titles):
    print("Transcoding Videos\n")
    count = 1

    # for filename in os.listdir("/Users/admin/Desktop/Renamed/"):
    #     print(filename[count])
    #     count+=1    
    wait = WebDriverWait(driver, 200)
    downloaded_Videos = os.listdir("/Users/admin/Desktop/Videos")

#######TESTING PURPOSES######
    # for filename in downloaded_Videos:
    #     print(filename)
###############################
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
    for filename in downloaded_Videos:
        if filename ==".DS_Store":
                    print("SKIPPED")
        else:
            print(filename)
            time.sleep(3)

            if count % 10 == 0:
                time.sleep(10)

            driver.get("https://transcoder.studentbridge.com/admin/")

            # goes to encode video page
            encode_button = driver.find_element_by_link_text('Encode Video')
            encode_button.click()

            # upload video file
            file_upload = driver.find_element_by_id('file_upload')
            # print("Here")
            file_upload.send_keys("/Users/admin/Desktop/Videos/" + filename)

            # print(video)
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
            os.rename("/Users/admin/Desktop/Videos/" + filename,"/Users/admin/Desktop/Done/" + filename)
            count += 1

def transferURLS(video_titles, college_names, driver, sheet):
    print("Tranferring Videos urls....\n")
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
    name_counter= 0
    for title in video_titles:
        try:
            # print(college_names)
            search = driver.find_element_by_name('search')
            search.click()
            title = stripFormat(title)
            # print(college_names[count]+" "+title)
            college_name = college_names[count]
            college_name = stripFormat(college_name)
            # print(college_name)
            print(college_name + " " +title)
            search.send_keys("DE " + str(name_counter) + " " + college_name + " " +title)
            # search.send_keys(title)
            # search.send_keys(college_names[count] +"_" + title)
            search.send_keys(Keys.RETURN)
            # print(title)
            time.sleep(3)
            url = driver.find_element_by_partial_link_text('http').text
            # url.click()
            
            # print(url)

            cell_reference = "H" + str(row_count)
            sheet.update_acell(cell_reference, url)
            row_count += 1
            count+=1
            # print('Updated needs to clear')
            search = driver.find_element_by_name('search')
            search.click() 
            search.clear()
            name_counter+=1
            # print('Complete')
        except NoSuchElementException:
            search = driver.find_element_by_name('search')
            search.click() 
            search.clear()
            row_count += 1
            count+=1
            pass    




def deleteVideos():
    folder = Path("/Users/admin/Downloads/Videos")
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


# Main Function
def automate(sheetname):
    print("Active\n")

    # saves spreadsheet being used
    sheet = client.open(sheetname).sheet1

    # creates arrays for video urls and college names
    video_URLS = getVideoURLS(sheet)
    college_names = getCollegeNames(sheet)


    # creates array of video titles
    video_titles = getVideoTitles(sheet)

    # creates array of video categories
    # video_categories = formatCategories(sheet)

    # creates array for file name
    file_name = getFileName(sheet)



#############FUNCTIONS#####################
    
    #1 -> Uses spread sheet to acquire all iped ids
    # getIpeds(sheet, college_names)

    # 2 -> This has a limitation on calls, used for errors that happen in the pytube api 
    # getTitleFromYouTube(video_URLS, driver, sheet)

    #3 -> format categories
    # formatCategories(sheet)

    #4 -> downloads, renames and transfer thumbnails from youtube to spreadsheet
    # getThumb(video_URLS,video_titles, file_name, college_names, driver, sheet)

    # time.sleep(10)

    #5 -> downloads all videos and saves them in "College Name___ Video Title"
    # downloadVideos(video_URLS,college_names,sheet)
    
    #6 -> transcodes every video
    # transcodeVideos(driver, video_titles)

    #7 -> transfer transcoded urls to spreadsheet
    # transferURLS(video_titles,college_names,driver,sheet);

    #8 -> deletes videos in downloaded video folders
    #deleteVideos()


automate("Rhode Island QA")



###########UNUSED FUNCTIONS###########
# title function that loops through URLS
# def getTitle(video_URLS, driver, sheet):
#     row_count = 1

#     # gets title for every video in sheet
#     for x in video_URLS:
#         getTitleFromYouTube(x, driver, row_count, sheet)
#         row_count += 1

# title function that loops through URLS
# def getPytubeTitle(video_URLS, driver, sheet):
#     row_count = 1
#     print("Getting Titles...\n")

#     # gets title for every video in sheet
#     for x in video_URLS:
#         try:
#             yt = YouTube(x).title
#             print(yt)
#             # title = yt.title
#             time.sleep(3)
#             title = stripFormat(yt)
#             print(title + " transferring")
        
#         except RegexMatchError:
#             title = "Error"
#             pass    
#         except KeyError:
#             title = "Error"
#             pass
#         cell_reference = "D" + str(row_count)
#         sheet.update_acell(cell_reference, title)
#         row_count += 1


                    


 


# def transferThumb():
    # open('/Users/admin/Desktop/Thumbnails/')
    # row_count = 1
    # print("Transferring Thumbnails...\n")
    # all_thumbnails = 

    # gets title for every video in sheet
    # cell_reference = "I" + str(row_count)
    # sheet.update_acell(cell_reference, title)

# Function to download youtube videos



    # gets titles for videos
    # getPytubeTitle(video_URLS, driver, sheet)

# def findErrors():
#     print("Finding Errors...")
#     # create an array that will hold the image errors
#     errors = []

#     # opens the current spreadsheet
#     driver.get("https://docs.google.com/spreadsheets/d/1A7jG029FraN8CpnV8g5F6C90AU99_ZL2XAHmLw_zEa0/edit#gid=0") 
#     # open file 
#     f = open("/Users/admin/Desktop/errors.txt","r")
    
#     for line in f:
#         search_error = line;

#         errors.append(line)
#     print(errors)        


# function to download thumbnails
# def downloadThumb(video_URLS,file_name, college_names, driver):
#     print("Downloading Thumbnails\n")
#     count = 0
#     for x in video_URLS:
#         driver.get("https://youtubethumbnailimage.com/") # goes to  website for downloading thumbnails
#         search = driver.find_element_by_class_name("urlinput")
#         search.send_keys(x)     # inputs video url
#         search.send_keys(Keys.RETURN)
#         download = driver.find_element_by_xpath("//*[@id='im']/div[4]/div[2]/form/input")
#         download.click()   # downloads url
#         time.sleep(3)

# def renameThumbs(file_name, video_titles,college_names):
#     try:
#         print("Renaming Thumbnails\n")
#         dirPath = Path(r'/Users/admin/Downloads/')
#         os.chdir(dirPath)
#         entries = ((os.stat(files), files) for files in os.listdir(dirPath))
#         entries = ((stat[ST_CTIME], files) for stat, files in entries)
#         for cdate, files in sorted(entries):
#             src = dirPath / files
#             dst = dirPath / ('/Users/admin/Desktop/Thumbnails/' + video_titles[count]+ "___" + college_names[count]  + ".jpg")
#             os.rename(src, dst)
#             count += 1
#         print("Done renaming")    
#     except :
#             print("IE: Done renaming") 
#             pass   

