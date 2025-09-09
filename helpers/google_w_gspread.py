
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys
sys.path.insert(0, "C:/Users/thoma/OneDrive/Documents/Socialify/BOT")
from helpers.mongodb import MongoDB
from datetime import datetime, timedelta
import pandas as pd


class GoogleBot:
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('google_credentials.json', scope)
        gs_client = gspread.authorize(creds)
        self.MongoDB = MongoDB()

        self.campaignDetails = gs_client.open('Feuille Finale').worksheet('Campagnes Details')
        self.accountDetails = gs_client.open('Feuille Finale').worksheet('Comptes Details')

    def getAccount(self, username):
        account = list(self.MongoDB.db.InstagramAccount.find({ "username": username }))
        
        print(account)

    def writeAllAccounts(self):
        pipeline = [
            {
                "$lookup": {
                    "from": "SentMessage",
                    "localField": "_id",
                    "foreignField": "instagramAccountId",
                    "as": "sentMessages"
                }
            },
            {
                "$addFields": {
                    "sentMessagesCount": {"$size": "$sentMessages"}
                }
            },
            {
                "$project": {
                    "sentMessages": 0  # Enlève le champ 'sentMessages' pour ne pas retourner tous les messages
                }
            }
        ]
        accounts = list(MongoDB().db.InstagramAccount.aggregate(pipeline))
        rows = []
        for account in accounts:
            row = [
                account.get('username'),
                account.get('status'),
                account.get('campaignName'),
                account.get('sentMessagesCount'),
                account.get('accountOrigin'),
                account.get('accountMethod'),
                str(account.get('updatedAt')),
                account.get('password'),
                account.get('mail'),
                account.get('mailPassword'),
                account.get('followers'),
                account.get('following'),
                account.get('publications'),
                account.get('bio'),
                account.get('public'),
                account.get('twoFaTokens'),
            ]
            rows.append(row)

        self.accountDetails.update(range_name=f'D7:S{7+len(rows)-1}', values=rows, value_input_option='USER_ENTERED')

    def getSentMessagesByCampaignId(self, campaignId):
        # Déterminer les dates pour les 7 derniers jours
        fin = datetime.now()
        debut = fin - timedelta(days=6)
        dates_range = pd.date_range(start=debut, end=fin).tolist()

        # Pipeline d'agrégation pour filtrer par campaignId et compter les messages par jour
        pipeline = [
            {
                '$match': {
                    'campaignId': campaignId,
                    'createdAt': {'$gte': debut}
                }
            },
            {
                '$group': {
                    '_id': {
                        'jour': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$createdAt'}}
                    },
                    'count': {'$sum': 1}
                }
            },
            {
                '$sort': {'_id.jour': 1}
            }
        ]

        # Exécution de la requête d'agrégation
        resultats = list(self.MongoDB.db.SentMessage.aggregate(pipeline))
        
        # Convertir les résultats en dictionnaire pour un accès facile
        counts_by_day = {resultat['_id']['jour']: resultat['count'] for resultat in resultats}
        
        # Générer les comptes pour chaque jour, y compris les jours sans messages
        counts_for_7_days = [counts_by_day.get(day.strftime('%Y-%m-%d'), 0) for day in dates_range]
        
        return counts_for_7_days
        
    def getOnGoingCampaignIds(self):
        campaigns = list(self.MongoDB.db.Campaign.find({"status": "Ongoing"}, {"_id": True, "campaignName": True, "nbMessages": True, "createdAt": True}))
        return campaigns

    def getTotalSendByCampaignId(self, campaignId):
        return self.MongoDB.db.SentMessage.count_documents({'campaignId': campaignId})

    def getTotalRepliesByCampaignId(self, campaignId):
        return self.MongoDB.db.Conversation.count_documents({'campaignId': campaignId})

    def WriteCampaignsOverview(self):
        campaignsOverview = []
        campaigns = self.getOnGoingCampaignIds()
        print(campaigns)

        for campaign in campaigns:
            campaignOverview = [campaign.get('campaignName'), campaign.get('status'), campaign.get('createdAt').strftime('%d/%m/%Y'), None, campaign.get('nbMessages'), None]
            campaignOverview += [self.getTotalSendByCampaignId(campaign["_id"])]
            campaignOverview += [None, None]
            campaignOverview += self.getSentMessagesByCampaignId(campaign["_id"])
            campaignOverview += [self.getTotalRepliesByCampaignId(campaign["_id"])]

            campaignsOverview.append(campaignOverview)
        

        self.campaignDetails.update(range_name=f'D8:T{8+len(campaignsOverview)-1}', values=campaignsOverview, value_input_option='USER_ENTERED')


GoogleBot().writeAllAccounts()


# # Define the scope
# scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# # Authenticate using the service account
# creds = ServiceAccountCredentials.from_json_keyfile_name('google_credentials.json', scope)
# gs_client = gspread.authorize(creds)

# # List the first few available spreadsheets to test connectivity and authentication
# try:
#     available_sheets = gs_client.openall()  # Adjust limit as needed
#     print("Available sheets:")
#     for sheet in available_sheets:
#         print(sheet.title)
# except Exception as e:
#     print("An error occurred:", e)