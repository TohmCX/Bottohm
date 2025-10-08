import requests
import subprocess

url = "http://192.168.1.9/bottohm.py"  # replace with your phone's IP
r = requests.get(url)
with open("bottohm.py", "w") as f:
    f.write(r.text)

# Run the latest version
subprocess.run(["python3", "bottohm.py"])