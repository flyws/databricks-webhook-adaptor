from datetime import datetime
import pytz
import requests

def send_to_wecom_bot(wecom_webhook_url, job_run):
    def to_local_time(ts, tz_id):
        utc_dt = datetime.utcfromtimestamp(ts / 1000)
        local_tz = pytz.timezone(tz_id)
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
        return local_dt.strftime('%Y-%m-%d %H:%M:%S')

    # Modify the timezone to match your geographical location
    timezone_id = job_run.get("schedule", {}).get("timezone_id", "Asia/Shanghai")

    tasks = job_run.get('tasks', [])
    # Find the first failed task and its cluster instance
    failed_task_cluster_instance = None
    for task in tasks:
        if task.get('state', {}).get('result_state') == 'FAILED':
            failed_task_cluster_instance = task.get('cluster_instance')
            break
    if not failed_task_cluster_instance:
        print('No failed tasks found.')
        return

    # format the feishu message in its webhook format
    try:
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": f"**Run Name:** {job_run['run_name']}\n\n"
                        f"[Run Page URL]({job_run['run_page_url']})\n\n"
                        f"**Start Time:** {to_local_time(job_run['start_time'], timezone_id)}\n\n"
                        f"**End Time:** {to_local_time(job_run['end_time'], timezone_id)}\n\n"
                        f"**Cluster Instance:** {failed_task_cluster_instance['cluster_id']}\n\n"
                        f"**Creator:** {job_run['creator_user_name']}\n\n"
                        f"**Result State:** {job_run['state']['result_state']}\n\n"
                        f"**State Message:** {job_run['state']['state_message']}"
            }
        }

    except KeyError as e:
        raise ValueError("Error parsing job run JSON") from e

    response = requests.post(wecom_webhook_url, json=payload, timeout=20)
    if response.status_code != 200:
        raise ValueError(f'Error sending message to Feishu Bot: {response.status_code} - {response.text}')