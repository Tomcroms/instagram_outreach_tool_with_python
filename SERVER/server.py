from flask import Flask, request, jsonify
import sys
sys.path.insert(0, "C:/Users/thoma/OneDrive/Documents/Socialify/BOT")
import os
from flask_cors import CORS
from helpers.instagram import InstagramWorker

app = Flask(__name__)
CORS(app)

API_KEY = '12345'

# Dictionnaire global pour stocker les états des scripts
script_status = {}

@app.route('/run-test-connexion-by-campaign-id', methods=['POST'])
def run_test_connexion_by_campaign_id():
    campaignId = request.json.get('campaignId')
    if not campaignId:
        return jsonify({'error': 'Missing campaignId parameter'}), 400

    if script_status.get(campaignId) == 'running':
        return jsonify({'error': 'Script already running for this campaign'}), 400

    script_status[campaignId] = 'running'

    try:
        InstagramWorker.testConnection(campaignId)
        script_status[campaignId] = 'finished'
        return jsonify({'status': 'success'})
    except Exception as e:
        script_status[campaignId] = 'failed'
        return jsonify({'error': str(e)}), 500
    

@app.route('/run-delete-dms-by-campaign-id', methods=['POST'])
def run_delete_dms_by_campaign_id():
    campaignId = request.json.get('campaignId')
    if not campaignId:
        return jsonify({'error': 'Missing campaignId parameter'}), 400

    if script_status.get(campaignId) == 'running':
        return jsonify({'error': 'Script already running for this campaign'}), 400

    script_status[campaignId] = 'running'

    try:
        InstagramWorker.deleteDmByCampaignId(campaignId)
        script_status[campaignId] = 'finished'
        return jsonify({'status': 'success'})
    except Exception as e:
        script_status[campaignId] = 'failed'
        return jsonify({'error': str(e)}), 500


@app.route('/run-modify-bio-by-campaign-id', methods=['POST'])
def run_modify_bio_by_campaign_id():
    campaignId, bio = request.json.get('campaignId', 'bio')
    if not campaignId:
        return jsonify({'error': 'Missing campaignId parameter'}), 400

    if script_status.get(campaignId) == 'running':
        return jsonify({'error': 'Script already running for this campaign'}), 400

    script_status[campaignId] = 'running'

    try:
        InstagramWorker.modifyBioByCampaignId(campaignId, bio)
        script_status[campaignId] = 'finished'
        return jsonify({'status': 'success'})
    except Exception as e:
        script_status[campaignId] = 'failed'
        return jsonify({'error': str(e)}), 500

@app.route('/run-modify-bio-and-delete-dms-by-campaign-id', methods=['POST'])
def run_modify_bio_and_delete_dms_by_campaign_id():
    data = request.json  # Get the JSON data from the request
    campaignId = data.get('campaignId')
    bio = data.get('bio')
    if not campaignId:
        return jsonify({'error': 'Missing campaignId parameter'}), 400

    if script_status.get(campaignId) == 'running':
        return jsonify({'error': 'Script already running for this campaign'}), 400

    script_status[campaignId] = 'running'

    try:
        InstagramWorker.modifyBioAndDeleteDmByCampaignId(campaignId, bio)
        script_status[campaignId] = 'finished'
        return jsonify({'status': 'success'})
    except Exception as e:
        script_status[campaignId] = 'failed'
        return jsonify({'error': str(e)}), 500

@app.route('/run-scraping-followers-by-usernames', methods=['POST'])
def run_scraping_followers_by_followers():
    data = request.get_json()
    campaignId = data.get('campaignId')
    usernames = data.get('usernames')
    
    if not isinstance(usernames, list):
        usernames = [usernames]
    
    print("usernames: ", usernames)
    numberOfAccountsToScrap = data.get('numberOfAccountsToScrap')

    print("NumberOfAccountsToScrap: ", numberOfAccountsToScrap)

    if not campaignId:
        return jsonify({'error': 'Missing campaignId parameter'}), 400

    if script_status.get(campaignId) == 'running':
        return jsonify({'error': 'Script already running for this campaign'}), 400

    script_status[campaignId] = 'running'

    try:
        InstagramWorker.scrapingFollowersByCampaignId(campaignId, usernames, numberOfAccountsToScrap)
        script_status[campaignId] = 'finished'
        return jsonify({'status': 'success'})
    except Exception as e:
        script_status[campaignId] = 'failed'
        return jsonify({'error': str(e)}), 500

@app.route('/run-send-messages-by-campaign-id', methods=['POST'])
def run_send_messages_by_campaignId():
    data = request.get_json()
    campaignId = data.get('campaignId')

    if not campaignId:
        return jsonify({'error': 'Missing campaignId parameter'}), 400

    if script_status.get(campaignId) == 'running':
        return jsonify({'error': 'Script already running for this campaign'}), 400

    script_status[campaignId] = 'running'

    try:
        InstagramWorker.sendCampaignMessagesByCampaignId(campaignId, 8)
        script_status[campaignId] = 'finished'
        return jsonify({'status': 'success'})
    except Exception as e:
        script_status[campaignId] = 'failed'
        return jsonify({'error': str(e)}), 500

@app.route('/check-status/<campaignId>', methods=['GET'])
def check_status(campaignId):
    print("Called check status")
    status = script_status.get(campaignId, 'not started')
    return jsonify({'status': status})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
