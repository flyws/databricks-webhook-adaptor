# import the necessary packages
from flask import Flask, request, jsonify
import requests
import json
from feishu_bot import send_to_feishu_bot
from wecom_bot import send_to_wecom_bot

# Read the configuration file
with open("config.json", "r", encoding='utf-8') as config_file:
    config = json.load(config_file)

# Load the URLs
wecom_webhook_url = config["wecom_webhook_url"]
feishu_webhook_url = config["feishu_webhook_url"]
databricks_workspaces = config["databricks_workspaces"]

# Create the Flask app
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        if not data:
            raise ValueError("No JSON payload received")

        # Get the run_id and workspace_id from the JSON payload
        run_id = data.get('run', {}).get('run_id')
        workspace_id = data.get('workspace_id')

        if run_id is None or workspace_id is None:
            raise ValueError("No run_id or workspace_id found in the JSON payload")

        print(f"Run ID: {run_id}")

        # Get the job run details from the Databricks API and send to the custom Bot
        job_run = get_databricks_job_run(workspace_id, run_id)
        # send the message to your bot (Please modify accordingly)
        send_to_wecom_bot(wecom_webhook_url, job_run)

        print("Job run details:")
        print(json.dumps(job_run, indent=4, sort_keys=True))

        return jsonify(job_run), 200

    except ValueError as e:
        print(e)
        return 'Invalid JSON', 400

def get_databricks_job_run(workspace_id, run_id):

    # Find the Databricks workspace that contains the run_id
    databricks_instance = None
    databricks_token = None
    for workspace in databricks_workspaces:
        if str(workspace_id) == str(workspace.get('workspace_id')):
            databricks_instance = str(workspace.get('databricks_instance'))
            databricks_token = str(workspace.get('databricks_token'))
            break
    if not databricks_instance or not databricks_token:
        raise ValueError(f'No Databricks workspace information found for run_id: {run_id}')
    
    # Get the job run details from the Databricks API
    url = f'https://{databricks_instance}/api/2.1/jobs/runs/get?run_id={run_id}'
    headers = {
        'Authorization': f'Bearer {databricks_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f'Error getting job run from Databricks API: {response.status_code} - {response.text}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)