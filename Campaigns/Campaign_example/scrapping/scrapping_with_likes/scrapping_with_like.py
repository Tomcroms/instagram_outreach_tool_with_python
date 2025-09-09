from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium .webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
import concurrent.futures
import datetime
import threading
import google.auth
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os
import sys 

sys.path.insert(0, "C:/Users/thoma/OneDrive/Documents/Socialify/BOT")

from helpers.utils import DataCapacities
from helpers.instagram import InstagramWorker
from helpers.google import GoogleBot

def getAccounts(sheet_name, start, end):
    # Charger les identifiants
    creds = None
    creds = Credentials.from_service_account_file('google_credentials.json',
                                                scopes=["https://www.googleapis.com/auth/spreadsheets"])

    # Construire le service Google Sheets
    service = build('sheets', 'v4', credentials=creds)

    # ID de la feuille de calcul
    spreadsheet_id = '1WfR9DOTSBiS972ggOBWgDgnzrGOJ62c2n-SiMtaVvj8'

    # Spécifiez la plage de cellules pour la lecture, ici "Feuille 1!A1:B10"
    range_name = f"{sheet_name}!A{start}:B{end}"

    # Lire le contenu des cellules
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    # Extraire les valeurs
    values = result.get('values', [])

    # Construire la liste accounts
    accounts = [(row[0], row[1]) for row in values if len(row) >= 2]

    # Afficher la liste accounts
    return accounts



def cookies(driver):
    driver.get("https://www.instagram.com")
    try:
        time.sleep(random.uniform(2,4))
        button_cookies = driver.find_element(By.XPATH, f"//button[contains(text(), 'Autoriser')]")
        button_cookies.click()

    except:
        print("Impossible d'accepter les cookies")

def login(driver, username, password):
        time.sleep(random.uniform(2, 4))
        inputs_have_been_found = False
        while inputs_have_been_found == False:
            try:
                driver.find_element(By.NAME, "username").send_keys(username)
                driver.find_element(By.NAME, "password").send_keys(password)
                inputs_have_been_found = True                                
            except:
                print("Inputs de login introuvable")

        time.sleep(random.uniform(1, 2))
        try:
            button = driver.find_element(By.XPATH, "//button[@type='submit' and .//div[contains(text(), 'Se connecter')]]")
            button.click()
            time.sleep(random.uniform(4, 6))
        except:
            print("Bouton de connexion introuvable, on reessaye...")
            driver.get("https://www.instagram.com")
            time.sleep(random.uniform(30, 35))
            login(driver, username, password)

def ready_to_scrap(driver, username, password):
    cookies(driver)
    login(driver, username, password)

def get_post(driver, i):    
    print("get_post...")
    time.sleep(random.uniform(1, 2))
    try:                                
        elements = driver.find_elements(By.XPATH, "//a[div[@class='_aagu']]")
        elements[i].click()
    except:
        try:
            driver.find_element(By.XPATH, f"/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/div[{i+1}]/article/div/div/div[1]/div[1]/a")
        except:
            try:                               
                driver.find_element(By.XPATH, f"/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/div[{i+1}]/article/div[1]/div/div[1]/div[2]/a")
            except Exception as e:
                print(f"Erreur get post {e}")
                time.sleep(1000)


def get_liked(driver):
    print("get_targets_from_post_likes...")
    time.sleep(random.uniform(1,2))
    try:    
        like_btn = driver.find_element(By.XPATH, "//a//span[contains(text(), ' J’aime') or contains(text(), 'autres personnes')]")                                                  
        like_btn.click()
    except Exception as e: 
        print(f"Erreur clic sur btn like {e}")
        raise Exception
    time.sleep(random.uniform(1, 2))

def get_targets_from_post_likes(driver):
    time.sleep(random.uniform(4, 5))
    usernames = []          

    try:                                                 
        accounts_container = driver.find_element(By.XPATH, "//div[@style='height: 356px; overflow: hidden auto;']")
    except Exception as e:
        print(f"Erreur container similar_accounts: {e}")
        time.sleep(1000)

    accounts = accounts_container.find_elements(By.XPATH, "./div/*")
    for _ in range(10):
        accounts = accounts_container.find_elements(By.XPATH, "./div/*")
        for account in accounts:
            try:
                follower1 = account.find_element(By.XPATH, ".//a").get_attribute("href")
                usernames.append(follower1.split('/')[-2])
            except Exception as e:
                print(f"Erreur pour récupérer l'username du similar accounts: {e}")
        driver.execute_script("arguments[0].scrollTop += 660;", accounts_container)
        time.sleep(random.uniform(1.2, 1.6))

    return usernames

def main_acount_selection(driver, mainAccount):
    driver.get(f"https://www.instagram.com/{mainAccount}")
    time.sleep(random.uniform(3, 4))
    
def exit_post(driver):
    print("Exit post...")
    actions = ActionChains(driver)
    actions.send_keys(Keys.ESCAPE).perform()
    time.sleep(random.uniform(1, 2))
    actions.send_keys(Keys.ESCAPE).perform()

def add_to_scrapped_accounts(usernames):
    dossier_base = os.path.dirname(__file__)
    chemin_fichier1 = os.path.join(dossier_base, "scrappedAccounts.txt")
    with open(chemin_fichier1, 'a') as fichier:
        for element in usernames:
            fichier.write(element + "\n")

def worker(accounts, username, password):
    try:
        # Initialisation du driver
        options = webdriver.ChromeOptions()
        service = ChromeService(executable_path="C:/Users/thoma/OneDrive/Documents/Chrome/chromedriver-win64/chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=options)
        ready_to_scrap(driver, username, password)
        time.sleep(5)
        for account in accounts:
            main_acount_selection(driver, account)
            for i in range(30):
                try:
                    get_post(driver, i)
                    get_liked(driver)
                    usernames = get_targets_from_post_likes(driver)
                    print(usernames)
                    add_to_scrapped_accounts(usernames)
                    exit_post(driver)
                except:
                    print(f"Erreur sur le post {i}")
                    exit_post(driver)
                    continue
                time.sleep(random.uniform(2, 3))
        
    except Exception as e:
        print(f"Erreur worker: {e}")

campaign = "..."
working_accounts_sheet_name = "..."
spreadsheet_id = "..." 



accounts_to_scrap_with = ["entrepreneur"]

def main(accounts_to_scrap_with, start, end):
    base_directory_path = os.path.dirname(__file__)

    googleBot = GoogleBot(working_accounts_sheet_name, spreadsheet_id)
    accounts = googleBot.getAccountsByCampaign(campaign)

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        j=1
        for username, password in accounts:
            future = executor.submit(worker, accounts_to_scrap_with, username, password)
            futures.append(future)
            print("Worker "+str(j)+" ouvert !")
            j+=1
            # Pause de 5 secondes entre chaque démarrage de worker
            time.sleep(25)

main(accounts_to_scrap_with, 62, 62)
