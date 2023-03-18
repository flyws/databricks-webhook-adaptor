# databricks-webhook-adaptor
This is a project to make Databricks Workflow webhook be able to send messages to different IM tools that are not formally supported by Databricks.

## Context
Databricks Workflow is the orchestrator feature on Databricks platform, and it supports custom [webhooks](https://docs.databricks.com/administration-guide/workspace/settings/notification-destinations.html#add-a-webhook-to-a-job) to notify the status of the workflow. However, the webhook has pre-configured format so is only able to send notifications to Slack, Teams, and Email. This project is to make the webhook be able to adapt to different IM tools that are not formally supported by Databricks. At the moment this project will only send notifications when the workflow is failed. But it can be extended or customized.

This project is a minimal implementation of the webhook adaptor. It is designed to be extensible. You can add new IM tools and contributions are welcome.

## Requirements
1. You have a server that can run a Python script.
2. The server has a public IP address / domain name and can accept web request from Databricks server.
3. The server can access the internet and send out the relay message.

***Note that in best practice you shouldn't expose your server to accept all web requests from the internet. You should find the Databricks server IP and only accept its web requests. You can find the relevant IPs in Databricks doc or from a test site like [webhook.site](https://webhook.site/)***

## Architecture
```text
+---------------------+               +-----------------------+               +---------------------+
| Databricks Control  | --webhook-->  | Your Flask Application | --webhook-->  |  IM Tool (Feishu or |
|       Plane         |               |       (Server)         |               |        Wecom)       |
+---------------------+               +-----------------------+               +---------------------+
                                     ^                          |
                                     |                          |
                             Allow traffic only from            |
                           Databricks Control Plane IP          |
                                                                 |
                                                                 v
                                                      +---------------------+
                                                      | Databricks Jobs API |
                                                      +---------------------+
```

## How to use
There are two ways to use this project:

### Run the script on your server machine
1. Download the code from this repo to your server.
2. Install the required packages by running `pip install -r requirements.txt`.
3. Modify the `config.json` file to add your own webhook URL and Databricks instance information.
4. Run the script by `python webhook_adaptor.py`.
5. Add the webhook URL to your Databricks Workflow. Example: `http://<your_server_ip>:5000/webhook`.
6. Run the workflow and check the notification on your IM tool.

### Build and run the Docker image
1. Download the code from this repo to your server.
2. Build the Docker image by `docker build -t databricks-webhook-adaptor .`.
3. Run the Docker image by `docker run -d -p 5000:80 databricks-webhook-adaptor`.
4. Add the webhook URL to your Databricks Workflow. Example: `http://<your_server_ip>:5000/webhook`.
5. Run the workflow and check the notification on your IM tool.

## How to find your workspace ID?
1. Go to your Databricks workspace.
2. Retrieve your workspace ID from URL by following the [link](https://kb.databricks.com/en_US/administration/find-your-workspace-id#:~:text=After%20you%20have%20logged%20into,make%20up%20the%20workspace%20ID.)
3. If you have custom DNS name with Databricks, you can also find your workspace ID from Databricks representative or use the utility tool on the support hub.
4. If none of the above work, you can get your workspace ID from the webhook message by setting up your webhook using a test site like [webhook.site](https://webhook.site/). 


## Supported IM tools
1. Tencent Wecom （企业微信）
2. Feishu / Lark （飞书）

## How to add new IM tools
This project is designed to be highly extensible. You can add new IM tools by following the steps below:
1. Create a new Python file under the same folder. The file name should be the name of the IM tool + `_bot`.
2. Import the new adaptor function into the main Flask server script `webhook_server.py`.
3. Change the `config.json` file to add the new IM tool name.
4. Add your send function into the main script `webhook_server.py`.
5. Test

## How to customize your message
TODO
