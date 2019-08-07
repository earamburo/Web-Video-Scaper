# Web-Video-Scaper
Automate Content Uploading

# What it does?

  Downloads, takes Thumbnails, and Scrapes data from videos

# Installation

  *RECOMMENDED*
  Create a virtual enviorment so that you don't affect your computer's packages directly:
  https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/

  Libraries needed to be installed: 
  pip install : gspread, httplib2, oauthlib, apiclient, and pytube
  
  Must install selenium - $ pip install selenium
  
  Install chromedriver - 
    https://sites.google.com/a/chromium.org/chromedriver/downloads
  
  Grant Google Drive API permission - 
    https://developers.google.com/drive/api/v3/quickstart/python
    https://www.youtube.com/watch?v=cnPlKLEGR7E&t=294s
  
  Install pytube - $ pip install pytube
  
  Install youtube-dl $pip install youtube-dl OR https://ytdl-org.github.io/youtube-dl/download.html
  
  Update Python API client $pip install --upgrade google-api-python-client
  
# API Reference

 Google Sheets - https://developers.google.com/sheets/api/guides/concepts
 Selenium Webdriver - https://www.seleniumhq.org/docs/03_webdriver.jsp
 Pytube - https://python-pytube.readthedocs.io/en/latest/index.html
 
# How to Use
  1. Make sure the chromedrive and API credentials paths are correct
  2. Make sure all libraries are installed and all APIs are working properly
  3. Format spreadsheet according to import format (Do not include the top row of import_format)
  4. "Automate(state_name)" replace x with spreadsheet name
  5. After the program terminates, Audit categories.
  6. Audit Video Titles
  7. Add the top row of import_format to first row of spreadsheet
  8. Copy screenshot file names to spreadsheet to the proper row
  9. Download properly formatted spreadsheet as .csv
  10. Move the .csv to the folder with all the screenshots
  11. Compress the folder and post import on CC Admin Panel
  

