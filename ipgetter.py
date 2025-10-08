import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    # connecting to an external server just to get your local IP
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
finally:
    s.close()

print("Local IP:", ip)