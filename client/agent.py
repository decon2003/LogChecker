import threading
import requests
import time
import subprocess
from xml.etree.ElementTree import fromstring
from database.db_manager import insert_log

def fetch_logs(required_logs, uuid):  
    """
    Fetch logs from the Windows Event Log and save them to the database.
    """
    command = (
        f"powershell.exe -Command \"Get-WinEvent -LogName Microsoft-Windows-Sysmon/Operational -MaxEvents {required_logs} | ForEach-Object {{ $_.ToXml() }}\""
    )
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        logs_output, error_output = process.communicate()
        if error_output:
            print(f"[ERROR] {error_output}")
            return

        logs = logs_output.strip().split("</Event>")
        logs = [log + "</Event>" for log in logs if log.strip()]

        for log in logs:
            root = fromstring(log)
            event_record_id = root.find(".//EventRecordID")
            if event_record_id is not None:
                insert_log(uuid, log)

        print(f"[INFO] {len(logs)} logs fetched and saved.")
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

def start_agent(data, uuid, result_display):
    """
    Start the agent to fetch and monitor logs.
    """
    required_logs = data["required_logs"]
    socket_url = data["socket_url"]

    # Fetch initial logs
    result_display.insert("Fetching initial logs...\n")
    fetch_logs(required_logs, uuid)
    result_display.insert("Initial logs saved.\n")

    # Start monitoring new logs
    is_running = threading.Event()
    is_running.set()
    threading.Thread(target=monitor_new_logs, args=(0, uuid, is_running), daemon=True).start()

    # Handle graceful shutdown
    def stop_agent():
        is_running.clear()
        result_display.insert("Agent stopped.\n")

    return stop_agent
