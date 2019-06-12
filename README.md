# Web-Video-Scaper
Automate Content Uploading to Campus Compare

# What it does?

  Fills all the Import_Format columns 

# Installation

  Libraries needed to be installed: gspread, httplib2, oauthlib, apiclient, and pytube.
  
  Must install selenium - $ pip install selenium
  
  Install chromedriver - 
    https://sites.google.com/a/chromium.org/chromedriver/downloads
  
  Grant Google Drive API permission - 
    https://developers.google.com/drive/api/v3/quickstart/python
  
  Install pytube - $ pip install pytube
  
  Install youtube-dl $pip install youtube-dl OR https://ytdl-org.github.io/youtube-dl/download.html
# API Reference

 Google Sheets - https://developers.google.com/sheets/api/guides/concepts
 Selenium Webdriver - https://www.seleniumhq.org/docs/03_webdriver.jsp
 Pytube - https://python-pytube.readthedocs.io/en/latest/index.html
 
# How to Use
  1. Make sure all libraries are installed and all APIs are working properly
  2. Format spreadsheet according to import format (Do not include the top row of import_format)
  3. "Automate(state_name)" replace x with spreadsheet name
  4. After the program terminates, Audit categories.
  5. Audit Video Titles
  7. Add the top row of import_format to first row of spreadsheet
  8. Copy screenshot file names to spreadsheet to the proper row
  9. Download properly formatted spreadsheet as .csv
  10. Move the .csv to the folder with all the screenshots
  11. Compress the folder and post import on CC Admin Panel
  

