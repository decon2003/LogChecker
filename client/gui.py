import threading
import time
import uuid
import requests
from tkinter import Tk, Text, Button, END
from client.agent import start_agent

SERVER_URL = "http://127.0.0.1:5000"
UUID = str(uuid.uuid4())

def append_result(message, result_display):
    result_display.insert(END, f"{message}\n")
    result_display.see(END)

def run_agent(result_display):
    response = requests.get(f"{SERVER_URL}/required_logs")
    if response.status_code == 200:
        data = response.json()
        append_result("[INFO] Starting agent...", result_display)
        threading.Thread(target=start_agent, args=(data, UUID, result_display)).start()
    else:
        append_result("[ERROR] Cannot connect to the server.", result_display)

def upload_logs_and_update_gui(logs, result_display):
    try:
        response = requests.post(f"{SERVER_URL}/upload_logs", json={"uuid": UUID, "logs": logs})
        if response.status_code == 200:
            predictions = response.json().get("predictions", [])
            append_result(f"[INFO] Predictions: {predictions}", result_display)
        else:
            append_result(f"[ERROR] Failed to upload logs. Status: {response.status_code}", result_display)
    except Exception as e:
        append_result(f"[ERROR] Exception occurred while uploading logs: {e}", result_display)

        
def main():
    root = Tk()
    root.title("Agent")

    result_display = Text(root, height=20, width=80)
    result_display.pack()

    start_button = Button(root, text="Bắt đầu", command=lambda: run_agent(result_display))
    start_button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
