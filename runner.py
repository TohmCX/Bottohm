import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import sys

BOT_FILE = "bottohm.py"   # your bot file
CHECK_INTERVAL = 1       # seconds

class ReloadHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_bot()

    def start_bot(self):
        if self.process:
            self.process.kill()
        self.process = subprocess.Popen([sys.executable, BOT_FILE])
        print("Bot started...")

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"{event.src_path} changed locally. Restarting bot...")
            self.start_bot()

def get_commit_hash():
    result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    return result.stdout.strip()

def git_pull():
    """Pull and return True if commit hash changes"""
    before = get_commit_hash()
    subprocess.run(["git", "pull"], capture_output=True, text=True)
    after = get_commit_hash()
    return before != after

if __name__ == "__main__":
    event_handler = ReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(CHECK_INTERVAL)
            if git_pull():
                print("New commit detected. Restarting bot...")
                event_handler.start_bot()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()