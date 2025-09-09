import sys
import os
import random
import time
import datetime
import concurrent.futures
import threading
sys.path.insert(0, "C:/Users/thoma/OneDrive/Documents/Socialify/BOT")

from helpers.utils import DataCapacities
from helpers.instagram import InstagramWorker
from helpers.google import GoogleBot



campaign = "..."
working_accounts_sheet_name = "..."
spreadsheet_id = "..." 



def main(totalTime, nbConnections, nbMessagesSent):
    base_directory_path = os.path.dirname(__file__)


    googleBot = GoogleBot(working_accounts_sheet_name, spreadsheet_id)
    accounts = googleBot.getAccountsByCampaign(campaign)
    print(accounts)

    DataCapacities.garder_seulement_les_targets_pas_encore_contactees(base_directory_path)
    targets = DataCapacities.getTargets(base_directory_path)

    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        lock = threading.Lock()
        futures = []
        j=1
        for username, password, _ in accounts:
            future = executor.submit(InstagramWorker.worker_send_messages, campaign, username, password, targets, lock, totalTime, nbMessagesSent, googleBot, base_directory_path, nbConnections)
            futures.append(future)
            time.sleep(random.uniform(8, 72))
            
main(8, 3, 1)
