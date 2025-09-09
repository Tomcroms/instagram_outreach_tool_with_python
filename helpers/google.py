from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
import datetime
import random
import time

class GoogleBot:
    def __init__(self, working_accounts_sheet_name, spreadsheet_id):
        self.credentials_path = "C:/Users/thoma/OneDrive/Documents/Socialify/BOT/google_credentials.json"
        self.creds = Credentials.from_service_account_file(self.credentials_path, scopes=['https://www.googleapis.com/auth/spreadsheets'])
        
        self.working_accounts_sheet_name = working_accounts_sheet_name
        self.working_accounts_spreadsheet_id = "1WfR9DOTSBiS972ggOBWgDgnzrGOJ62c2n-SiMtaVvj8"

        self.spreadsheet_id = spreadsheet_id

    def getAccounts(self, start, end):
        service = build('sheets', 'v4', credentials=self.creds)

        range_name = f"{self.working_accounts_sheet_name}!A{start}:Q{end}"

        # Lire le contenu des cellules
        result = service.spreadsheets().values().get(
            spreadsheetId=self.working_accounts_spreadsheet_id,
            range=range_name
        ).execute()

        # Extraire les valeurs
        values = result.get('values', [])

        # Construire la liste accounts
        accounts = [(row[0], row[1], row[15], row[2]) for row in values if len(row) >= 15 and row[2]]

        # Afficher la liste accounts
        return accounts

    def getAccountsByCampaign(self, campaign):
        service = build('sheets', 'v4', credentials=self.creds)

        range_name = f"{self.working_accounts_sheet_name}!A:Q"

        # Read the cell contents
        result = service.spreadsheets().values().get(
            spreadsheetId=self.working_accounts_spreadsheet_id,
            range=range_name
        ).execute()

        # Extract the values
        values = result.get('values', [])

        # Build the list of accounts for the specified campaign
        accounts = [(row[0], row[1], row[15]) for row in values if len(row) >= 15 and row[2] == campaign]

        random.shuffle(accounts)

        # Return the list of accounts
        return accounts

    def find_user_row(self, username):
        service = build('sheets', 'v4', credentials=self.creds)
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=self.working_accounts_spreadsheet_id,
                range=f"{self.working_accounts_sheet_name}!A:A"
            ).execute()

            rows = result.get('values', [])

            # Rechercher le nom d'utilisateur dans les lignes récupérées.
            for idx, row in enumerate(rows):
                if row and row[0] == username:
                    return idx + 1  # Les indices de ligne dans Sheets commencent à 1, pas à 0

        except Exception as e:
            print(f"Erreur lors de la recherche du nom d'utilisateur {username} : {e}")

        return None

    def update_sheet_for_test_connection(self, row_number, values, color):
        service = build('sheets', 'v4', credentials=self.creds)
        try:
            # Préparez la plage et les valeurs
            range_name = f"{self.working_accounts_sheet_name}!D{row_number}:L{row_number}"
            body = {'values': values}
            
            # Mise à jour des valeurs
            service.spreadsheets().values().update(
                spreadsheetId=self.working_accounts_spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()

            # Préparez la mise à jour de la couleur de fond
            red, green, blue = color
            requests = [{
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': row_number - 1,
                        'endRowIndex': row_number,
                        'startColumnIndex': 7,
                        'endColumnIndex': 8
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {
                                'red': red,
                                'green': green,
                                'blue': blue
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor)'
                }
            }]

            # Exécutez la demande de mise à jour de la couleur de fond
            service.spreadsheets().batchUpdate(spreadsheetId=self.working_accounts_spreadsheet_id, body={'requests': requests}).execute()

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")

    def update_drive_account(self, username, accountIsAccessible, accountInfo):
        service = build('sheets', 'v4', credentials=self.creds)
        if not service:
            print("GoogleBot: service is not set properly")
            return False

        currentDate = datetime.datetime.now().strftime('%Y-%m-%d  %H:%M')
        values = [
            [
                accountInfo.get("nbFollowers", None),
                accountInfo.get("nbFollowing", None),
                accountInfo.get("nbPublications", None),
                accountInfo.get("fullName", None),
                accountIsAccessible,
                currentDate,
                accountInfo.get("PDP", None),
                accountInfo.get("bio", None),
                accountInfo.get("nationnalite", None),
            ]
        ]

        color_map = {
            "Working": (0, 1, 0),
            "Not working": (1, 0.207, 0),
            "Banned": (1, 0, 0)
        }
        red, green, blue = color_map.get(accountIsAccessible, (0, 0, 0))

        row_number = self.find_user_row(username)
        if row_number is None:
            print(f"Username {username} not found.")
            return False

        self.update_sheet_for_test_connection(row_number, values, (red, green, blue))

    def getOriginAnMethod(self):
        return ""

    def getCampaignMessage(self, campaign):
        service = build('sheets', 'v4', credentials=self.creds)
        try: 
            sheet_name = 'Campaigns'

            range_name = f"{sheet_name}!A:C"

            result = service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()

            values = result.get('values', [])

            for row in (values):
                if row[0] and row[2] and row[2] == campaign:
                    return row[0]
            
            return None
        except Exception as e: 
            print(f"Erreur getCampaignMessage: {e}")

    def getAllReplies(self, username, campaign):
        service = build('sheets', 'v4', credentials=self.creds)
        sheet_name = 'Leads'

        range_name = f"{sheet_name}!A:G"

        # Lire le contenu des cellules
        result = service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range_name
        ).execute()

        # Extraire les valeurs
        values = result.get('values', [])

        # Construire la liste accounts
        valid_combinations = []
        for row in values:
            if len(row) > 6 and row[6] and row[2] == username and row[3] == campaign:  # Vérifie si la colonne L (index 11) n'est pas vide
                target_username = row[0]  # Username se trouve dans la colonne A
                reply = row[6]    # Réponse se trouve dans la colonne L
                valid_combinations.append((target_username, reply))

        # Afficher la liste accounts
        return valid_combinations   

    def update_replied_on_gg(self, target_username, reply, campaign):
        service = build('sheets', 'v4', credentials=self.creds)
        sheet_name = 'Leads'

        range_name = f"{sheet_name}!A:G"

        # Lire le contenu des cellules
        result = service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range_name
        ).execute()

        # Extraire les valeurs
        values = result.get('values', [])

        # Trouver la cellule à modifier
        for i, row in enumerate(values):
            if len(row) > 6 and row[0] == target_username and row[3] == campaign:
                # Construire la nouvelle valeur
                reply = reply.replace("\n", " ")
                new_value = row[4] + "\n\n" + "Vous:  " + reply

                reply_date = datetime.datetime.now().date().isoformat()
                # Préparer la mise à jour
                update_range = f"{sheet_name}!E{i+1}:G{i+1}"
                value_range_body = {
                    "values": [[new_value, reply_date, ""]]
                }

                # Mettre à jour la cellule
                request = service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id, 
                    range=update_range, 
                    valueInputOption="USER_ENTERED", 
                    body=value_range_body
                )
                request.execute()

                break

    def isMessageOnGG(self, username, campaign, message):
        service = build('sheets', 'v4', credentials=self.creds)
        messageIsOnGG = False

        sheet_name = 'Leads'

        # Spécifiez la plage de cellules pour la lecture, ici seulement la colonne A
        range_name = f"{sheet_name}!A:E"

        try:
            # Lire le contenu des cellules
            result = service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()

            # Extraire les valeurs
            values = result.get('values', [])

            for row in values:
                if(len(row) > 4 and row[0] == username and row[3] == campaign and message in row[4]):
                    messageIsOnGG = True
                    break
        except Exception as e:
            print(f"\n======\n======\nErreur isMessageOnGG : {e}\n======\n======\n")
            time.sleep(9000000)

        # Afficher la liste accounts
        return messageIsOnGG

    def firstTimeOnGG(self, target_username, campaign):
        service = build('sheets', 'v4', credentials=self.creds)
        firstMessage = True

        sheet_name = 'Leads'

        # Spécifiez la plage de cellules pour la lecture, ici seulement la colonne A
        range_name = f"{sheet_name}!A:E"

        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
        except Exception as e:
            print(f"\n======\n======\nErreur firstTimeOnGG {e}\n======\n======\n")
            time.sleep(8000000)
        # Extraire les valeurs
        values = result.get('values', [])

        # Construire la liste accounts
        for row in values:
            if(len(row) > 4 and row[0] == target_username and row[3] == campaign):
                firstMessage = False
                break

        return firstMessage   

    def add_first_reply_to_gg(self, target_username, campaign, message, username):
        service = build('sheets', 'v4', credentials=self.creds)
        #sheetName
        sheet_name = 'Leads'

        link = "https://www.instagram.com/"+target_username
        reply_date = datetime.datetime.now().date().isoformat()
        message = f"{target_username}:  " + message


        values = [[target_username, link, username, campaign, message, reply_date]]

        body = {
        'values': values
        }
        range_name = f"{sheet_name}!A:A"

        try:
            sheet = service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                body=body,
                valueInputOption='RAW'  # Les valeurs sont écrites telles quelles
            ).execute()

        except Exception as e:
            print(f"Erreur drive add_first_reply_to_gg: {e}")
 
    def add_new_reply_to_gg(self, target_username, campaign, message):
        service = build('sheets', 'v4', credentials=self.creds)
        sheet_name = 'Leads'

        # Rechercher la ligne correspondante
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!A:E"
            ).execute()
            values = result.get('values', [])

            # Trouver l'index de la ligne avec "AAA" dans la colonne A
            row_index = None
            for i, row in enumerate(values):
                if(len(row) > 4 and row[0] == target_username and row[3] == campaign):
                    row_index = i
                    break

            if row_index is None:
                print(f"Aucune ligne avec {target_username} trouvée.")
                return

            reply_date = datetime.datetime.now().date().isoformat()

            # Préparer les nouvelles données
            existing_content = values[row_index][4] if len(values[row_index]) > 4 else ""
            new_content = existing_content + "\n\n"+ f"{target_username}:  " + message  # Concaténer l'ancien et le nouveau message

            # Mise à jour de la cellule
            update_range = f"{sheet_name}!E{row_index+1}:F{row_index+1}"
            body = {
                'values': [[new_content, reply_date]]
            }
            service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=update_range,
                body=body,
                valueInputOption='RAW'
            ).execute()

        except Exception as e:
            print(f"Erreur add_new_reply_to_gg : {e}")
    
    def incrementTotalSend(self, campaign):
        service = build('sheets', 'v4', credentials=self.creds)
        sheet_name = 'Campaigns'
        range_name = f"{sheet_name}!A:G"

        result = service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range_name
        ).execute()

        values = result.get('values', [])

        for index, row in enumerate(values):
            if len(row) > max(2, 6) and row[2] == campaign:
                # Vérifier si la valeur existante est un nombre
                try:
                    current_value = int(row[6])
                except ValueError:
                    print("La valeur existante n'est pas un nombre valide")

                # Construire la référence de la cellule à modifier
                cell_to_update = f"{sheet_name}!G{index + 1}"

                # Incrémenter la valeur et mettre à jour la cellule
                new_value = current_value + 1
                update_body = {
                    "values": [[new_value]]
                }
                service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=cell_to_update,
                    valueInputOption="USER_ENTERED",
                    body=update_body
                ).execute()

    #scrapping
    def update_google_sheet(self, target, accountInfo, scraping_spreadsheet_id):
        try:
            # Charger les identifiants
            creds = None
            creds = Credentials.from_service_account_file('C:/Users/thoma/OneDrive/Documents/Socialify/BOT/google_credentials.json',
                                                        scopes=["https://www.googleapis.com/auth/spreadsheets"])
        except Exception as e:
            print(f"Erreur lors de la création des identifiants : {e}")

        # Construire le service Google Sheets
        service = build('sheets', 'v4', credentials=creds)

        #sheetName
        sheet_name = 'Feuille 4'

        username = target
        nbFollowers = accountInfo["nbFollowers"]
        nbFollowing = accountInfo["nbFollowing"]
        nbPublications = accountInfo["nbPublications"]
        fullName = accountInfo["fullName"]
        bio = accountInfo["bio"]
        link = accountInfo["url_link"]

        values = [[username, fullName, nbFollowers, nbFollowing, nbPublications, bio, link]]

        body = {
        'values': values
        }
        range_name = f"{sheet_name}"

        try:
            sheet = service.spreadsheets().values().append(
                spreadsheetId=scraping_spreadsheet_id,
                range=range_name,
                body=body,
                valueInputOption='RAW'  # Les valeurs sont écrites telles quelles
            ).execute()

        except Exception as e:
            print(f"Erreur drive update_google_sheet : {e}")

