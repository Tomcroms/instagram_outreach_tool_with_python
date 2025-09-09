import os
from selenium.webdriver.common.by import By
import time
import datetime
import random
import concurrent.futures
import threading
import pyperclip
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium .webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import JavascriptException
from helpers.google import GoogleBot
from helpers.utils import DataCapacities, TextProcessor, TimeProcessor
from helpers.mongodb import MongoDB
from helpers.gptUtils import GPTutils


class InstagramWorker:
   
   #test connection
    def testConnectionByCampaignId(campaignId):
        mongoDB = MongoDB()
        instagramAccount = mongoDB.getAccountsByCampaignId(campaignId)[0]
        driver = InstagramWorker.initializeDriver()
        instagramBot = InstagramBot(driver, instagramAccount.get("username"), instagramAccount.get("password"), instagramAccount.get("twoFaTokens"))
        instagramBot.connect_to_instagram()
        instagramBot.test_connexion(mongoDB=mongoDB)
        time.sleep(2000)

    def testConnectionByUsername(username):
        mongoDB = MongoDB()
        instagramAccount = mongoDB.getAccountByUsername(username)[0]
        driver = InstagramWorker.initializeDriver()
        instagramBot = InstagramBot(driver, instagramAccount.get("username"), instagramAccount.get("password"), instagramAccount.get("twoFaTokens"))
        instagramBot.connect_to_instagram()
        instagramBot.test_connexion(mongoDB=mongoDB)

    #bio
    def modifyBioByCampaignId(campaignId, bio):
        mongoDB = MongoDB()
        instagramAccounts = mongoDB.getAccountsByCampaignId(campaignId)

        with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
            futures = []
            for instagramAccount in instagramAccounts:
                future = executor.submit(InstagramWorker.workerModifyBio, mongoDB, instagramAccount.get("username"), instagramAccount.get("password"), bio, instagramAccount.get("twoFaTokens"))
                futures.append(future)
                time.sleep(random.uniform(38, 172))

    def workerModifyBio(mongoDB, username, password, bio, twoFaTokens):
        driver = InstagramWorker.initializeDriver()
        instagramBot = InstagramBot(driver, username, password, twoFaTokens)
        instagramBot.connect_to_instagram()
        instagramBot.test_connexion(mongoDB=mongoDB)
        instagramBot.accountCapacities.getToModifyAccount()
        instagramBot.accountCapacities.updateBio(bio)
        instagramBot.test_connexion(mongoDB=mongoDB)


    #delete dms
    def deleteDmByCampaignId(campaignId):
        mongoDB = MongoDB()
        instagramAccounts = mongoDB.getAccountsByCampaignId(campaignId)

        # instagramAccounts = mongoDB.getAccountByUsername("julie_morel_1996")

        # filteredInstagramAccounts = []
        # filteredInstagramAccounts.append(instagramAccounts[0])
        with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
            futures = []
            for instagramAccount in instagramAccounts:
                future = executor.submit(InstagramWorker.workerDeleteDmByCampaignId, mongoDB, instagramAccount.get("username"), instagramAccount.get("password"), instagramAccount.get("twoFaTokens"))
                futures.append(future)
                time.sleep(random.uniform(38, 172))

    def workerDeleteDmByCampaignId(mongoDB, username, password, twoFaTokens):
        driver = InstagramWorker.initializeDriver()
        instagramBot = InstagramBot(driver, username, password, twoFaTokens)
        instagramBot.connect_to_instagram()
        instagramBot.test_connexion(mongoDB=mongoDB)
        instagramBot.disable_notifications()
        instagramBot.messageCapacities.delete_unread_messages()


    def modifyBioAndDeleteDmByCampaignId(campaignId,bio):
        mongoDB = MongoDB()
        instagramAccounts = mongoDB.getAccountsByCampaignId(campaignId)

        with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
            futures = []
            for instagramAccount in instagramAccounts:
                future = executor.submit(InstagramWorker.workerModifyBioAndDeleteDmByCampaignId, mongoDB, instagramAccount.get("username"), instagramAccount.get("password"), bio, instagramAccount.get("twoFaTokens"))
                futures.append(future)
                time.sleep(random.uniform(38, 172))

    def workerModifyBioAndDeleteDmByCampaignId(mongoDB, username, password, bio, twoFaTokens):
        driver = InstagramWorker.initializeDriver()
        instagramBot = InstagramBot(driver, username, password, twoFaTokens)
        instagramBot.connect_to_instagram()
        instagramBot.test_connexion(mongoDB=mongoDB)
        instagramBot.accountCapacities.getToModifyAccount()
        instagramBot.accountCapacities.updateBio(bio)
        instagramBot.test_connexion(mongoDB=mongoDB)
        instagramBot.disable_notifications()
        instagramBot.messageCapacities.delete_unread_messages()


    #scraping followers
    def scrapingFollowersByCampaignId(campaignId, usernames, numbersOfAccountsToScrap):
        mongoDB = MongoDB()
        # instagramAccount = mongoDB.getAccountForScraping(campaignId)  #can be changed in the future to get accounts (not just 1)

        instagramAccount = mongoDB.getAccountsByCampaignId(campaignId)[1]
        
        InstagramWorker.workerScrapingFollowersByUsername(campaignId, mongoDB, instagramAccount.get("username"), instagramAccount.get("password"), instagramAccount.get("twoFaTokens"), usernames, numbersOfAccountsToScrap)

    def workerScrapingFollowersByUsername(campaignId, mongoDB, username, password, twoFaTokens, usernames, numbersOfAccountsToScrap):
        driver = InstagramWorker.initializeDriver()
        instagramBot = InstagramBot(driver, username, password, twoFaTokens)
        instagramBot.connect_to_instagram()
        instagramBot.test_connexion(mongoDB=mongoDB)
        for instagramAccount in usernames:
            instagramBot.scrappingCapacities.scraping_followers(instagramAccount, numbersOfAccountsToScrap, campaignId, mongoDB)
            time.sleep(random.uniform(8, 12))


    #read and reply
    def testReadAndReply(campaignId):
        mongoDB = MongoDB()
        instagramAccounts = mongoDB.getAccountsByCampaignId(campaignId)

        # filteredInstagramAccounts = []
        # filteredInstagramAccounts.append(instagramAccounts[0])
        InstagramWorker.workerTestReadAndReply(campaignId, mongoDB, instagramAccounts[0].get("_id"), instagramAccounts[0].get("username"), instagramAccounts[0].get("password"), instagramAccounts[0].get("twoFaTokens"))   

    def workerTestReadAndReply(campaignId, mongoDB, instagramAccountId, username, password, twoFaTokens):
        driver = InstagramWorker.initializeDriver()
        instagramBot = InstagramBot(driver, username, password, twoFaTokens)
        instagramBot.connect_to_instagram()
        instagramBot.test_connexion(mongoDB=mongoDB)
        instagramBot.disable_notifications()
        instagramBot.readAndReply(1, mongoDB, campaignId, instagramAccountId)
        time.sleep(1000)     


    #send message
    def testSendMessageByCampaignId(campaignId, dailyDuration):
        mongoDB = MongoDB()
        nbMessagesSent=1 
        # instagramAccounts = mongoDB.getAccountsByCampaignId(campaignId)
        instagramAccounts = mongoDB.getAccountByUsername("julie_morel_1996")
        targets = ["thomas_laumonier"]
        message = mongoDB.getCampaignMessage(campaignId)
        instagramAccount = instagramAccounts[0]
        amazonLink = mongoDB.getAmazonLinkByCampaignId(campaignId)

        print(instagramAccount.get("_id"))
        driver = InstagramWorker.initializeDriver()
        instagramBot = InstagramBot(driver, instagramAccount.get("username"), instagramAccount.get("password"), instagramAccount.get("twoFaTokens"))
        instagramBot.connect_to_instagram()
        if not instagramBot.test_connexion(mongoDB=mongoDB): return
        instagramBot.disable_notifications()

        # instagramBot.readAndReplyWithGPT(nbMessagesSent, mongoDB, campaignId, instagramAccount.get("_id"), amazonLink)
        if(instagramBot.sendMessageCapacities.send_message('thomas_laumonier', targets, message, threading.Lock())):
            print("Success !")
        else:
            print("Error test send message...")


    def sendCampaignMessagesByCampaignId(campaignId, dailyDuration):
        mongoDB = MongoDB()
        instagramAccounts = mongoDB.getAccountsByCampaignId(campaignId)
        targets = mongoDB.getUncontactedTargets(campaignId)
        message = mongoDB.getCampaignMessage(campaignId)

        with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
            lock = threading.Lock()
            futures = []
            for instagramAccount in instagramAccounts:
                future = executor.submit(InstagramWorker.worker_send_messages_with_mongoDB, campaignId, instagramAccount.get("_id"), message, instagramAccount.get("username"), instagramAccount.get("password"), instagramAccount.get("Names"), targets, lock, dailyDuration, mongoDB, instagramAccount.get("twoFaTokens"))
                futures.append(future)
                time.sleep(random.uniform(38, 172))
            
    def worker_send_messages_with_mongoDB(campaignId, instagramAccountId, message, username, password, name, targets, lock, totalTime, mongoDB, twoFaTokens=None):
        nbMessagesSent = 1
        driver = InstagramWorker.initializeDriver()
        instagramBot = InstagramBot(driver, username, password, twoFaTokens)
        instagramBot.connect_to_instagram()
        if not instagramBot.test_connexion(mongoDB=mongoDB): return

        if(name and "xxx" in message):
            message = message.replace("xxx", name)

        while True:
            instagramBot.disable_notifications()
            
            current_time = datetime.datetime.now()
            delays = random.sample(range(totalTime * 3600), random.randint(27, 29))
            delays.sort()

            start_time = datetime.datetime(year=current_time.year, month=current_time.month, day=current_time.day, hour=current_time.hour, minute=current_time.minute, second=current_time.second) + datetime.timedelta(seconds=100)            
            
            for delay in delays:

                if(not instagramBot.isAccountConnected()):
                    mongoDB.updateInstagramAccount(username, "Not Working", None)
                    print(f"Error: {username} is not connected anymore at {datetime.datetime.now()}")
                    return

                instagramBot.readAndReply(nbMessagesSent, mongoDB, campaignId, instagramAccountId)
                
                current_time = datetime.datetime.now()
                if(current_time.hour >= 21 or current_time.hour < 8):
                    break

                target = instagramBot.sendMessageCapacities.get_next_target(targets, lock)
                if(target):

                    send_message_time = start_time + datetime.timedelta(seconds=delay)
                    sleep_time = (send_message_time - datetime.datetime.now()).total_seconds()

                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    else:
                        sleep_time = -sleep_time
                        time.sleep(sleep_time)

                    if(instagramBot.sendMessageCapacities.send_message(target, targets, message, lock)):
                        mongoDB.addSentMessage(campaignId, instagramAccountId, target, message)
                        mongoDB.updateTargetContacted(target, campaignId)
                    else:
                        print(f"Erreur niveau maximal send_message pour {username}")
                        time.sleep(3600)
                        driver.quit()
                        return

                else:
                    print("No more users to contact")       
                    driver.quit()
                    return

            TimeProcessor.sleepToAround9am()


    #send message with gpt
    def testReadAndReplyWithGPTbyUsernameAndCampaignId(campaignId, username):
        mongoDB = MongoDB()
        nbMessagesSent=1
        instagramAccounts = mongoDB.getAccountByUsername(username)
        print(instagramAccounts)
        instagramAccount = instagramAccounts[0]
        amazonLink = mongoDB.getAmazonLinkByCampaignId(campaignId)

        print(instagramAccount.get("_id"))
        driver = InstagramWorker.initializeDriver()
        instagramBot = InstagramBot(driver, instagramAccount.get("username"), instagramAccount.get("password"), instagramAccount.get("twoFaTokens"))
        instagramBot.connect_to_instagram()
        if not instagramBot.test_connexion(mongoDB=mongoDB): return
        instagramBot.disable_notifications()

        instagramBot.readAndReplyWithGPT(nbMessagesSent, mongoDB, campaignId, instagramAccount.get("_id"), amazonLink)        

    def sendMessageForAmazonByCampaignIdWithGPT(campaignId, dailyDuration):
        mongoDB = MongoDB()
        instagramAccounts = mongoDB.getAccountsByCampaignId(campaignId)
        targets = mongoDB.getUncontactedTargets(campaignId)
        message = mongoDB.getCampaignMessage(campaignId)
        amazonLink = mongoDB.getAmazonLinkByCampaignId(campaignId)
        print(amazonLink)

        with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
            lock = threading.Lock()
            futures = []
            for instagramAccount in instagramAccounts:
                future = executor.submit(InstagramWorker.workerSendMessageForAmazonByCampaignIdWithGPT, campaignId, instagramAccount.get("_id"), message, instagramAccount.get("username"), instagramAccount.get("password"), instagramAccount.get("Names"), targets, lock, dailyDuration, mongoDB, amazonLink, instagramAccount.get("twoFaTokens"))
                futures.append(future)
                time.sleep(random.uniform(38, 172))

    def workerSendMessageForAmazonByCampaignIdWithGPT(campaignId, instagramAccountId, message, username, password, name, targets, lock, totalTime, mongoDB, amazonLink, twoFaTokens=None):
        nbMessagesSent = 1
        driver = InstagramWorker.initializeDriver()
        instagramBot = InstagramBot(driver, username, password, twoFaTokens)
        instagramBot.connect_to_instagram()

        if not instagramBot.test_connexion(mongoDB=mongoDB): return

        if(name and "xxx" in message):
            message = message.replace("xxx", name)

        while True:
            instagramBot.disable_notifications()
            
            current_time = datetime.datetime.now()
            delays = random.sample(range(totalTime * 3600), random.randint(27, 29))
            delays.sort()

            start_time = datetime.datetime(year=current_time.year, month=current_time.month, day=current_time.day, hour=current_time.hour, minute=current_time.minute, second=current_time.second) + datetime.timedelta(seconds=100)            
            
            for delay in delays:

                if(not instagramBot.isAccountConnected()):
                    mongoDB.updateInstagramAccount(username, "Not Working", None)
                    print(f"Error: {username} is not connected anymore at {datetime.datetime.now()}")
                    return

                instagramBot.readAndReplyWithGPT(nbMessagesSent, mongoDB, campaignId, instagramAccountId, amazonLink)
                
                current_time = datetime.datetime.now()
                if(current_time.hour >= 21 or current_time.hour < 8):
                    break

                target = instagramBot.sendMessageCapacities.get_next_target(targets, lock)
                if(target):

                    send_message_time = start_time + datetime.timedelta(seconds=delay)
                    sleep_time = (send_message_time - datetime.datetime.now()).total_seconds()

                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    else:
                        sleep_time = -sleep_time
                        time.sleep(sleep_time)

                    if(instagramBot.sendMessageCapacities.send_message(target, targets, message, lock)):
                        mongoDB.addSentMessage(campaignId, instagramAccountId, target, message)
                        mongoDB.updateTargetContacted(target, campaignId)
                    else:
                        print(f"Erreur niveau maximal send_message pour {username}")
                        time.sleep(3600)
                        driver.quit()
                        return

                else:
                    print("No more users to contact")       
                    driver.quit()
                    return

            TimeProcessor.sleepToAround9am()






    def openChromeDriver():
        driver = InstagramWorker.initializeDriver()
        time.sleep(20)

    ## Utils
    def initializeDriver():
        options = webdriver.ChromeOptions()
        options.add_argument("--no-first-run")  # Empêche l'affichage du popup de premier lancement
        options.add_argument("--disable-default-apps")  # Désactive les applications par défaut
        prefs = {
            "search_provider_overrides": {
                "name": "Google",
                "keyword": "https://www.google.com",
                "search_url": "https://www.google.com/search?q={searchTerms}",
                "suggest_url": "https://www.google.com/complete/search?q={searchTerms}"
            }
        }
        
        # Ajout des préférences à ChromeOptions
        options.add_experimental_option("prefs", prefs)
        service = ChromeService(executable_path="C:/Users/thoma/OneDrive/Documents/Chrome/chromedriver-win64/chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=options)

        return driver


    ## Scraping
    def scraping_compatible_accounts(base_directory_path):
        mongoDB = MongoDB()

        instagramAccounts = [("banjamin_durandet","rasoolap1"), ("gregoire_delanet", "rasoolap1")]
        DataCapacities.remove_already_scrapped_targets(base_directory_path)
        targets = DataCapacities.getTargetsForScrap(base_directory_path)
        print(targets)

        # instagramAccount = instagramAccounts[0]
        # lock = threading.Lock()
        # InstagramWorker.worker_scrap_compatible_accounts(instagramAccount[0], instagramAccount[1], targets, lock, base_directory_path)

        with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
            lock = threading.Lock()
            futures = []
            for username, password in instagramAccounts:
                future = executor.submit(InstagramWorker.worker_scrap_compatible_accounts, username, password, targets, lock, base_directory_path)
                futures.append(future)
                time.sleep(random.uniform(38, 172))

    def worker_scrap_compatible_accounts(username, password, targets, lock, base_directory_path):
        driver = InstagramWorker.initializeDriver()
        instagramBot = InstagramBot(driver, username, password)
        instagramBot.connect_to_instagram()
        while True:
            target = instagramBot.sendMessageCapacities.get_next_target(targets, lock)
            if(target):
                instagramBot.scrappingCapacities.go_to_next_target(target)

                if(instagramBot.scrappingCapacities.accountStillExists()):
                    print("Good")
                    DataCapacities.add_to_selected_targets(target, base_directory_path)
                    accountInfo = instagramBot.scrappingCapacities.get_account_info()
                    GoogleBot("","").update_google_sheet(target, accountInfo, "19ancYqrHFi4U0Y791orar5HClsirmQyFFMC_Xpq1xJA")
                    #to do  -> write account on gg sheet 
                else:
                    print("Not good..")
                    #add to already scrapped
                DataCapacities.add_scrapped_target(target, base_directory_path)

            else:
                print("No more target")
                return
            
            time.sleep(random.uniform(4, 22))

    def scraping_similar_accounts(base_directory_path):
        instagramAccounts = [("francois_dutrait","nJ0EINMnTN1"), ("thomas_dureims", "x5X6YHio"), ("david__duplessis", "YnyoBQxbF"), ("henry_dutourette", "1VRToRlMy"), ("reza86_V36Hd", "13811380"), ("remaa325Hdjk", "13811380")]
        random.shuffle(instagramAccounts)
        DataCapacities.remove_used_for_similar_scrapping(base_directory_path)
        targets = DataCapacities.getTargetsForScrap(base_directory_path)
        print(targets)

        # instagramAccount = instagramAccounts[0]
        # lock = threading.Lock()
        # InstagramWorker.worker_scrap_similar_accounts(instagramAccount[0], instagramAccount[1], targets, lock, base_directory_path)

        with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
            lock = threading.Lock()
            futures = []
            for username, password in instagramAccounts:
                future = executor.submit(InstagramWorker.worker_scrap_similar_accounts, username, password, targets, lock, base_directory_path)
                futures.append(future)
                time.sleep(random.uniform(38, 172))

    def worker_scrap_similar_accounts(username, password, possible_accounts, lock, base_directory_path):
        driver = InstagramWorker.initializeDriver()
        instagramBot = InstagramBot(driver, username, password)
        instagramBot.connect_to_instagram()
        i=0
        while True:
            i+=1
            possible_account = instagramBot.sendMessageCapacities.get_next_target(possible_accounts, lock)
            if (not possible_account):
                print(f"Reloading targets for {username}")
                instagramBot.scrappingCapacities.reload_possible_targets(lock)
                if (not possible_account):
                    print(f"No more targets for {username}")
                    return
            
            try:
                instagramBot.scrappingCapacities.go_to_next_target(possible_account)
                if(instagramBot.scrappingCapacities.accountLooksGood()):
                    DataCapacities.add_to_selected_targets(possible_account, base_directory_path)
                    accountInfo = instagramBot.scrappingCapacities.get_account_info()
                    GoogleBot("","").update_google_sheet(possible_account, accountInfo, "19ancYqrHFi4U0Y791orar5HClsirmQyFFMC_Xpq1xJA")
                    DataCapacities.add_to_accounts_used_for_similar(possible_account, base_directory_path)
                    instagramBot.scrappingCapacities.display_similar_accounts()
                    print("displayed")
                    accounts = instagramBot.scrappingCapacities.get_similar_accounts()
                    print(accounts)

                    for account in accounts:
                        DataCapacities.add_to_all_possible_targets(account, base_directory_path)
                

                else:
                    DataCapacities.add_to_accounts_used_for_similar(possible_account, base_directory_path)
                    time.sleep(random.uniform(4, 8))

            except Exception as e:
                print(f"Erreur boucle worker{e}")
                time.sleep(random.uniform(10, 20))

            time.sleep(random.uniform(4, 10))

            if(i>random.uniform(98, 105)):
                i=0
                time.sleep(random.uniform(246, 455))


class InstagramBot: 
    def __init__(self, driver, username, password, twoFaTokens=None):
        self.driver = driver
        self.username = username
        self.password = password
        self.twoFaTokens = twoFaTokens
        self.accountCapacities = AccountCapacities(driver, username, password)
        self.messageCapacities = MessageCapacities(driver, username, password)
        self.sendMessageCapacities = SendMessageCapacities(driver, username, password)
        self.deleteMessageCapacities = DeleteMessageCapacities(driver)
        self.scrappingCapacities = ScrappingCapacities(driver, username, password)

    def isAccountConnected(self):
        accountIsConnected = False
        if("instagram" in self.driver.current_url):
            accountIsConnected = True
        return accountIsConnected

    def accept_cookies(self):
        time.sleep(random.uniform(3, 4))
        try:
            button_cookies = self.driver.find_element(By.XPATH, f"//button[contains(text(), 'Autoriser ')]")
            button_cookies.click()
        except:
            try:
                button_cookies = self.driver.find_element(By.XPATH, f"//div[contains(@aria-label, 'Autoriser tous les cookies')]")
                button_cookies.click()
                time.sleep(random.uniform(2, 3))
            except:
                print(end="")


    def login(self):
        time.sleep(random.uniform(6, 8))
        inputs_have_been_found = False
        while not inputs_have_been_found:
            try:
                self.driver.find_element(By.NAME, "username").send_keys(self.username)
                self.driver.find_element(By.NAME, "password").send_keys(self.password)
                inputs_have_been_found = True
            except:
                print("Inputs de login introuvable")

        time.sleep(random.uniform(5, 7.5))
        try:
            button = self.driver.find_element(By.XPATH, "//button[@type='submit' and .//div[contains(text(), 'Se connecter')]]")
            button.click()
            time.sleep(random.uniform(7.5, 10))
        except:
            print("Bouton de connexion introuvable, on reessaye...")
            self.driver.get("https://www.instagram.com")
            time.sleep(random.uniform(5, 7.5))
            self.login(self.username, self.password)

    def login_with_2faCode(self, twoFaCode):
        try:
            twoFaInput = self.driver.find_element(By.XPATH, "//input[@aria-label='Code de sécurité']")
            twoFaInput.send_keys(twoFaCode)
        except Exception as e:
            print(f"Erreur twoFa input, {e}")


        try:
            time.sleep(random.uniform(1, 2))
            self.driver.find_element(By.XPATH, "//button[contains(text(), 'Confirmer')]").click()
        except Exception as e:
            print(f"Erreur twoFa confirm button , {e}")

        time.sleep(random.uniform(12, 15))
        try:
            self.driver.find_element(By.XPATH, "//*[contains(text(), 'une tentative de')]")
            time.sleep(random.uniform(1, 2))
            self.driver.find_element(By.XPATH, "//button[contains(text(), 'moi') and not(contains(text(), 'pas'))]").click()
        except Exception as e:
            print("") #pas de tentative à valider

            # try:
            #     self.driver.find_element(By.XPATH, "//button[contains(text(), 'moi') and not(contains(text(), 'pas'))]").click()
            # except JavascriptException as e:
            #     print(f"\n=======\n=======\n(Error select_next_target): JavaScript error occurred: {e}\n=======\n=======\n")

    def acceptFreeUtilisation(self):
        try:
            time.sleep(random.uniform(5.02, 6.7))
            print("Starting to acceptFreeUtilisation")
            self.driver.find_element(By.XPATH, f"//div[@role='button' and contains(text(), 'Démarrer')]").click()
            time.sleep(random.uniform(1.5, 2.7))
            self.driver.find_element(By.XPATH, f"//div[@role='button' and .//span[contains(text(), 'Utiliser gratuitement')]]").click()
            time.sleep(random.uniform(1.1, 1.7))
            self.driver.find_element(By.XPATH, f"//div[@role='button' and .//span[contains(text(), 'Accepter')]]").click()
            time.sleep(random.uniform(0.9, 1.7))
        except:
            print(end="")

    def disable_notifications(self):
        time.sleep(random.uniform(3, 6))
        self.driver.get("https://www.instagram.com/direct/inbox/")
        time.sleep(random.uniform(7.5, 10))
        self.accept_cookies()
        time.sleep(random.uniform(4, 6))
        try:
            self.driver.find_element(By.XPATH, f"//button[contains(text(), 'Plus tard')]").click()
        except:
            print("Impossible d'accepter les notifications")

    def connect_to_instagram(self):
        try:
            self.driver.get("https://www.instagram.com")
            time.sleep(random.uniform(5, 6))
            self.accept_cookies()
            time.sleep(random.uniform(4, 5))
        except:
            print("Erreur accept cookies")
        try:
            self.login()
            time.sleep(random.uniform(2, 3))
        except:
            print("Erreur login")

        if("two_factor" in self.driver.current_url):
            if(self.twoFaTokens):
                twoFaCode = self.get2faCode(self.twoFaTokens)
                time.sleep(random.uniform(2.12, 3.11))
                self.login_with_2faCode(twoFaCode)
            else:
                print("========\n=======\n Attention, le 2faToken n'est pas disponible, 2fa authentification impossible\n=========\n=========\n")
        else:
            try:
                self.driver.find_element(By.XPATH, f"//*[contains(text(), 'connexion inhabituelle')]")
                print(f"========\n=======\nConnexion avec mail requis pour {self.username}\n=========\n=========\n")
                time.sleep(9000000)
            except:
                print("") #login normal
        time.sleep(random.uniform(12, 15))
        self.acceptFreeUtilisation()
        self.accept_cookies()
        self.removeChallenge()
        print("Connected")

    def removeChallenge(self):
        if "challenge" in self.driver.current_url:
            try:
                ignoreButton = self.driver.find_element(By.XPATH, "//div[@role='button' and .//span[contains(text(), 'Ignorer')]] | //button[.//span[contains(text(), 'Ignorer')]]")
                ignoreButton.click()
            except:
                try:
                    ignoreButtonAria = self.driver.find_element(By.XPATH, "//div[@role='button' and @aria-label='Ignorer']")
                    ignoreButtonAria.click()
                except Exception as e2:
                    print(f"Erreur avec aria-label='Ignorer': {e2}")
            time.sleep(random.uniform(2, 3))

    def getPdp(self, header_element):
        try:
            img_user = header_element.find_element(By.XPATH, "//img[@alt='Modifier la photo de profil']")            
            pdp_url = img_user.get_attribute("src")
        except:
            pdp_url = None
        return pdp_url

    def isPrivate(self):
        return None

    def getAccountInfo(self):
        time.sleep(random.uniform(1, 2))
        header_element = self.driver.find_element(By.XPATH, "//header")
        account_info = header_element.text.split('\n')
        account_info = [info.replace('\u202f', '') for info in account_info]
        
        bio = ""
        nbFollowing = -1
        fullName = None
        for index, info in enumerate(account_info):
            if "suivi(e)s" in info:
                nbFollowing = TextProcessor.convert_to_int(info)
                if (len(account_info) > index+1 and account_info[index+1] is not None):
                    fullName = account_info[index+1]
                    if((len(account_info) > index+2) and (account_info[index+2] is not None)):
                        while len(account_info) > index+2:
                            bio += account_info[index+2] + "\n"
                            index += 1

        nbPublications = -1
        for info in account_info:
            if "publications" in info:
                nbPublications = TextProcessor.convert_to_int(info)
                break

        nbFollowers = -1
        for info in account_info:
            if "followers" in info:
                nbFollowers = TextProcessor.convert_to_int(info)
                break

        PDP = self.getPdp(header_element)

        
        nationnalite = "FR"

        account_info_cleaned = {"nbPublications": nbPublications, "nbFollowers": nbFollowers, "nbFollowing": nbFollowing, "fullName": fullName, "PDP": PDP, "bio": bio, "nationnalite": nationnalite}
        return account_info_cleaned

    def getAccountIsWorking(self):
        time.sleep(random.uniform(1.3, 2.1))
        self.driver.get(f"https://www.instagram.com/{self.username}/")
        time.sleep(random.uniform(4.5, 5))
        self.accept_cookies()
        try:
            self.driver.find_element(By.XPATH, "//a[contains(text(), 'Modifier le profil')]")
            return True
        except:
            False

    def getAccountIsBanned(self):
        time.sleep(random.uniform(4.5, 5))
        if("suspended" or "disabled" in self.driver.current_url):
            print("Account is banned...")
            print(f"URL is: {self.driver.current_url}")
            time.sleep(60)
            return True
        else:
            return False

    def follow_back(self):  
        try:                                           
            heart_btn = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[1]/div/div/div[1]/div/div[2]/div[6]/span/div/a")
        except:
            try:
                heart_btn = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[1]/div/div/div/div/div[2]/div[6]/span/span/div/a")
            except:
                try:
                    heart_btn = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[1]/div/div/div/div/div[2]/div[6]/span/div/a")
                except:
                    try:
                        heart_btn = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/div/div/div/div/div[2]/div[6]/span/span/div/a")
                    except:
                        try:
                            heart_btn = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/div/div/div/div/div[2]/div[6]/span/div/a")
                        except:
                            print("Heart button not accessible")
                            time.sleep(200)
                            return
        heart_btn.click()
        print("Clicked")
        time.sleep(random.uniform(4, 6))
        for i in range(2):
            try:
                scrollbar_container = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[1]/div/div/div[2]/div/div")
            except:
                try:
                    scrollbar_container = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/div/div/div[2]/div/div")
                except:
                    print("Scroll bar container not found...")
                    return
                
            self.driver.execute_script(f"arguments[0].scrollTop = arguments[0].scrollTop + 500", scrollbar_container)

        nbFollowBack = random.uniform(11, 16)
        for _ in range(nbFollowBack):
            try:
                follow_back_btn = self.driver.find_element(By.XPATH, "//button[@type='button' and .//div[contains(text(), 'Suivre')]]")
                follow_back_btn.click()
                self.driver.execute_script(f"arguments[0].scrollTop = arguments[0].scrollTop + 50", scrollbar_container)
            except Exception as e:
                    self.driver.execute_script(f"arguments[0].scrollTop = arguments[0].scrollTop + 500", scrollbar_container)
                    print(e)
            time.sleep(random.uniform(2,8))

    def getPrivacy(self, target):
        self.driver.get(f"https://instagram.com/{target}")
        time.sleep(random.uniform(4, 6))
        privacy = "Public"
        try:
            h2_private = self.driver.find_element(By.XPATH, "//H2[contains(text(), 'Ce compte est privé')]")
            privacy = "Private"
        except Exception as e:
            print(e)
        return privacy
    
    def getAccountIsChallenged(self):
        if("challenge" in self.driver.current_url):
            print("Account is challenged...")
            return True
        else:
            return False

    def test_connexion(self, googleBot=None, mongoDB=None):
        accountInfo = {}
        if(self.getAccountIsWorking()):
            accountIsWorking = "Working"
            accountInfo = self.getAccountInfo()

        elif(self.getAccountIsBanned()):
            accountIsWorking = "Banned"

        elif(self.getAccountIsChallenged()):
            accountIsWorking = "Challenged"  #instagram demands a mail confirmation 

        else:
            accountIsWorking = "Not working"

        if googleBot: googleBot.update_drive_account(self.username, accountIsWorking, accountInfo)
        elif mongoDB: mongoDB.updateInstagramAccount(self.username, accountIsWorking, accountInfo)

        if(accountIsWorking == "Working"):
            print("Working")
            return True
        else:
            print(f"{self.username} test connexion unsuccessfull")
            time.sleep(3600)
            self.driver.quit()
            return False
              
    def inspect_messages(self, nbMessagesSent, mongoDB:MongoDB=None, campaignId=None):

        replies = self.messageCapacities.getReplies()

        for reply in replies[:10]:

            last_reply = self.messageCapacities.getlastReply(reply)

            if(last_reply and self.messageCapacities.userResponded(last_reply)):
            
                messages = self.messageCapacities.getFullConversation(nbMessagesSent, reply)
                target_username = self.messageCapacities.getReplyUsername()
                imageUrl = self.messageCapacities.getProfilPictureUrl()
                if(target_username):
                    if(len(messages) > 1):  #si il y a eu une réponse
                        for message in messages:
                            mongoDB.handleNewMessage(campaignId, self.username, target_username, imageUrl, message)

            time.sleep(random.uniform(0.1, 0.3))

    def reply_to_all(self, campaign, googleBot):

        replies = googleBot.getAllReplies(self.username, campaign)
        for target_username, reply in replies:
            try:
                if(self.sendMessageCapacities.send_reply(target_username, reply)):
                    googleBot.update_replied_on_gg(target_username, reply, campaign)
            except Exception as e:
                print(f"Erreur reply_to_all ou update_replied_on_gg: {e}")
                time.sleep(900000)

    def reply_to_all_mongoDB(self, campaignId, instagramAccountId, mongoDB: MongoDB):
        replies = mongoDB.getFilteredMessages(campaignId, instagramAccountId)

        for reply in replies:
            target_username = reply["contactedUsername"]
            message = reply["body"]
            print(f"\n!!!New reply to send!!!\nTarget: {target_username}\nMessage: {message}\nId: {reply['_id']}\n\n")
            self.sendMessageCapacities.send_reply(target_username, message)
            mongoDB.updateMessageOnInstagram(reply['_id'])

    def get2faCode(self, twoFaTokens):
        #ouvrir nouvel onglet
        self.driver.execute_script("window.open('');")

        # Passer au nouvel onglet ouvert
        time.sleep(random.uniform(1, 2))
        self.driver.switch_to.window(self.driver.window_handles[1])

        self.driver.get("https://2fa.live/")
        time.sleep(random.uniform(3, 4))

        input = self.driver.find_element(By.ID, "listToken")
        input.clear()
        input.send_keys(twoFaTokens)
        time.sleep(random.uniform(1, 2))
        self.driver.find_element(By.ID, "submit").click()

        time.sleep(random.uniform(1, 2))
        output = self.driver.find_element(By.ID, "output")
        output_text = output.get_attribute("value")
        output_text = output_text.split("|")
        
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

        time.sleep(random.uniform(1, 2))
        return output_text[1]

    def readAndReply(self, nbMessagesSent, mongoDB, campaignId, instagramAccountId):
        self.inspect_messages(nbMessagesSent, mongoDB=mongoDB, campaignId=campaignId)
        time.sleep(random.uniform(2, 3))
        self.reply_to_all_mongoDB(campaignId, instagramAccountId, mongoDB)

    def readAndReplyWithGPT(self, nbMessagesSent, mongoDB: MongoDB, campaignId, instagramAccountId, amazonLink):
        replies = self.messageCapacities.getReplies()

        for reply in replies[:10]:

            last_reply = self.messageCapacities.getlastReply(reply)

            if(last_reply and self.messageCapacities.userResponded(last_reply)):
            
                messages = self.messageCapacities.getFullConversation(nbMessagesSent, reply)
                print(messages)
                target_username = self.messageCapacities.getReplyUsername()
                imageUrl = self.messageCapacities.getProfilPictureUrl()
                if(target_username):
                    if(len(messages) > 1):  #si il y a eu une réponse
                        isFirst = True
                        for message in messages:
                            mongoDB.handleNewMessage(campaignId, self.username, target_username, imageUrl, message, isFirst)
                            isFirst = False

                        self.replyWithGPT(mongoDB, target_username, instagramAccountId, campaignId, amazonLink)

            time.sleep(random.uniform(0.1, 0.3))

    def replyWithGPT(self, mongoDB: MongoDB, targetUsername, instagramAccountId, campaignId, amazonLink):
        conversationId, messages = mongoDB.getConversationByTargetUsernameAndCampaignId(targetUsername, campaignId)
        if(messages[-1].get("body").lower() != "merci"):
            messageForGPT = GPTutils.getMessageForGPT(messages, instagramAccountId, amazonLink)
            # print(messageForGPT)
            reply = GPTutils.getReplyFromOpenAI(messageForGPT)
            motifs_a_remplacer = [
                "Utilisateur instagram : ",
                "Utilisateur instagram: ",
                "Vous : ",
                "Vous: "
            ]
            for motif in motifs_a_remplacer:
                if motif in reply:
                    reply = reply.replace(motif, "")

            if(self.sendMessageCapacities.send_reply(targetUsername, reply)):
                mongoDB.addNewSentMessageByConversationId(instagramAccountId, conversationId, reply)


class AccountCapacities:
    def __init__(self, driver, username, password):
        self.driver = driver
        self.username = username
        self.password = password

    def follow_back(self):  
        try:                                           
            heart_btn = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[1]/div/div/div[1]/div/div[2]/div[6]/span/div/a")
        except:
            try:
                heart_btn = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[1]/div/div/div/div/div[2]/div[6]/span/span/div/a")
            except:
                try:
                    heart_btn = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[1]/div/div/div/div/div[2]/div[6]/span/div/a")
                except:
                    try:
                        heart_btn = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/div/div/div/div/div[2]/div[6]/span/span/div/a")
                    except:
                        try:
                            heart_btn = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/div/div/div/div/div[2]/div[6]/span/div/a")
                        except:
                            print("Heart button not accessible")
                            time.sleep(200)
                            return
        heart_btn.click()
        print("Clicked")
        time.sleep(random.uniform(4, 6))
        for i in range(2):
            try:
                scrollbar_container = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[1]/div/div/div[2]/div/div")
            except:
                try:
                    scrollbar_container = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/div/div/div[2]/div/div")
                except:
                    print("Scroll bar container not found...")
                    return
                
            self.driver.execute_script(f"arguments[0].scrollTop = arguments[0].scrollTop + 500", scrollbar_container)

        nbFollowBack = random.uniform(11, 16)
        for _ in range(nbFollowBack):
            try:
                follow_back_btn = self.driver.find_element(By.XPATH, "//button[@type='button' and .//div[contains(text(), 'Suivre')]]")
                follow_back_btn.click()
                self.driver.execute_script(f"arguments[0].scrollTop = arguments[0].scrollTop + 50", scrollbar_container)
            except Exception as e:
                    self.driver.execute_script(f"arguments[0].scrollTop = arguments[0].scrollTop + 500", scrollbar_container)
                    print(e)
            time.sleep(random.uniform(2,8))

    def getPrivacy(self, target):
        self.driver.get(f"https://instagram.com/{target}")
        time.sleep(random.uniform(4, 6))
        privacy = "Public"
        try:
            h2_private = self.driver.find_element(By.XPATH, "//H2[contains(text(), 'Ce compte est privé')]")
            privacy = "Private"
        except Exception as e:
            print(e)
        return privacy

    def getToModifyAccount(self):
        try:
            modify_account_btn = self.driver.find_element(By.XPATH, "//a[@role='link' and contains(text(), 'Modifier le profil')]")
            modify_account_btn.click()
            time.sleep(random.uniform(3, 4))
        except Exception as e:
            print(f"Erreur cliquer sur modifier profil: {e}")
            time.sleep(1000)
        try:
            close_popUp_btn = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/main/div[1]/div/div[1]/div")
            close_popUp_btn.click()
        except:
            print("No popUp to close")

    def getToAdvancedAccount(self):
        try:
            time.sleep(random.uniform(2, 3))
            account_center = self.driver.find_element(By.XPATH, "//a[contains(@href, 'https://accountscenter.')]")
            account_center.click()

            time.sleep(random.uniform(4, 6))
            profil_center = self.driver.find_element(By.XPATH, "//a[contains(@href, '/profiles/')]")
            profil_center.click()

        except Exception as e:
            print(f"Erreur getToAdvancedAccount, {e}")

        x=250
        y=3*64
        actions = ActionChains(self.driver)
        actions.move_by_offset(x, y).click().perform()

        time.sleep(random.uniform(2, 3))

        actions = ActionChains(self.driver)
        actions.move_by_offset(-x, -y).perform()

        # time.sleep(random.uniform(4, 6))
        # profil_center2 = self.driver.find_element(By.XPATH, f"//a[contains(@href, '/profiles/') and contains(@aria-label, '{self.username.lower()}')]")
        # link_to_advanced_profile = profil_center2.get_attribute("href")
        # self.driver.get(link_to_advanced_profile)

    def closeAccountPopUp(self):
        time.sleep(random.uniform(2, 3))
        script = """
            try {
                var svgElement = document.querySelector('svg[aria-label="Fermer"]');
                if (!svgElement) {
                    return 'SVG element not found';
                }

                var targetDiv = svgElement.parentNode.parentNode;
                if (!targetDiv) {
                    return 'Parent div not found';
                }

                targetDiv.click();
                return 'Success';
            } catch (error) {
                return 'Error: ' + error.message;
            }
            """
        try:
            result = self.driver.execute_script(script)
            if result == 'Success':
                new_message_ready = True
        except JavascriptException as e:
            print(f"\n=======\n=======\n(Error close Account Pop Up): JavaScript error occurred: {e}\n=======\n=======\n")
        
    def updatePrivacy(self, privacy):
        try:
        #private account
            content_btn = self.driver.find_element(By.XPATH, "//a[@role='link' and .//span[contains(text(), 'Confidentialité du compte')]]")
            content_btn.click()
            time.sleep(random.uniform(3, 4))
        except:
            content_btn = self.driver.find_element(By.XPATH, "//a[@role='link' and .//span[contains(text(), 'Qui peut voir votre contenu')]]")
            content_btn.click()
            time.sleep(random.uniform(3, 4))

        try:
            input_element = self.driver.find_element(By.XPATH, "//input[@role='switch' and @type='checkbox']")
            input_element.click()
            time.sleep(random.uniform(3, 4))
            if(privacy == "private"):
                confirm_private_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Passer à un compte privé')]")
                confirm_private_btn.click()

            elif(privacy == "public"):
                confirm_private_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Passer à un compte publi')]")
                confirm_private_btn.click()

            time.sleep(random.uniform(3, 4))

        except Exception as e:
            annuler_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Annuler')]")
            annuler_btn.click()
            time.sleep(random.uniform(3, 4))

    def updateBio(self, bio):
        #Bio
        text_area = self.driver.find_element(By.XPATH, "//*[@id='pepBio']")
        text_area.clear()
        pyperclip.copy(bio)
        text_area.send_keys(Keys.CONTROL, 'v')
        time.sleep(random.uniform(3, 4))
        try:
            confirm_bio_btn = self.driver.find_element(By.XPATH, "//div[@role='button' and contains(text(), 'Envoyer')]")
            confirm_bio_btn.click()
            time.sleep(random.uniform(4, 5))
        except Exception as e:
            print(e)

    def clearInput(self):
        try:
            clear_input_btn = self.driver.find_element(By.XPATH, "//div[contains(@aria-label, 'Effacer le texte') and @role='button']")
            clear_input_btn.click()
        except Exception as e:
            print(f"Erreur clear Input : {e}")

    def update_username(self, usernames, names, lock):
        usernameAvailable = False

        time.sleep(random.uniform(4, 6))
        username_settings = self.driver.find_element(By.XPATH, "//a[contains(@href, '/username/')]")
        username_settings.click()

        time.sleep(random.uniform(2, 3))

        while not usernameAvailable:
            with lock:
                username = usernames.pop(0)
            username_input = self.driver.find_element(By.XPATH, "//input[@type='text']")

            text_length = len(username_input.get_attribute('value'))

            for _ in range(text_length):
                username_input.send_keys(Keys.BACK_SPACE)
                time.sleep(random.uniform(0.1, 0.2))

            username_input.send_keys(username)
            time.sleep(random.uniform(1, 2))

            if(username_input.get_attribute("aria-invalid") == "false"):
                usernameAvailable = True
            else:
                with lock:
                    name = names.pop(0)
                    #puis on recommence la boucle

        time.sleep(random.uniform(4, 6))
        self.click_termine_btn()

        DataCapacities.write_old_and_new_usernames(self.username, username)

        time.sleep(random.uniform(4, 6))
        try:
            name_input = self.driver.find_element(By.XPATH, "//input[@aria-label='Retour']")
            name_input.click()
        except Exception as e:
            print(f"Erreur clic btn retour")

    def update_name(self, names, lock):
        with lock:
            name = names.pop(0)

        time.sleep(random.uniform(4, 6))
        name_settings = self.driver.find_element(By.XPATH, "//a[contains(@href, '/name/')]")
        name_settings.click()

        time.sleep(random.uniform(2, 3))

        name_input = self.driver.find_element(By.XPATH, "//input[@type='text']")
        text_length = len(name_input.get_attribute('value'))

        for _ in range(text_length):
            name_input.send_keys(Keys.BACK_SPACE)
            time.sleep(random.uniform(0.1, 0.2))

        name_input.send_keys(name)

        time.sleep(random.uniform(1, 2))
        self.click_termine_btn()

        time.sleep(random.uniform(4, 6))
        try:
            name_input = self.driver.find_element(By.XPATH, "//input[@aria-label='Retour']")
            name_input.click()
        except Exception as e:
            print(f"Erreur clic btn retour")

    def click_termine_btn(self):
        x=370
        y=655

        actions = ActionChains(self.driver)
        actions.move_by_offset(x, y).click().perform()

        actions = ActionChains(self.driver)
        actions.move_by_offset(-x, -y).perform()


class MessageCapacities:
    def __init__(self, driver, username, password):
        self.driver = driver
        self.username = username
        self.password = password

    def getReply(self, i):       
        try:                   
            reply = self.driver.find_element(By.XPATH, f"/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/section/div/div/div/div[1]/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div[{i}]")
            return reply
        except Exception as e:
            try:
                reply =  self.driver.find_element(By.XPATH, f"/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/section/div/div/div/div[1]/div/div[1]/div/div[3]/div/div/div/div/div[2]/div/div[{i}]")
                return reply
            except Exception as e:
                print(e)
                time.sleep(40)

    def scroll_messages(self, scroll_height): 
        try:                                                     
            scrollbar_container = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/section/div/div/div/div[1]/div/div[1]/div/div[3]/div/div/div/div")
            self.driver.execute_script(f"arguments[0].scrollTop = arguments[0].scrollTop + {scroll_height}", scrollbar_container)
        except Exception as e:
            try:
                scrollbar_container = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/section/div/div/div/div[1]/div/div[1]/div/div[2]/div/div/div/div")
                self.driver.execute_script(f"arguments[0].scrollTop = arguments[0].scrollTop + {scroll_height}", scrollbar_container)
            except Exception as e:
                print(f"Erreur scroll_messages: {e}")
                time.sleep(10)

    def userResponded(self, message):
        responded = True
        if("Vous avez retiré" in message[1] or "A aimé" in message[1] or "Vous avez envoyé" in message[1] or "Vous:" in message[1] or "Ce compte ne peut pas recevoir" in message[1] or "wasn't notified about this message" in message[1]): #mettre mieux que Bonjour ! qui peut aussi être utilisé par la cible
            responded = False
        return responded

    def getReplies(self):
        time.sleep(0.8)
        try:
            replies = self.driver.find_elements(By.XPATH, "//div[contains(@aria-label, 'Chats') and contains(@role, 'list')]//div[contains(@style, 'opacity: 1')]")
            return replies
        except Exception as e:
            print(f"Erreur replies1 : {e}")
        try:                                              
            replies_container = self.driver.find_element(By.XPATH, "//div[contains(@aria-label, 'Chats') and contains(@role, 'list')]/div/div/div/div/div")
            replies = replies_container.find_elements(By.XPATH, "./div")

            return replies
        
        except Exception as e:
            print(f"Erreur getReplies: Dms introuvables, {e}")

    def scrollUpConversation(self):
        messages_container = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/section/div/div/div/div[1]/div/div[2]/div/div/div/div/div/div[2]/div/div/div[1]/div/div/div/div/div/div")
        self.driver.execute_script(f"arguments[0].scrollTop = arguments[0].scrollTop - 600", messages_container)

    def getFullConversation(self, nbMessagesSent, reply):
        messages_text = []
        try:                                                              
            conversation_btn = reply.find_element(By.XPATH, "./div")
            conversation_btn.click()

            time.sleep(random.uniform(1, 2))

        except Exception as e:
            print(f"Erreur click conversation (getFullConversation): {e}")
            time.sleep(9000000)

        try:
            #self.scrollUpConversation()
            time.sleep(random.uniform(2.1, 3.77))
            messages_container = self.driver.find_element(By.XPATH, "//div[contains(@aria-label, 'Messages dans la conversation')]")
            messages = messages_container.find_elements(By.XPATH, ".//div[contains(@aria-label, 'Double tap to like')]")

            for message in messages:
                messages_text.append(message.text)

        except Exception as e:
            print(f"Erreur lecture conversation (getFullConversation): {e}")
            time.sleep(9000000)

        return messages_text
       
    def getlastReply(self, reply):
        try:
            last_reply = reply.find_element(By.XPATH, "./div").text.split("\n")
            return last_reply
        except Exception as e:
            print(f"Erreur getlastReply pour {self.username}, {e}")
            return None

    def getReplyUsername(self):
        try:
            time.sleep(random.uniform(2, 3))
            target_username_element = self.driver.find_element(By.XPATH, "//span[contains(text(), '· Instagram')]")
            target_username = target_username_element.text.split(" ")[0]
        except:
            try:
                print(f"{self.username}: getReplyUsername1  -> on essaye avec preceding-sibling::div[1]\n")
                target_username = self.driver.find_element(By.XPATH, "//div[span[text()='Instagram']]/preceding-sibling::div[1]").text          
            except:
                try:
                    print(f"{self.username}: getReplyUsername2  -> on essaye avec XPATH ABSOLU\n")
                    target_username = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/section/div/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[2]/div/div/div[1]/div/div/div/div/div/div/div[1]/div/div[2]/div[3]/span").text.split(" ")[0]
                except:
                    try:                      
                        target_username = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/section/div/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[2]/div/div/div[1]/div/div/div/div/div/div/div[1]/div/div[2]/div[3]/span").text.split(" ")[0]
                    except Exception as e:
                        print(f"=================\n=============\nErreur pour {self.username} -> getReplyUsername : {e}\n=============\n=============\n")
                        target_username = None
        return target_username

    def getFirstReply(self):
        time.sleep(0.8)
        try:                                              
            reply = self.driver.find_element(By.XPATH, "//div[contains(@aria-label, 'Chats') and contains(@role, 'list')]/div/div/div/div[2]/div/div[1]")

            return reply
        
        except Exception as e:
            print(f"")

    def clickConversation(self, message):
        try:
            message.find_element(By.XPATH, "./div").click()
            return True
        except Exception as e:
            print(e)
            return False
        
    def no_more_messages(self):
        try:
            self.driver.find_element(By.XPATH, "//div[span[text()='Aucun message trouvé']]")
            return True
        except:
            return False
            
    def delete_unread_messages(self):
        counter_error = 0

        while not self.no_more_messages():

            if(counter_error > 3):
                print(f"Counter_error > 3 for {self.username}")
                time.sleep(72000)
                return

            if(counter_error > 1):
                self.driver.refresh()
                time.sleep(random.uniform(5, 6))

            try:
                message = self.getFirstReply()
                message_text = message.text.split("\n")
            except:
                counter_error += 1


            if(self.userResponded(message_text)):
                if(self.clickConversation(message)):
                    try:
                        self.deleteConversation()
                        counter_error = 0
                    except:
                        counter_error += 1
                else:
                        counter_error += 1
                        
            elif(self.clickConversation(message)):
                if(self.onlySentMessageInConversation()):
                    try:
                        self.deleteSentMsg()
                    except:
                        counter_error += 1
                    try:
                        self.deleteConversation()
                        counter_error = 0
                    except:
                        counter_error += 1
                    
                else:
                    try:
                        self.deleteConversation()
                        counter_error = 0
                    except:
                        counter_error += 1
            else:
                counter_error += 1

        return

    def onlySentMessageInConversation(self):
        time.sleep(random.uniform(0.4,0.6))
        messages = []
        try:
            messages = self.driver.find_elements(By.XPATH, ".//div[contains(@aria-label, 'Double tap to like')]")
        except Exception as e:
            print(f"Erreur nb messages dans la conversation: {e}")
        if(len(messages) > 1):
            return False
        else:
            return True
        
    def deleteSentMsg(self):
        time.sleep(random.uniform(0.1,0.2))
        try:
            message = self.driver.find_element(By.XPATH, ".//div[contains(@aria-label, 'Double tap to like')]")
            action = ActionChains(self.driver)
            action.move_to_element(message).perform()
        except Exception as e:
            raise
        time.sleep(random.uniform(0.15,0.2))
        try:                                                  
            options_3_petits_pts = self.driver.find_element(By.XPATH, "//div[@aria-haspopup='menu']")
            options_3_petits_pts.click()
        except Exception as e:
            print(f"Erreur click sur les 3 petits points: {e}")
            raise
        time.sleep(random.uniform(0.25,0.35))
        try:
            btn_retirer_msg = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Retirer')]/ancestor::div[1]")
            btn_retirer_msg.click()
        except:
            print("Erreur click sur retirer le msg")
            # time.sleep(3600)
            raise
        time.sleep(random.uniform(0.75, 0.95))
        try:
            btn_confirmer_retirer_msg = self.driver.find_element(By.XPATH, f"//button[contains(text(), 'Retirer')]")
            btn_confirmer_retirer_msg.click()
        except:
            print("Erreur click sur le confirmer supp msg")
            raise
        time.sleep(random.uniform(0.25, 0.35))

    def deleteConversation(self):
        time.sleep(random.uniform(0.35, 0.4))
        try:                                    
            btn_i = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/section/div/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[1]/div/div[2]/div[3]/div")
        except:
            try:
                btn_i = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/section/div/div/div/div[1]/div/div[2]/div/div/div/div/div/div[1]/div/div[2]/div[3]/div")
            except:
                try:
                    btn_i = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/section/div/div/div/div[1]/div/div[2]/div/div/div/div/div/div[1]/div/div[2]/div/div")
                except:
                    try:
                        btn_i = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/section/div/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[1]/div/div[2]/div[3]/div")
                    except:
                        print("Erreur click sur i pr supp le dm !!!!!!!!!!!")
        btn_i.click()

        time.sleep(random.uniform(0.35,0.4))
        try:
            btn_supp_dm = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Supprimer la discussion')]/..")
            btn_supp_dm.click()
        except:
            print("Erreur click sur le bouton supprimer le dm")
        time.sleep(random.uniform(0.35,0.4))
        try:                                               
            btn_supp_dm = self.driver.find_element(By.XPATH, "/html/body/div[7]/div[1]/div/div[2]/div/div/div/div/div/div/div[2]/div/button[1]")
            btn_supp_dm.click()
        except:
            print("Erreur click sur le bouton confirmer suppression du dm")
            time.sleep(5)
        time.sleep(random.uniform(0.35,0.4))

    def getProfilPictureUrl(self):
        try:
            img_user = self.driver.find_element(By.XPATH, "//img[@height='96'][@width='96'][@alt='Avatar utilisateur']")            
            return img_user.get_attribute("src")
        except Exception as e:
            print(f"Erreur récupération profil picture {e}")
            return None


class SendMessageCapacities:
    def __init__(self, driver, username, password):
        self.driver = driver
        self.username = username
        self.password = password

    def get_next_target(self, targets, lock):
        with lock:
            if targets:
                print("Nb cibles restantes :", str(len(targets)))
                return targets.pop(0)
            else:
                return None

    def open_conversation(self):
        #appuyer sur Discuter
        try:
            self.driver.find_element(By.XPATH, "//div[@role='button' and contains(text(), 'Discuter')]").click()
            time.sleep(random.uniform(2.8,5.08))
        except:
            print("Erreur cliquer sur envoyer")

    def write_new_message(self, message, name=None):

        try:
            # Sélectionnez la zone de texte
            text_area = self.driver.find_element(By.XPATH, "//div[@aria-describedby='Écrire un message' or @aria-label='Écrire un message' or @aria-placeholder='Votre message…']") # A CHANGER !!!!!!!!!!!!!!
            text_area.click()
        except:
            try:
                self.refresh()
                time.sleep(random.uniform(2.8, 5.08))
                text_area = self.driver.find_element(By.XPATH, "//div[@aria-describedby='Écrire un message' or @aria-label='Écrire un message' or @aria-placeholder='Votre message…']")
                text_area.click()
            except Exception as e:
                print(f"Erreur pour {self.username} lors du click sur Écrire un message {e}")
                return False
        try: 
            if(name):
                if("xxx" in message):
                    message = message.replace("xxx", name)

            pyperclip.copy(message)
            text_area.send_keys(Keys.CONTROL, 'v')
            time.sleep(random.uniform(1.44,3.11))
            text_area.send_keys(Keys.ENTER)
            
            time.sleep(random.uniform(1, 2))
            return True

        except Exception as e:
            print(f"Erreur pour {self.username} lors de l'envoi du message {e}")
            return False

    def test_write_new_message(self, message):
        #appuyer sur Discuter
        try:
            self.driver.find_element(By.XPATH, "//div[@role='button' and contains(text(), 'Discuter')]").click()
            time.sleep(random.uniform(2.8,5.08))
        except:
            print("Erreur cliquer sur envoyer")
        #entrer le message à envoyer
        try:
            # Sélectionnez la zone de texte
            text_area = self.driver.find_element(By.XPATH, "//div[@aria-describedby='Écrire un message' or @aria-label='Écrire un message']")
            text_area.click()
        except:
            try:
                self.refresh()
                text_area = self.driver.find_element(By.XPATH, "//div[@aria-describedby='Écrire un message' or @aria-label='Écrire un message']")
                text_area.click()
            except Exception as e:
                print(f"Erreur pour {self.username} lors du click sur Écrire un message {e}")
                return False
        try: 
            pyperclip.copy(message)
            text_area.send_keys(Keys.CONTROL, 'v')
            time.sleep(random.uniform(1.44,3.11))
            #text_area.send_keys(Keys.ENTER)
            
            time.sleep(random.uniform(1, 2))
            return True

        except Exception as e:
            print(f"Erreur pour {self.username} lors de l'envoi du message {e}")
            return False

    def send_post(self, target):
        self.driver.get("")
        time.sleep(random.uniform(8,12))
        #cliquer sur partager la publication (icone avion en papier)
        try:
            self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/main/div/div/div/div[2]/div/div[3]/div[1]/div[1]/button").click()
        except:
            print("Bouton trois petits points pour partager la publication introuvable")
            pass

        time.sleep(random.uniform(1.5,2.5))


        try:
            #entrer le nom de la cible à dm
            input_element = self.driver.find_element(By.XPATH, "//input[@autocomplete='off']")
            input_element.send_keys(target)
            time.sleep(random.uniform(1.5,2.5))
        except:
            print("Input pour entrer le nom de la cible introuvable")
            time.sleep(random.uniform(15, 25))
            pass


        try:
            #appuyer sur la div button qui contient un span avec le bon id recherché  ( !!! MARCHE PAS TOUJOURS !!! )
            user_div = self.driver.find_element(By.XPATH, f"//span[contains(text(), '{target}')]/ancestor::div[@role='button']")
            user_div.click()
            #appuyer sur la div tout en haut de la liste
            #user_div = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[1]/div/div[3]/div/div/div[1]")

            time.sleep(random.uniform(2,3))
        except:
            print("Impossible de cliquer sur l'utilisateur de la liste déroulante pour le message")
            pass

        try:
            #appuyer sur suivant
            self.driver.find_element(By.XPATH, "//div[@role='button' and contains(text(), 'Envoyer')]").click()
            time.sleep(random.uniform(4,5))
        except:
            print("Impossible de cliquer sur le bouton pour envoyer le message")
            pass

    def send_reply(self, target_username, reply):
        if(self.click_new_message() and self.select_target(target_username)):
            if(self.write_new_message(reply)):
                return True
        
        #sinon
        return False

    def click_new_message(self):
        time.sleep(random.uniform(3.8,5.4))
        new_message_ready = False
        script = """
            try {
                var svgElement = document.querySelector('svg[aria-label="Nouveau message"]');
                if (!svgElement) {
                    return 'SVG element not found';
                }

                var targetDiv = svgElement.parentNode.parentNode;
                if (!targetDiv) {
                    return 'Parent div not found';
                }

                targetDiv.click();
                return 'Success';
            } catch (error) {
                return 'Error: ' + error.message;
            }
        """

        # Exécution du script et gestion des erreurs dans Selenium
        try:
            result = self.driver.execute_script(script)
            if result == 'Success':
                new_message_ready = True
        except JavascriptException as e:
            print(f"\n=======\n=======\n(Error select_next_target): JavaScript error occurred: {e}\n=======\n=======\n")
        
        return new_message_ready

    def select_target(self, target, div_number=None):

        if(not div_number):
            div_number = 0

        time.sleep(random.uniform(3.8,5.4))
        try:
            input = self.driver.find_element(By.XPATH, "//input[@autocomplete='off']")
            input.send_keys(target)
            time.sleep(random.uniform(4.8, 6.4))
        except Exception as e:
            print(f"{e}\nEntrer l'utilisateur impossible: {self.username}\n")
            time.sleep(9000000)

        try:
            # XPath modifié pour isoler les divs user sous la div avec l'attribut style spécifié
            xpath_string = "//div[@role='dialog']/div/div[@style='transform: translateX(0%) translateZ(1px);']//div[@role='button' and @tabindex='0']"
            user_divs = self.driver.find_elements(By.XPATH, xpath_string)
            self.driver.execute_script("arguments[0].click();", user_divs[div_number+1])
            return True
        except:
            return False

    def refresh(self):
        time.sleep(random.uniform(26, 71))
        self.driver.refresh()
        time.sleep(random.uniform(4.5, 7))
        return True
    
    def getTargetUsername(self):
        try:
            time.sleep(random.uniform(2, 3))
            target_username_element = self.driver.find_element(By.XPATH, "//span[contains(text(), '· Instagram')]")
            target_username = target_username_element.text.split(" ")[0]
        except:
            try:
                print(f"{self.username}: getReplyUsername1  -> on essaye avec preceding-sibling::div[1]\n")
                target_username = self.driver.find_element(By.XPATH, "//div[span[text()='Instagram']]/preceding-sibling::div[1]").text          
            except:
                try:
                    print(f"{self.username}: getReplyUsername2  -> on essaye avec XPATH ABSOLU\n")
                    target_username = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/section/div/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[2]/div/div/div[1]/div/div/div/div/div/div/div[1]/div/div[2]/div[3]/span").text.split(" ")[0]
                except:
                    try:                      
                        target_username = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/section/div/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[2]/div/div/div[1]/div/div/div/div/div/div/div[1]/div/div[2]/div[3]/span").text.split(" ")[0]
                    except Exception as e:
                        print(f"=================\n=============\nErreur pour {self.username} -> getTargetUsername : {e}\n=============\n=============\n")
                        target_username = None
        return target_username
    
    def correct_target(self, target):
        if(self.getTargetUsername() == target):
            self.open_conversation()
            return True
        else: 
            return False

    def send_message(self, target, targets, message, lock, name=None):
        reload = False
        nbChangedTarget = 0
        if(name is None):
            name=None

        div_number = 0

        while True:
            if(reload):
                self.driver.get("https://www.instagram.com/direct/inbox/")
                time.sleep(random.uniform(3.8, 5.4))
                reload = False
            
            if(self.click_new_message()):
                if(self.select_target(target, div_number)):
                    if(self.correct_target(target)):
                        if(self.write_new_message(message, name)):
                            return True
                        else:
                            nbChangedTarget+=1
                            target = self.get_next_target(targets, lock)
                    else:
                        div_number += 1    

                elif(self.refresh() and self.click_new_message() and self.select_target(target, div_number)):
                    if(self.correct_target(target)):
                        if(self.write_new_message(message)):
                            return True
                        else:
                            print("Erreur envoi message")
                            target = self.get_next_target(targets, lock)
                            nbChangedTarget+=1
                    else:
                        div_number += 1    

                elif(nbChangedTarget <= 3):
                    target = self.get_next_target(targets, lock)
                    nbChangedTarget+=1
                    if(not target):
                        print("No more targets")
                        return False
                else:
                    print(f"\n=====\n=====\n=====\n=====\n=====\nTarget list unavailable\n=====\n=====\n=====\n=====\n=====\n")
                    time.sleep(9000000)
                    #faire qlq chose -> se déco reco par exemple

            else:
                if(reload):
                    print(f"\n=====\nClick new message impossible, even after reloading pour {self.username}\n=====\n")
                    time.sleep(3600)
                    self.driver.quit()
                    return False 
                else:
                    reload = True
                    time.sleep(random.uniform(2, 3))

    def test_send_message(self, target, targets, message, lock):
        reload = False
        nbChangedTarget = 0

        while True:
            if(reload):
                self.driver.get("https://www.instagram.com/direct/inbox/")
                time.sleep(random.uniform(3.8, 5.4))
            
            if(self.click_new_message()):
                if(self.select_target(target)):
                    if(self.test_write_new_message(message)):
                        return True
                    else:
                        print("Erreur envoi message")
                        return False
                    
                elif(self.refresh() and self.click_new_message() and self.select_target(target)):
                    if(self.test_write_new_message(message)):
                        return True
                    else:
                        print("Erreur envoi message")
                        return False
                    
                elif(nbChangedTarget <= 3):
                    target = self.get_next_target(targets, lock)
                    nbChangedTarget+=1
                    if(not target):
                        print("No more targets")
                        return False  
                else:
                    print(f"\n=====\n=====\n=====\n=====\n=====\nTarget list unavailable\n=====\n=====\n=====\n=====\n=====\n")
                    time.sleep(9000000)
                    #faire qlq chose -> se déco reco par exemple

            else:
                if(reload):
                    print(f"\n=====\nClick new message impossible, even after reloading pour {self.username}\n=====\n")
                    time.sleep(3600)
                    self.driver.quit()
                    return False 
                else:
                    reload = True
                    time.sleep(random.uniform(2, 3))


class DeleteMessageCapacities:
    def __init__(self, driver):
        self.driver = driver

    def click_1er_msg(self):
        try:                                       
            message_div = self.driver.find_element(By.XPATH, f"/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/div/div/div/div[1]/div/div[1]/div/div[3]/div/div/div/div/div[2]/div/div[1]")
            message_div.click()
        except Exception as e:
            print("Erreur pour trouver et cliquer sur le 1er msg"+str(e))
        time.sleep(1)

    def selection_dm(self, i, nb_msg_deleted):
        message_div = self.driver.find_element(By.XPATH, f"/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/div/div/div/div[1]/div/div[1]/div/div[3]/div/div/div/div/div[2]/div/div[{i-nb_msg_deleted}]/div")  
        message_div.click()
        return True
    
    def selection_suppression_dm(self, i, nb_msg_deleted):
        message_div = self.driver.find_element(By.XPATH, f"/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/div/div/div/div[1]/div/div[1]/div/div[3]/div/div/div/div/div[2]/div/div[{i-nb_msg_deleted}]")
        span_element = message_div.find_elements(By.XPATH, ".//span[contains(text(), 'Vous avez retiré un message')]")
        if(span_element):  
            message_div.click()
            return True

    def delete_dm(self):
        time.sleep(random.uniform(0.35,0.4))
        try:
            btn_i = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/div/div/div/div[1]/div/div[2]/div/div/div/div/div/div[1]/div/div[2]/div[3]/div")
            btn_i.click()
        except:
            print("Erreur click sur le bouton i des options du dm")
        time.sleep(random.uniform(0.35,0.4))
        try:
            btn_supp_dm = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Supprimer la discussion')]/..")
            btn_supp_dm.click()
        except:
            print("Erreur click sur le bouton supprimer le dm")
        time.sleep(random.uniform(0.35,0.4))
        try:                                            
            btn_supp_dm = self.driver.find_element(By.XPATH, "/html/body/div[6]/div[1]/div/div[2]/div/div/div/div/div/div/div[2]/div/button[1]")
            btn_supp_dm.click()
        except:
            print("Erreur click sur le bouton confirmer suppression du dm")
            time.sleep(5)
        time.sleep(random.uniform(0.35,0.4))

    def delete_unread_messages(self):

        self.driver.get("https://www.instagram.com/direct/new/")
        time.sleep(random.uniform(5, 7.5))
        
        try:
            message_container = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/div/div/div/div[1]/div/div[1]/div/div[3]/div/div/div/div/div[2]/div")
            scrollbar_container = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/div/div/div/div[1]/div/div[1]/div/div[3]/div/div/div/div")
        except:
            print("Messages container not found")

        time.sleep(random.uniform(0.5, 0.7))

        # messages_divs = [] # Initialiser ici

        print("Scroll vers le bas")
                

        #while True:
        for i in range(12):
            try:
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 200", scrollbar_container)
            except:
                print("Chargement...")
                pass
            time.sleep(random.uniform(0.012, 0.22))

        self.click_1er_msg()

        nb_dm_deleted=0
        i=1
        time.sleep(5)
        try:
            while True:
                dm_to_be_deleted = self.selection_dm(i, nb_dm_deleted)
                if(dm_to_be_deleted):
                    print(f"Le message {i} va être supprimé dans 1s")
                    time.sleep(random.uniform(0.8, 1.2))
                    try:
                        self.delete_dm()
                        time.sleep(random.uniform(0.7, 0.98))
                        nb_dm_deleted+=1
                        print(nb_dm_deleted)
                        i+=1
                    except:
                        print("Erreur dans le bloc try")
                        pass

        except Exception as e:
            print(f"Erreur delete unread: {e}")
            self.delete_unread_messages() 


class ScrappingCapacities:
    def __init__(self, driver, username, password):
        self.driver = driver
        self.username = username
        self.password = password

    def go_to_next_target(self, nextTarget):
        self.driver.get(f"https://www.instagram.com/{nextTarget}/")
        time.sleep(random.uniform(3, 5))
    
    def display_similar_accounts(self):
        print("Displaying similar accounts...")
        time.sleep(random.uniform(1, 2))
        header_element = self.driver.find_element(By.XPATH, "//header")
        try:                                                      
            similar_accounts_btn = header_element.find_element(By.XPATH, ".//div[@style='width: 34px;']/div")
            similar_accounts_btn.click()
        except Exception as e:  
            print(f"Erreur click sur afficher les comptes similaires: {e}")   
            time.sleep(1000)                                            
            # try:
            #     similar_accouts_btn = driver.find_element(By.XPATH, f"/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/div[1]/div[1]/div/div[2]/div")
            #     similar_accouts_btn.click()
            # except Exception as e:
            #     print("Erreur click sur afficher les comptes similaires")
            #     time.sleep(300)

        time.sleep(random.uniform(2, 3))
        try:
            voir_tout = self.driver.find_element(By.XPATH, "//a[./span[text()='Voir tout']]")
            voir_tout.click()
        except Exception as e:
            print(f"Erreur click sur voir tout: {e}")

    def get_similar_accounts(self):
        time.sleep(random.uniform(1, 2))
        accountsRemaining = True
        usernames = []          

        try:                                                 
            accounts_container = self.driver.find_element(By.XPATH, "//div[@style='height: auto; overflow: hidden auto;']")
            parent_div = accounts_container.find_element(By.XPATH, "./..")
        except Exception as e:
            print(f"Erreur container similar_accounts: {e}")
            time.sleep(1000)

        try:
            #accounts_container_scroll = accounts_container.find_element(By.XPATH, "./..")
            for _ in range(10):
                self.driver.execute_script("arguments[0].scrollTop += 500;", parent_div)
                time.sleep(random.uniform(0.2, 0.45))
        except:
            print("Scroll container does not work...")
            time.sleep(2)

                  
        try:                                  
            containers = accounts_container.find_elements(By.XPATH, f"./div/div")
            print(len(containers))
        except Exception as e:
            print(f"Erreur get_similar_accounts {e}")   

        for container in containers :
            try:
                follower1_link = container.find_element(By.XPATH, ".//a").get_attribute("href")
                usernames.append(follower1_link.split('/')[-2])
                print(follower1_link.split('/')[-2])
            except Exception as e:
                print(f"Erreur pour récupérer l'username du similar accounts: {e}")


        return usernames

    def accountIsFrench(self):
        french = False

        # x = 792.0
        # y = 54.0
        # actions = ActionChains(driver)
        # actions.move_by_offset(x, y).context_click().perform()        
        try:
            options = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/div[1]/div[2]/div")
        except: 
            options = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[2]/div/div[2]/section/main/div/header/section[2]/div/div/div[3]/div")
        
        
        
        if("Options" not in options.get_attribute("outerHTML")):
            print("Not options...")
            try:
                options = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/div[1]/div[3]/div")
            except:
                try:
                    options = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/div[1]/div[3]/div")
                except:
                    print("Erreur options")
                    return
    
        options.click()
        time.sleep(random.uniform(1.7, 2))
        a_propos = self.driver.find_element(By.XPATH, "//button[contains(text(), 'À propos de ce compte')]")
        a_propos.click()
        time.sleep(random.uniform(2, 3))

        try:
            france = self.driver.find_element(By.XPATH, "//div[@role='dialog'][.//text()='France']")
            print("FRANCAIS !")
            french = True
        except Exception as e:                      
            print("Pas Français")                           

        try:                                        
            fermer_btn = self.driver.find_element(By.XPATH, "/html/body/div[6]/div[1]/div/div[2]/div/div/div/div/div[2]/div/button")
            fermer_btn.click()
        except:
            fermer_btn = self.driver.find_element(By.XPATH, "//button[text()='Fermer']")
            fermer_btn.click()


        return french

    def accountLooksGood(self):
        accountLooksGood = False

        time.sleep(random.uniform(4, 5))
        header_element = self.driver.find_element(By.XPATH, "//header")
        account_info = header_element.text.lower().split('\n')
        account_info = [info.replace('\u202f', '') for info in account_info]

        key_words = [
            "vêtement",
            "vêtements",
            "vetement",
            "vetements",
            "seconde main",
            "chaussure",
            "shoes"
            "chaussures",
            "sur-mesure",
            "accessoires",
            "clothe",
            "clothes",
            "textile",
            "pret-a-porter",
            "prêt-à-porter",
            "tenues",
            "denim",
            " bag ",
            "dress",
            " sac "
            
        ]
            # collection
            # "store",
            # "magasin",
            # "boutique",
            # "commerce",
            # "commerçant",
            # "vente",
            # "créations",
            # "mode",
            # "cbd",
            # "accessoires",
            # "boutique",
            # "boutique concept",
            # "bagasin conceptuel",
            # "point de vente",
            # "marchand",
            # "vendeur",
            # "Vente",
            # "huiles",
            # "crèmes",
            # "fleurs",
            # "commerçant",
            # "sur-mesure",
            # "sur mesure",
            # "bar à jeux",
            # "café ludique",
            # "artisan",
            # "artiste",
            # "atelier",
            # "créateur",
            # "décoration",
            # "décorateur",
            # "décoratrice",
            # "créatrice",
            # "conceptrice",
            # "concepteur",
            # "fabrication",
            # "conceptions",
            # "artisane",
            # "bijoux",
            # "dépôt-vente",
            # "seconde main",
            # "occasion",
            # "chaussure",
            # "chaussures",
            # "local",
            # "locaux",
            # "fait main",
            # "artisanal",
            # "confectionné à la main",
            # "fabriqué à la main",
            # "chanvre",
            # "vapote",
            # "vapotage",
            # "cigarette électronique",
            # "vapoter",
            # "huiles CBD",
            # "shop"

        avoid_words = [
            "bijoux",
            "blog",
            "communauté",
            "joaillerie",
            "vidéos"
        ]
        mot_trouve = any(word in line for word in key_words for line in account_info)
        mot_a_ne_pas_trouve = any(word in line for word in avoid_words for line in account_info)

        for info in account_info:
            if "followers" in info:
                nbFollowers = TextProcessor.convert_to_int(info)
                break

        if(mot_trouve and not mot_a_ne_pas_trouve and nbFollowers > 20000 and self.accountIsFrench()):
            mots_trouves = set()
            for line in account_info:
                for word in key_words:
                    if word in line:
                       mots_trouves.add(word)
            print(mots_trouves)
            accountLooksGood = True
            print("ACCOUNT IS SELECTED!")
        return accountLooksGood

    def get_account_info(self):
        time.sleep(random.uniform(2, 3))
        header_element = self.driver.find_element(By.XPATH, "//header")
        account_info = header_element.text.split('\n')

        account_info = [info.replace('\u202f', '') for info in account_info]
        name = ""
        nbFollowing = -1
        for index, info in enumerate(account_info):
            if "suivi(e)s" in info or "suivi(e)" in info:
                nbFollowing = TextProcessor.convert_to_int(info)
                if (len(account_info) > index+1 and account_info[index+1] != None):
                    name = account_info[index+1]
                    if((len(account_info) > index+2) and (account_info[index+2] is not None)):
                        bio = account_info[index+2]

        nbPublications = -1
        for info in account_info:
            if "publications" in info or "publication" in info:
                nbPublications = TextProcessor.convert_to_int(info)
                break

        nbFollowers = -1
        for info in account_info:
            if "followers" in info or 'follower' in info:
                nbFollowers = TextProcessor.convert_to_int(info)
                break

        url_link = ""
        for info in account_info:
            if ".fr" in info or ".com" in info or ".org" in info or ".linktr.ee" in info or ".net" in info:
                url_link = info
                break

        account_info_cleaned = {"nbPublications": nbPublications, "nbFollowers": nbFollowers, "nbFollowing": nbFollowing, "fullName": name, "bio": bio,"url_link": url_link}
        return account_info_cleaned

    def scrap_target(self, target, googleBot, base_directory_path):
        self.go_to_next_target(target)
        if(self.accountLooksGood()):
            account_info_cleaned = self.get_account_info()
            googleBot.update_google_sheet(target, account_info_cleaned)
            DataCapacities.add_to_selected_targets(target, base_directory_path)
        else:
            DataCapacities.add_scrapped_target(target, base_directory_path)

    def accountStillExists(self):
        if(self.driver.find_elements(By.XPATH, "//header")):
            return True
        else:
            return False

    def scraping_followers(self, instagram_account, numbersOfAccountsToScrap, campaignId, mongoDB: MongoDB):
        self.driver.get(f"https://instagram.com/{instagram_account}/")
        time.sleep(random.uniform(4, 5))


        self.driver.find_element(By.XPATH, "//a[contains(@href, '/followers/')]").click()
        
        time.sleep(random.uniform(4, 5))
        
        xpath = "//div[@role='dialog']/div[@style='display: flex; flex-direction: column; height: 100%; max-width: 100%;']"
        followers_container = self.driver.find_element(By.XPATH, xpath)

        if(followers_container.find_elements(By.XPATH, ".//span[text()='seul(e)']")):
            return False
        

        followers_scrollbar_container = followers_container.find_element(By.XPATH, ".//div[@style='max-height: 400px; min-height: 200px;']/div[3]") #/div[div[@style='height: auto; overflow: hidden auto;']]
        followers_divs = followers_scrollbar_container.find_element(By.XPATH, "./div[1]/div")

        followers = followers_divs.find_elements(By.XPATH, "./div")

        print(f"Number of followers retrieved: {len(followers)}")
        
        for _ in range(round(numbersOfAccountsToScrap / 3)):
            self.driver.execute_script(f"arguments[0].scrollTop = arguments[0].scrollTop + 1200", followers_scrollbar_container)
            time.sleep(random.uniform(1.2, 3.1))

        followers = followers_divs.find_elements(By.XPATH, "./div")

        usernames = []
        for follower in followers:
            try:
                follower1_link = follower.find_element(By.XPATH, ".//a").get_attribute("href")
                usernames.append(follower1_link.split('/')[-2])
                print(follower1_link.split('/')[-2])
            except Exception as e:
                print(f"Erreur pour récupérer l'username du similar accounts: {e}")

        print(f"Number of followers retrieved: {len(followers)}")
        mongoDB.addTargets(usernames, "66ed5167621d248013c7b5f0")