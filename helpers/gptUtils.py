from openai import OpenAI
import os
from bson.objectid import ObjectId
import datetime

class GPTutils:
    def getMessageForGPT(messages, instagramAccountId, amazonLink):
        formatted_conversation = ""

        formatted_conversation += f"Voici un dialogue sur instagram, tu es le vendeur affilié amazon, si l'utilisateur est intéressé par l'offre tu dois lui donner le lien affilié suivant de manière subtile : {amazonLink}\nS'il n'est pas intéressé réponds poliment.\nAttention, donne uniquement la réponse.\n\n"

        for index, message in enumerate(messages):
            if message["senderId"] == ObjectId(instagramAccountId) or index==0 or message.get("isSent"):    #maintenant on a juste besoin de isSent mais les anciens messages (avant 15/10/2024) n'ont pas isSent
                sender = "Vous"
            else:
                sender = "Utilisateur instagram"
            
            formatted_conversation += (f"{sender} : {message['body']}\n")
        
        return formatted_conversation

    def getReplyFromOpenAI(message):
        client = OpenAI(
            api_key='...'
        )

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": message
                }
            ]
        )
        return completion.choices[0].message.content