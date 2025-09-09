from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium .webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
import os
import sys
import time
import random
import concurrent.futures
import threading

sys.path.insert(0, "C:/Users/thoma/OneDrive/Documents/Socialify/BOT")

from helpers.utils import DataCapacities
from helpers.instagram import InstagramBot
from helpers.google import GoogleBot

def worker(username, password, targets, lock, googleBot, base_directory_path):
    try:
        # Initialisation du driver
        options = webdriver.ChromeOptions()
        service = ChromeService(executable_path="C:/Program Files (x86)/Google/chromedriver-win64/chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=options)
        instagramBot = InstagramBot(driver, username, password)

        instagramBot.connect_to_instagram()
        if (not instagramBot.test_connexion(googleBot)):
            print("Test connexion unsuccessful")
            driver.quit()
            return

        while len(targets) > 0:
            lock.acquire()
            target = targets.pop(0)
            lock.release()
            try:
                instagramBot.scrappingCapacities.scrap_target(target, googleBot, base_directory_path)
            except Exception as e:
                print(f'======== ERREUR ======== SCRAP ========= {e}')
            time.sleep(random.uniform(11.8, 17.4))
        

        
    except Exception as e:
        print(f"Erreur worker: {e}")



campaign = "..."
working_accounts_sheet_name = "..."
spreadsheet_id = "..." 

def main():

    base_directory_path = os.path.dirname(__file__)
    googleBot = GoogleBot("C:/Users/thoma/OneDrive/Documents/Socialify/BOT/google_credentials.json", working_accounts_sheet_name, scrapping_spreadsheet_id)
      

    accounts = googleBot.getAccountsByCampaign(campaign)

    DataCapacities.remove_already_scrapped_targets(base_directory_path)
    targets =  DataCapacities.getTargetsForScrap(base_directory_path)

    print(f"Nombre de cibles restantes : {len(targets)}")

    lock = threading.Lock()
    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        futures = []
        j=1
        for username, password in accounts:
            future = executor.submit(worker, username, password, targets, lock, googleBot, base_directory_path)
            futures.append(future)
            print("Worker "+str(j)+" ouvert !")
            j+=1
            # Pause de 5 secondes entre chaque démarrage de worker
            time.sleep(44)


main()

