from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium .webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver import ActionChains
import time
import random
import concurrent.futures
import sys

sys.path.insert(0, "C:/Users/thoma/OneDrive/Documents/Socialify/BOT")

from helpers.utils import DataCapacities
from helpers.instagram import InstagramWorker
from helpers.google import GoogleBot


campaign = "..."
working_accounts_sheet_name = "..."
spreadsheet_id = "..." 


def main():
    googleBot = GoogleBot("C:/Users/thoma/OneDrive/Documents/Socialify/BOT/google_credentials.json", working_accounts_sheet_name, spreadsheet_id)
    accounts = googleBot.getAccountsByCampaign(campaign)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        futures = []
        j=1
        for username, password in accounts:
            future = executor.submit(InstagramWorker.worker_delete_unread_messages, username, password, googleBot)
            futures.append(future)
            time.sleep(random.uniform(18, 74))
            
main()