import pygame
import socket
import csv
import time

# --- NETWORK & LOGGING CONFIG ---
UDP_IP = "0.0.0.0"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)

# Data Logging
csv_file = open('swarm_telemetry_data.csv', mode='w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['node_id', 'pos_x', 'pos_y', 'battery', 'label'])

# --- UI CONFIG ---
WIDTH, HEIGHT = 1000, 750  # Increased resolution for tactical view
FPS = 30
MASTER_ID = 1 # Initial Master (Raspberry Pi)
HEARTBEAT_TIMEOUT = 3.0 # Seconds before a drone is considered "Down"

# Colors
WHITE = (255, 255, 255)
RED = (255, 50, 50)       # Master
ORANGE = (255, 165, 0)    # Active Node
CYAN = (0, 255, 255)      # Sector UI
GRAY = (100, 100, 100)    # Offline

class Drone:
    def __init__(self, drone_id):
        self.id = drone_id
        self.x, self.y = 0, 0
        self.battery = 100
        self.is_physical = False
        self.last_seen = 0
        self.is_alive = False
        self.is_master = False

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("BHEESHM: Tactical Swarm Anchor (ZedBoard HIL)")
    
    # LOAD ASSETS
    try:
        bg = pygame.image.load("basecamp.png")
        bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    except:
        print("Error: basecamp.png not found. Using dark background.")
        bg = None

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 18, bold=True)
    small_font = pygame.font.SysFont("arial", 12)

    # Initialize Swarm (Nodes 1 and 2 are our physical RPi and ESP)
    swarm = {1: Drone(1), 2: Drone(2)}
    global MASTER_ID

    print("[SYSTEM] Tactical Overlay Active. Listening for packets...")

    running = True
    try:
        while running:
            # 1. DRAW BACKGROUND & SECTORS
            if bg:
                screen.blit(bg, (0, 0))
            else:
                screen.fill((10, 15, 20))
            
            # Draw Sector Divider (Alpha/Bravo)
            pygame.draw.line(screen, CYAN, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)
            screen.blit(font.render("SECTOR ALPHA", True, CYAN), (50, 20))
            screen.blit(font.render("SECTOR BRAVO", True, CYAN), (WIDTH//2 + 50, 20))

            # 2. CAPTURE & LOG DATA
            current_time = time.time()
            try:
                while True:
                    data, addr = sock.recvfrom(1024)
                    msg = data.decode('utf-8').split(',')
                    
                    if len(msg) == 4:
                        d_id, d_x, d_y, d_bat = int(msg[0]), float(msg[1]), float(msg[2]), int(msg[3])
                        
                        # Labeling for AI Training
                        label = 1 if (d_x == 50.0 and d_y == 50.0) else 0
                        csv_writer.writerow([d_id, d_x, d_y, d_bat, label])

                        if d_id in swarm:
                            drone = swarm[d_id]
                            drone.x, drone.y = d_x, d_y
                            drone.battery = d_bat
                            drone.last_seen = current_time
                            drone.is_alive = True
            except BlockingIOError:
                pass

            # 3. SELF-HEALING LOGIC (Master Election)
            # If current Master is offline, elect the other node
            if swarm[MASTER_ID].is_alive and (current_time - swarm[MASTER_ID].last_seen > HEARTBEAT_TIMEOUT):
                print(f"[ALERT] MASTER NODE {MASTER_ID} LOST. ELECTING NEW ANCHOR...")
                swarm[MASTER_ID].is_alive = False
                # Simple flip logic for 2-node demo
                MASTER_ID = 2 if MASTER_ID == 1 else 1 

            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False

            # 4. DRAW DRONES & TELEMETRY
            for d_id, drone in swarm.items():
                if not drone.is_alive: continue
                
                # Check for "Death" timeout
                if current_time - drone.last_seen > HEARTBEAT_TIMEOUT:
                    drone.is_alive = False
                    continue

                # Determine Color
                color = RED if d_id == MASTER_ID else ORANGE
                
                # Draw Drone Body
                pos = (int(drone.x), int(drone.y))
                pygame.draw.circle(screen, color, pos, 15)
                pygame.draw.circle(screen, WHITE, pos, 15, 2) # Outline

                # Draw Data Labels
                role_text = "MASTER (ANCHOR)" if d_id == MASTER_ID else "SCOUT"
                label = font.render(f"ID:{d_id} | {role_text}", True, WHITE)
                bat_text = small_font.render(f"BATT: {drone.battery}%", True, WHITE)
                
                screen.blit(label, (drone.x + 20, drone.y - 20))
                screen.blit(bat_text, (drone.x + 20, drone.y))

                # Simulate Video Feed Viewport (Green box around drone)
                pygame.draw.rect(screen, (0, 255, 0), (drone.x-30, drone.y-30, 60, 60), 1)

            pygame.display.flip()
            clock.tick(FPS)
    finally:
        csv_file.close()
        pygame.quit()

if __name__ == "__main__":
    main()