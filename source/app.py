from asyncio.log import logger
from selenium import webdriver
from faker import Faker
import os
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
import pandas as pd
import boto3

# FUNCTION TO ALLOW THE DOWNLOAD OF THE FILEs ON HEADLESS CHROME
def enable_download_headless(browser,download_dir):
    browser.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd':'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    browser.execute("send_command", params)

#   -------------------------------------------------------

prefs = {
    "profile.default_content_settings.popups": 0,
    "download.default_directory": r"/tmp",
    "directory_upgrade": True
    }

def get_driver():
    fake_user_agent = Faker()
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", prefs)
    options.binary_location = '/opt/chrome-linux/chrome'
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    options.add_argument('--disable-web-security')
    options.add_argument('--user-agent=' + fake_user_agent.user_agent())
    options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument("--single-process")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("window-size=1400,1200")
    options.add_argument("--disable-dev-tools")
    options.add_argument(f"--user-data-dir={'/tmp'}")
    options.add_argument(f"--data-path={'/tmp'}")
    options.add_argument(f"--disk-cache-dir={'/tmp'}")
    chrome = webdriver.Chrome("/opt/chromedriver", options=options)

    return chrome

def lambda_handler(event, context):
    
    driver = get_driver()
    
    enable_download_headless(driver,'/tmp')
    username = os.environ.get('username')
    password = os.environ.get('password')
    
    current_direct = os.getcwd()
    print(f'Current Directory: {current_direct}')
    
    login_url = os.environ.get('login_url')
    template_url = os.environ.get('template_url')
    
    driver.get(template_url)
    time.sleep(10)
    
    user = WebDriverWait(driver,25).until(
        EC.presence_of_element_located((By.ID, 'fieldUsername')))
    user.send_keys(username)
    print('sent username')
    
    passw = WebDriverWait(driver, 25).until(
        EC.presence_of_element_located((By.ID, 'fieldPassword')))   
    
    passw.send_keys(password)
    print('Password submitted')
    time.sleep(6)
    submit = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'btnEnter')))
    
    submit.click()
    print('submitted')
    time.sleep(10)
    
    driver.get(template_url)
    
    time.sleep(10)
    logger.info(f"URL for Template: {template_url}")
    print('Signed in, getting emails from export')
    
    next_button_1 = WebDriverWait(driver, 25).until(
        EC.element_to_be_clickable((By.ID, f'nextButton0')))
    next_button_1.click()
    
    next_button_2 = WebDriverWait(driver, 25).until(
    EC.element_to_be_clickable((By.ID, f'nextButton1')))
    next_button_2.click()
            
    
    csv_button = WebDriverWait(driver, 25).until(
        EC.element_to_be_clickable((By.ID, 'btnExport')))
    csv_button.click()
    print('Exporting email csv now')
    
    export = os.environ.get('exported_name')
    path = f'/tmp/{export}'
    
    while not os.path.exists(path):
        time.sleep(1)
        
    if os.path.isfile(path):
        emails_df = pd.read_csv(path)
        print(f'There are {emails_df.shape[0]} emails being exported')
    else:
        raise ValueError("%s isn't a file!" % path)
    
    driver.quit()
    
    
    print(emails_df.head())
    print(emails_df.shape)
    
    
    bucket = os.environ.get('bucket')
    key = os.environ.get('key')
    
    data = open(r'''/tmp/student_email_export.csv''', 'rb')
    
    s3 = boto3.resource('s3')
    s3.Bucket(bucket).put_object(Key = key, Body = data)
    print(f'Emails Deposited to {key}')
    