import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import sys

BOT_FILE = "bottohm.py"  # replace with your bot file name

class ReloadHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_bot()

    def start_bot(self):
        if self.process:
            self.process.kill()  # stop previous process
        self.process = subprocess.Popen([sys.executable, BOT_FILE])
        print("Bot started...")

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"{event.src_path} changed. Restarting bot...")
            self.start_bot()

if __name__ == "__main__":
    event_handler = ReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
