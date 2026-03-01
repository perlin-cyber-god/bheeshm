import socket

# --- RADAR LISTENING POST ---
UDP_IP = "0.0.0.0"  # Listen to all incoming Wi-Fi traffic
UDP_PORT = 5005     # The exact port your ESP-12F is shooting at

# Setup the UDP Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"[SYSTEM] Listening for Swarm Telemetry on port {UDP_PORT}...")

while True:
    # Wait for a packet to hit the antenna
    data, addr = sock.recvfrom(1024) 
    message = data.decode('utf-8')
    
    # Print what we caught!
    print(f"[{addr[0]}] INCOMING: {message}")