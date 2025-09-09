import sys
import os
import random
import time
import datetime
import concurrent.futures
import threading

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
sys.path.insert(0, "C:/Users/thoma/OneDrive/Documents/Socialify/BOT")

from helpers.utils import DataCapacities
from helpers.instagram import InstagramWorker
from helpers.google import GoogleBot


campaign = "..."
working_accounts_sheet_name = "..."
spreadsheet_id = "..." 



def main(nbMessagesSent):
    googleBot = GoogleBot("C:/Users/thoma/OneDrive/Documents/Socialify/BOT/google_credentials.json", working_accounts_sheet_name, spreadsheet_id)
    accounts = googleBot.getAccountsByCampaign(campaign)


    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        lock = threading.Lock()
        futures = []
        j=1
        for username, password in accounts:
            future = executor.submit(InstagramWorker.worker_read_reply, campaign, username, password, nbMessagesSent, googleBot)
            futures.append(future)
            time.sleep(random.uniform(8, 34))
            
main(1)
