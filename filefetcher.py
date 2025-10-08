import subprocess
import time
import requests
import hashlib
import threading
import sys
import os

BOT_FILE = "bottohm.py"
PHONE_IP = "192.168.1.9"  # replace with your phone's IP
BOT_URL = f"http://{PHONE_IP}:8000/{BOT_FILE}"
FETCH_INTERVAL = 5  # seconds between fetch attempts

def fetch_latest_bot():
    """Fetch bot from phone, return True if file changed"""
    retries = 2
    for attempt in range(retries):
        try:
            r = requests.get(BOT_URL, timeout=15)  # increase timeout
            r.raise_for_status()
            new_code = r.text

            # check if file content changed
            if os.path.exists(BOT_FILE):
                with open(BOT_FILE, "r") as f:
                    old_code = f.read()
                if hashlib.md5(old_code.encode()).hexdigest() == hashlib.md5(new_code.encode()).hexdigest():
                    # file did not change
                    return False

            # write new file
            with open(BOT_FILE, "w") as f:
                f.write(new_code)
            print("Fetched latest bot from phone and updated.")
            return True
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt < retries - 1:
                continue  # try again
            else:
                print("⚠️ Could not fetch bot from phone — check connection.")
                return False
        except Exception as e:
            print("Failed to fetch bot:", e)
            return False

class BotRunner:
    def __init__(self):
        self.process = None
        self.start_bot()

    def start_bot(self):
        if self.process:
            self.process.kill()
        self.process = subprocess.Popen([sys.executable, BOT_FILE])
        print("Bot started...")

    def restart_if_changed(self):
        if fetch_latest_bot():
            print("Bot file changed. Restarting...")
            self.start_bot()

def fetch_loop(runner, interval=FETCH_INTERVAL):
    while True:
        runner.restart_if_changed()
        time.sleep(interval)

if __name__ == "__main__":
    runner = BotRunner()
    # run fetch loop in a separate daemon thread
    t = threading.Thread(target=fetch_loop, args=(runner,), daemon=True)
    t.start()

    # keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        if runner.process:
            runner.process.kill()
        print("Stopped.")