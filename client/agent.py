import threading
import requests
import time
import subprocess
from xml.etree.ElementTree import fromstring
from tkinter import END 
from database.db_manager import insert_log

SERVER_URL = "http://127.0.0.1:5000" 

def fetch_logs(required_logs, uuid):
    logs = []  # Initialize a list to store logs
    command = (
        f"powershell.exe -Command \"Get-WinEvent -LogName Microsoft-Windows-Sysmon/Operational -MaxEvents {required_logs} | ForEach-Object {{ $_.ToXml() }}\""
    )
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        logs_output, error_output = process.communicate()
        if error_output:
            print(f"[ERROR] {error_output}")
            return

        logs_split = logs_output.strip().split("</Event>")
        logs = [log + "</Event>" for log in logs_split if log.strip()]

        for log in logs:
            root = fromstring(log)
            event_record_id = root.find(".//EventRecordID")
            if event_record_id is not None:
                insert_log(uuid, log)

        print(f"[INFO] {len(logs)} logs fetched and saved.")
        
        # Upload logs to the server
        upload_logs_to_server(logs, uuid)

    except Exception as e:
        print(f"[ERROR] Failed to fetch logs: {e}")


def monitor_new_logs(last_record_id, uuid, is_running):
    """
    Continuously monitor new logs and save them to the database.
    """
    while is_running.is_set():
        try:
            query = (
                f"wevtutil qe Microsoft-Windows-Sysmon/Operational /f:RenderedXml /q:\"*[System[(EventRecordID > {last_record_id})]]\""
            )
            process = subprocess.Popen(query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
            logs_output, error_output = process.communicate()
            if error_output:
                print(f"[ERROR] {error_output}")
                continue

            logs = logs_output.strip().split("</Event>")
            logs = [log + "</Event>" for log in logs if log.strip()]

            for log in logs:
                root = fromstring(log)
                event_record_id = root.find(".//EventRecordID")
                if event_record_id is not None:
                    last_record_id = max(last_record_id, int(event_record_id.text))
                    insert_log(uuid, log)

            time.sleep(2)
        except Exception as e:
            print(f"[ERROR] Failed to monitor new logs: {e}")
            time.sleep(5)

def upload_logs_to_server(logs, uuid):
    """
    Upload logs to the server for processing.
    """
    try:
        response = requests.post(f"{SERVER_URL}/upload_logs", json={"uuid": uuid, "logs": logs})
        if response.status_code == 200:
            print("[INFO] Logs successfully uploaded to the server.")
        else:
            print(f"[ERROR] Failed to upload logs. Server responded with status: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Exception while uploading logs: {e}")

def start_agent(data, uuid, result_display):
    """
    Start the agent to fetch and monitor logs.
    """
    required_logs = data["required_logs"]
    socket_url = data["socket_url"]

    result_display.insert(END, "Fetching initial logs...\n") 
    fetch_logs(required_logs, uuid)
    result_display.insert(END, "Initial logs saved.\n")  

    # Start monitoring new logs
    is_running = threading.Event()
    is_running.set()
    threading.Thread(target=monitor_new_logs, args=(0, uuid, is_running), daemon=True).start()

    # Stop monitoring gracefully
    def stop_agent():
        is_running.clear()
        result_display.insert(END, "Agent stopped.\n")  

    return stop_agent
