from pymongo import MongoClient
from datetime import datetime
import bcrypt
from bson.objectid import ObjectId
import random



############### A SAVOIR ###############

# Attention, une conversation est entre
# deux (ou plus) Users.
# Donc pour chaque nouvel InstagramAccount
# il faut créer un User qui a le même _id

#######################################


class MongoDB:
    def __init__(self):
        conn_str = "mongodb+srv://thomaslaumonier:Qypj7XcUEOEuLugt@m0cluster.7daojiy.mongodb.net/?retryWrites=true&w=majority"
        client = MongoClient(conn_str)
        self.db = client["Socialify"]
        
    def eraseTargetCollection(self):
        # This will drop the entire Target collection
        self.db.Target.drop()

    def getAccountsByCampaignId(self, campaignId):
        accounts = list(self.db.InstagramAccount.find({ "campaignId": ObjectId(campaignId) }))
        random.shuffle(accounts)
        return accounts
    
    def getAccountByUsername(self, username):
        return list(self.db.InstagramAccount.find({ "username": username }))

    def updateInstagramAccount(self, username, accountStatus, accountInfo):
        try:
            currentDate = datetime.now()
            update_data = {
                "$set": {
                    "updatedAt": currentDate,
                    "followers": accountInfo.get("nbFollowers", None),
                    "following": accountInfo.get("nbFollowing", None),
                    "publications": accountInfo.get("nbPublications", None),
                    "Names": accountInfo.get("fullName", None),
                    "status": accountStatus,
                    "image": accountInfo.get("PDP", None),
                    "bio": accountInfo.get("bio", None),
                }
            }

            self.db.InstagramAccount.update_one({"username": username}, update_data)
        
        except Exception as e:
            print("Erreur mongoDB -> updateInstagramAccount")
            print(e)
    
    def getCampaignMessage(self, campaignId):
        return self.db.Campaign.find_one({ "_id": ObjectId(campaignId) }).get("message", None)

    def getAmazonLinkByCampaignId(self, campaignId):
        return self.db.Campaign.find_one({ "_id": ObjectId(campaignId) }).get("amazonLink", None)

    def getConversationByConversationId(self, conversationId):
        return self.db.Conversation.find_one({ "_id": ObjectId(conversationId) })

    def getConversationByTargetUsernameAndCampaignId(self, targetUsername, campaignId):
        conversation = self.db.Conversation.find_one({ 
            "contactedUsername": targetUsername, 
            "campaignId": ObjectId(campaignId) 
        })
        
        if not conversation:
            return None

        conversationId = conversation.get("_id")

        messages = list(self.db.Message.find({
            "conversationId": ObjectId(conversationId)
        }).sort("createdAt", 1))  # 1 means ascending order

        return conversationId, messages 

    def handleNewMessage(self, campaignId, username, targetUsername, imageUrl, message, isFirst=None):

        targetUser = self.db.User.find_one({"username": targetUsername })
        instagramAccountId = self.db.InstagramAccount.find_one({ "username": username })["_id"]

        currentConversation = self.db.Conversation.find_one( {"campaignId": ObjectId(campaignId), "contactedUsername": targetUsername} )
        if currentConversation: current_message = self.db.Message.find_one({ "conversationId": ObjectId(currentConversation["_id"]), "body": message })

        if(not targetUser):
            targetUserId = self.addNewUser(targetUsername, imageUrl)
            currentConversationId = self.addNewConversation(campaignId, instagramAccountId, targetUserId, targetUsername)
            self.addNewMessage(targetUserId, currentConversationId, message)

        elif(not currentConversation):
            currentConversationId = self.addNewConversation(campaignId, instagramAccountId, targetUser["_id"], targetUsername)
            self.addNewMessage(targetUser["_id"], currentConversationId, message)

        elif(not current_message and isFirst):
            self.addNewSentMessage(instagramAccountId, currentConversationId, message)

        elif(not current_message):
            self.addNewMessage(targetUser["_id"], currentConversation["_id"], message)

    def addNewUser(self, targetUsername, imageUrl):
        hashed_password = bcrypt.hashpw("motdepasse123".encode('utf-8'), bcrypt.gensalt())

        new_user = {
            "username": targetUsername,
            "name": targetUsername,
            "email": f"{targetUsername}@mail.com",
            "hashedPassword": hashed_password.decode('utf-8'),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "conversationIds": [],
            "seenMessageIds": [],
            "image": imageUrl
        }

        currentUserId = self.db.User.insert_one(new_user).inserted_id

        return currentUserId

    def addNewConversation(self, campaignId, instagramAccountId, targetUserId, targetUsername):

        campaignUserId = self.db.User.find_one({ "campaignIds": ObjectId(campaignId)})["_id"]
    
        new_conversation = {
            "contactedUsername": targetUsername,
            "createdAt": datetime.utcnow(),
            "lastMessageAt": datetime.utcnow(),
            "campaignId": ObjectId(campaignId),
            "instagramAccountId": ObjectId(instagramAccountId),
            "userIds": [ObjectId(targetUserId), ObjectId(campaignUserId)],
        }

        conversation_id = self.db.Conversation.insert_one(new_conversation).inserted_id

        self.db.User.update_one({ "_id": ObjectId(targetUserId) }, { "$push": {"conversationIds": ObjectId(conversation_id) }})
        self.db.User.update_one({ "_id": ObjectId(campaignUserId) }, { "$push": {"conversationIds": ObjectId(conversation_id) }})
        self.db.Campaign.update_one({ "_id": ObjectId(campaignId) }, { "$push": {"conversationIds": ObjectId(conversation_id) }})

        return conversation_id

    def addNewMessage(self, targetUserId, currentConversationId, message):

        new_message = {
            "body": message,
            "createdAt": datetime.now(),
            "onInstagram": True,
            "conversationId": ObjectId(currentConversationId),
            "senderId": ObjectId(targetUserId),
            "seenIds": [ObjectId(targetUserId)],
        }

        message_id = self.db.Message.insert_one(new_message).inserted_id
        self.db.User.update_one({ "_id": ObjectId(targetUserId) }, { "$push": {"seenMessageIds": ObjectId(message_id) }})

    def addNewSentMessageByConversationId(self, instagramAccountId, currentConversationId, message):
        
        new_message = {
            "body": message,
            "createdAt": datetime.now(),
            "onInstagram": True,
            "conversationId": ObjectId(currentConversationId),
            "senderId": ObjectId(instagramAccountId),
            "isSent": True
        }
        self.db.Message.insert_one(new_message).inserted_id

    def addSentMessage(self, campaignId, instagramAccountId, targetUsername, message):
        sentMessage = {
            "campaignId": ObjectId(campaignId),
            "instagramAccountId": ObjectId(instagramAccountId),
            "targetUsername": targetUsername,
            "createdAt": datetime.utcnow(),
            "message": message,
            "isSent": True
        }
        self.db.SentMessage.insert_one(sentMessage)

    def getRepliesByCampaignByInstagramAccount(self, campaignId, instagramAccountId):
        pipeline = [
            # Étape 1: Joindre les collections de conversations à messages
            {"$lookup": {
                "from": "conversations",
                "localField": "conversationId",
                "foreignField": "_id",
                "as": "conversation"
            }},
            # Déplier les documents de conversation pour faciliter le filtrage
            {"$unwind": "$conversation"},
            # Étape 2: Filtrer pour les documents qui correspondent aux critères
            {"$match": {
                "conversation.campaignId": ObjectId(campaignId),
                "conversation.instagramAccountId": ObjectId(instagramAccountId),
                "onInstagram": False
            }},
            # Étape 3: Trier les messages par createdAt
            {"$sort": {"createdAt": 1}},
            # Étape 4: Regrouper les messages par conversationId
            {"$group": {
                "_id": "$conversationId",
                "messages": {
                    "$push": {
                        "messageId": "$_id",
                        "body": "$body",
                        "createdAt": "$createdAt",
                        "senderId": "$senderId",
                        "seenIds": "$seenIds",
                        "onInstagram": "$onInstagram"
                    }
                }
            }},
        ]
        return list(self.db.messages.aggregate(pipeline))

    def updateMessageOnInstagram(self, messageId):
        return self.db.Message.update_one({ "_id": ObjectId(messageId) }, { "$set": { "onInstagram": True } })

    def getFilteredMessages(self, campaignId, instagramAccountId):
        pipeline = [
            {
                "$match": {
                    "campaignId": ObjectId(campaignId),
                    "instagramAccountId": ObjectId(instagramAccountId)
                }
            },
            {
                "$lookup": {
                    "from": "Message",
                    "localField": "_id",
                    "foreignField": "conversationId",
                    "as": "messages"
                }
            },
            {
                "$unwind": "$messages"
            },
            {
                "$match": {
                    "messages.onInstagram": False
                }
            },
            {
            "$sort": {
                "messages.createdAt": 1  # Trier les messages par createdAt de manière ascendante
                }
            },
            {
                "$project": {
                    "_id": "$messages._id",
                    "body": "$messages.body",
                    "createdAt": "$messages.createdAt",
                    "campaignId": "$messages.campaignId",
                    "conversationId": "$messages.conversationId",
                    "contactedUsername": 1
                }
            }
        ]

        return list(self.db.Conversation.aggregate(pipeline))

    def addUserImage(self, targetUserId, imageUrl):
        self.db.User.update_one({ "_id": ObjectId(targetUserId) }, { "$set":  {"image": imageUrl} })

    def addUserIdToConversations(self, campaignId, newUserId):
        # Rechercher toutes les conversations avec le campaignId spécifique
        conversations = self.db.Conversation.find({ "campaignId": ObjectId(campaignId) })

        for conversation in conversations:
            # Ajouter le nouvel userId à la liste des userIds de chaque conversation
            self.db.Conversation.update_one(
                { "_id": conversation["_id"] },
                { "$addToSet": { "userIds": ObjectId(newUserId) } }
            )

            # Mettre à jour les utilisateurs concernés par ces conversations
            self.db.User.update_one(
                { "_id": ObjectId(newUserId) },
                { "$addToSet": { "conversationIds": conversation["_id"] } }
            )

        print(f"New userId {newUserId} added to conversations with campaignId {campaignId}")

    def replaceSenderIdInMessages(self, campaignId, oldUserId, newUserId):
        # Rechercher toutes les conversations avec le campaignId spécifique
        conversations = self.db.Conversation.find({ "campaignId": ObjectId(campaignId) })

        for conversation in conversations:
            # Rechercher tous les messages dans ces conversations où senderId est l'ancien userId
            messages = self.db.Message.find({ 
                "conversationId": conversation["_id"],
                "senderId": ObjectId(oldUserId)
            })

            for message in messages:
                # Mettre à jour le senderId avec le nouveau userId
                self.db.Message.update_one(
                    { "_id": message["_id"] },
                    { "$set": { "senderId": ObjectId(newUserId) } }
                )

                # Mettre à jour seenIds s'il contient l'ancien userId
                self.db.Message.update_one(
                    { "_id": message["_id"], "seenIds": ObjectId(oldUserId) },
                    { "$pull": { "seenIds": ObjectId(oldUserId) } }
                )
                self.db.Message.update_one(
                    { "_id": message["_id"] },
                    { "$addToSet": { "seenIds": ObjectId(newUserId) } }
                )

            # Mettre à jour les utilisateurs concernés par ces messages
            self.db.User.update_one(
                { "_id": ObjectId(newUserId) },
                { "$addToSet": { "seenMessageIds": { "$each": [message["_id"] for message in messages] } } }
            )
            self.db.User.update_one(
                { "_id": ObjectId(oldUserId) },
                { "$pull": { "seenMessageIds": { "$in": [message["_id"] for message in messages] } } }
            )

        print(f"Messages with senderId {oldUserId} replaced by {newUserId} in conversations with campaignId {campaignId}")

    def countMessagesSentByUserByCampaign(self, campaignId, oldUserId):
        # Rechercher toutes les conversations avec le campaignId spécifique
        conversations = self.db.Conversation.find({ "campaignId": ObjectId(campaignId) })

        for conversation in conversations:
            # Rechercher tous les messages dans ces conversations où senderId est l'ancien userId
            messages = self.db.Message.find({ 
                "conversationId": conversation["_id"],
                "senderId": ObjectId(oldUserId)
            })

    def addTargets(self, usernames, campaignId):
        """
        Ajoute une liste de cibles (usernames) dans la collection Target avec la référence de campaignId.
        usernames: liste de strings représentant les usernames des cibles.
        campaignId: l'ID de la campagne associée (de type string ou ObjectId).
        """
        try:
            # Si campaignId est une chaîne de caractères, le convertir en ObjectId
            if isinstance(campaignId, str):
                campaignId = ObjectId(campaignId)

            currentDate = datetime.now()

            # Créer une liste de documents à insérer
            targets_to_insert = [
                {
                    "username": username,
                    "campaignId": campaignId,
                    "scraped_at": currentDate,
                    "contacted_at": None,  # Indique que cette cible n'a pas encore été contactée
                }
                for username in usernames
            ]

            # Insérer les documents dans la collection Target
            result = self.db.Target.insert_many(targets_to_insert)
            print(f"{len(result.inserted_ids)} cibles ont été ajoutées à la campagne {campaignId}.")

        except Exception as e:
            print("Erreur mongoDB -> addTargets")
            print(e)

    def addTargetsByReadingFile(self, file_path, campaignId):
        """
        Cette fonction lit le fichier filtré et ajoute les usernames extraits comme cibles dans la campagne spécifiée.
        
        output_file_path: chemin vers le fichier contenant les usernames.
        campaignId: ID de la campagne associée (de type string ou ObjectId).
        db_instance: l'instance de la base de données MongoDB où se trouve la collection Target.
        """
        try:
            # Lire le fichier filtré pour extraire les usernames
            with open(file_path, 'r', encoding='utf-8') as outfile:
                usernames = [line.strip() for line in outfile.readlines()]

            self.addTargets(usernames, campaignId)

        except Exception as e:
            print("Erreur lors de l'ajout des cibles à partir du fichier")
            print(e)

    def getUncontactedTargets(self, campaignId):
        """
        Récupère la liste des usernames des cibles qui n'ont pas encore été contactées pour une campagne donnée.
        campaignId: l'ID de la campagne associée (de type string ou ObjectId).
        """
        try:
            # Si campaignId est une chaîne de caractères, le convertir en ObjectId
            if isinstance(campaignId, str):
                campaignId = ObjectId(campaignId)

            # Rechercher les cibles non contactées (contacted_at == None)
            uncontacted_targets = self.db.Target.find({
                "campaignId": campaignId,
                "contacted_at": None
            })

            # Extraire et retourner les usernames des cibles non contactées
            return [target['username'] for target in uncontacted_targets]

        except Exception as e:
            print("Erreur mongoDB -> getUncontactedTargets")
            print(e)
            return []

    def updateTargetContacted(self, username, campaignId):
        """
        Met à jour l'état d'une cible (target) comme étant contactée pour une campagne donnée.
        username: Le nom d'utilisateur de la cible à mettre à jour.
        campaignId: L'ID de la campagne associée (de type string ou ObjectId).
        """
        try:
            # Si campaignId est une chaîne de caractères, le convertir en ObjectId
            if isinstance(campaignId, str):
                campaignId = ObjectId(campaignId)

            # Mettre à jour le champ contacted_at avec la date et l'heure actuelles
            currentDate = datetime.now()

           # Rechercher la cible par username et campaignId et mettre à jour contacted_at
            result = self.db.Target.update_one(
                {"username": username, "campaignId": campaignId},
                {"$set": {"contacted_at": currentDate}}
            )

            if result.matched_count < 1:
                print(f"Erreur, aucune cible trouvée pour {username} dans la campagne {campaignId}.")

        except Exception as e:
            print("Erreur mongoDB -> updateTargetContacted")
            print(e)

    def getAccountForScraping(self, campaignId):
        accounts = self.getAccountsByCampaignId(campaignId)
        
        if accounts:
            return random.choice(accounts)
        else:
            print(f"Aucune compte trouvé pour la campagne {campaignId}")
            return None

    def delete_conversations_and_messages_by_campaign(self, campaign_id):
        try:
            # Convertir le campaign_id en ObjectId
            campaign_object_id = ObjectId(campaign_id)
            
            # Récupérer toutes les conversations liées à la campaignId
            conversations = self.db.Conversation.find({"campaignId": campaign_object_id})
            
            # Récupérer tous les conversationId des conversations liées
            conversation_ids = [conversation["_id"] for conversation in conversations]
            
            if conversation_ids:
                # Supprimer les messages liés à ces conversations
                delete_messages_result = self.db.Message.delete_many({"conversationId": {"$in": conversation_ids}})
                print(f"{delete_messages_result.deleted_count} messages deleted.")

                # Supprimer les conversations liées à la campaignId
                delete_conversations_result = self.db.Conversation.delete_many({"campaignId": campaign_object_id})
                print(f"{delete_conversations_result.deleted_count} conversations deleted.")
            else:
                print("No conversations found for the given campaignId.")

        except Exception as e:
            print(f"An error occurred: {e}")

    def create_users_from_instagram_accounts(self):
        try:
            instagram_accounts = self.db.InstagramAccount.find()  # Récupérer tous les comptes Instagram

            for account in instagram_accounts:
                # Vérifier si un utilisateur avec le même _id existe déjà
                existing_user = self.db.User.find_one({"_id": account["_id"]})

                email = f"{account['username']}@mail.com"  # Générer l'email à partir du username
                created_at = datetime.now()  # Utiliser la date et l'heure actuelles pour createdAt

                if not existing_user:
                    # Si aucun utilisateur n'existe avec cet ID, créer un nouvel utilisateur
                    new_user = {
                        "_id": account["_id"],  # Utiliser le même _id que InstagramAccount
                        "username": account["username"],  # Copier des informations pertinentes
                        "email": email,  # Générer l'email
                        "createdAt": created_at,  # Définir createdAt comme la date actuelle
                        "updatedAt": created_at,
                        "isInstagramAccount": True  # Marquer cet utilisateur comme lié à un InstagramAccount
                    }

                    # Insérer le nouvel utilisateur dans la collection `User`
                    self.db.User.insert_one(new_user)
                    print(f"User created for InstagramAccount with _id {account['_id']}")
                else:
                    # Si l'utilisateur existe déjà, mettre à jour les champs createdAt et email
                    self.db.User.update_one(
                        {"_id": account["_id"]},
                        {
                            "$set": {
                                "email": email,  # Mettre à jour l'email
                                "createdAt": created_at,  # Mettre à jour createdAt
                                "updatedAt": created_at
                            }
                        }
                    )
                    print(f"User with _id {account['_id']} updated.")

        except Exception as e:
            print(f"An error occurred: {e}")

    def get_users_with_null_updatedAt(self):
        users_collection = self.db["User"]
        query = { "updatedAt": None }
        projection = { "_id": 1 }  # On ne récupère que le champ _id
        users_with_null_updatedAt = list(users_collection.find(query, projection))
        
        user_ids = [user["_id"] for user in users_with_null_updatedAt]
        count = len(user_ids)
        return count, user_ids

    def update_null_updatedAt(self):
        users_collection = self.db["User"]
        query = { "updatedAt": None }
        new_values = { "$set": { "updatedAt": datetime.now() } }
        result = users_collection.update_many(query, new_values)
        return result.modified_count

    def get_conversations_with_null_updatedAt(self):
        conversations_collection = self.db["Conversation"]
        query_null = { "updatedAt": None }
        query_missing = { "updatedAt": { "$exists": False } }

        # Conversations avec 'updatedAt' à null
        conversations_null = list(conversations_collection.find(query_null, { "_id": 1 }))
        count_null = len(conversations_null)

        # Conversations sans le champ 'updatedAt'
        conversations_missing = list(conversations_collection.find(query_missing, { "_id": 1 }))
        count_missing = len(conversations_missing)

        return count_null, conversations_null, count_missing, conversations_missing
