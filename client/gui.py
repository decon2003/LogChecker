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
        threading.Thread(target=start_agent, args=(data, UUID, result_display)).start()
    else:
        append_result("[ERROR] Không thể kết nối đến server.", result_display)

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
