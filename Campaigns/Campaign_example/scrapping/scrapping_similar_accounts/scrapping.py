import shutil
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium .webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
import time
import random
import concurrent.futures
import datetime
import threading
import pyautogui
import google.auth
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from selenium.webdriver.common.action_chains import ActionChains
import os

import signal
import sys


from helpers.utils import DataCapacities
from helpers.instagram import InstagramBot
from helpers.google import GoogleBot

def signal_handler(driver, sig, frame):
    print('Interruption détectée, fermeture des navigateurs...')
    driver.quit()
    sys.exit(0)


def update_google_sheet(spreadsheet_id, target, accountInfo):
    try:
        # Charger les identifiants
        creds = None
        creds = Credentials.from_service_account_file('C:/Users/thoma/OneDrive/Documents/Socialify/BOT/BASES/google_credentials.json',
                                                    scopes=["https://www.googleapis.com/auth/spreadsheets"])
    except Exception as e:
        print(f"Erreur lors de la création des identifiants : {e}")

    # Construire le service Google Sheets
    service = build('sheets', 'v4', credentials=creds)

    #sheetName
    sheet_name = 'Feuille 1'

    username = target
    nbFollowers = accountInfo["nbFollowers"]
    nbFollowing = accountInfo["nbFollowing"]
    nbPublications = accountInfo["nbPublications"]
    fullName = accountInfo["fullName"]
    bio = accountInfo["bio"]
    link = accountInfo["url_link"]

    values = [[username, fullName, nbFollowers, nbFollowing, nbPublications, bio, link]]

    # google_sheet = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
    #                             range=sheet_name).execute()
    # values = google_sheet.get('values', [])

    # current_line = len(values)+1

    body = {
    'values': values
    }

    print(values)
    # Spécifiez la plage de cellules pour l'écriture, ici "test!A4"
    range_name = f"{sheet_name}"

    try:
        sheet = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            body=body,
            valueInputOption='RAW'  # Les valeurs sont écrites telles quelles
        ).execute()


        print(f"{sheet.get('updatedCells')} cell(s) updated.")
    except Exception as e:
        print(f"Erreur drive : {e}")




def worker(username, password, lock, googleBot, scrapping_spreadsheet_id, base_directory_path):
    options = webdriver.ChromeOptions()
    service = ChromeService(executable_path="C:/Program Files (x86)/Google/chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    instagramBot = InstagramBot(driver, username, password)

    instagramBot.connect_to_instagram()
    if(not instagramBot.test_connexion(googleBot)):
        return



    i=0
    while True:
        if len(possible_targets) < 1:
            print("No more targets")
            instagramBot.scrappingCapacities.reload_possible_targets(lock)
            if len(possible_targets) < 1:
                return

        print("Nouvelle cible")
        lock.acquire()
        possible_target = possible_targets.pop(0)
        lock.release()
        try:
            instagramBot.scrappingCapacities.go_to_next_target(driver, possible_target)
            if(instagramBot.scrappingCapacities.accountLooksGood(driver)):
                DataCapacities.add_to_selected_targets(possible_target)
                accountInfo = instagramBot.scrappingCapacities.get_account_info(driver)
                googleBot.update_google_sheet(scrapping_spreadsheet_id, possible_target, accountInfo)
                DataCapacities.add_to_accounts_used_for_similar(possible_target, )
                instagramBot.scrappingCapacities.display_similar_accounts(driver)
                accounts = instagramBot.scrappingCapacities.get_similar_accounts(driver)
                print(accounts)

                for account in accounts:
                    DataCapacities.add_to_all_possible_targets(account)
            

            else:
                DataCapacities.add_to_accounts_used_for_similar(possible_target)
                time.sleep(random.uniform(7, 8))
                i+=1
        except Exception as e:
            print(f"Erreur boucle worker{e}")
            time.sleep(random.uniform(10, 20))
        print(i)
        if(i>100):
            i=0
            time.sleep(random.uniform(156, 207))
        time.sleep(random.uniform(8, 12))


dossier_base = os.path.dirname(__file__)
chemin_fichier1 = os.path.join(dossier_base, "all_possible_targets_username.txt")
with open(chemin_fichier1, "r") as file:
    possible_targets = [target.strip() for target in file.read().split("\n")] 


campaign = "..."
working_accounts_sheet_name = "..."
spreadsheet_id = "..." 


def main(start, end): 
    base_directory_path = os.path.dirname(__file__)
    googleBot = GoogleBot("C:/Users/thoma/OneDrive/Documents/Socialify/BOT/google_credentials.json", working_accounts_sheet_name, scrapping_spreadsheet_id)
                                                                                                                                                                                                                                                                                                                                                                               #pas encore vérifié lui 
    accounts = googleBot.getAccounts(start, end)
    googleBot.remove_used_for_similar_scrapping()

    lock = threading.Lock()
    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        futures = []
        j=1
        for username, password in accounts:
            future = executor.submit(worker, username, password, lock, googleBot, scrapping_spreadsheet_id, base_directory_path)
            futures.append(future)
            print("Worker "+str(j)+" ouvert !")
            j+=1
            # Pause de 5 secondes entre chaque démarrage de worker
            time.sleep(random.uniform(8, 24))

main(65, 80)

