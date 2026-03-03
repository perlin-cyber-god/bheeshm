import pygame
import socket
import csv
import time
import random

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
WIDTH, HEIGHT = 1000, 750  
FPS = 30
MASTER_ID = 1 
HEARTBEAT_TIMEOUT = 3.0 

# Colors
WHITE = (255, 255, 255)
RED = (255, 50, 50)       
ORANGE = (255, 165, 0)    
CYAN = (0, 255, 255)      
VIRTUAL_BLUE = (0, 150, 255) # Color for simulated nodes

class Drone:
    def __init__(self, drone_id, start_x, start_y):
        self.id = drone_id
        self.x, self.y = start_x, start_y
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.battery = 100
        self.is_physical = False # Tracks if real hardware is talking
        self.last_seen = 0
        self.is_alive = True
        self.is_master = False

    def simulate_behavior(self, master_id):
        """Moves the drone autonomously when no hardware is connected."""
        # 1. Battery drain simulation
        if random.random() < 0.01:
            self.battery = max(0, self.battery - 1)

        # 2. Movement Logic (Stay in Sectors)
        self.x += self.vx
        self.y += self.vy

        # Define Sector Bounds
        # Drone 1 stays in Alpha (Left), Drone 2 in Bravo (Right)
        if self.id == 1:
            min_x, max_x = 50, 450
        else:
            min_x, max_x = 550, 950
            
        # Bounce off boundaries
        if self.x < min_x or self.x > max_x: self.vx *= -1
        if self.y < 50 or self.y > HEIGHT - 50: self.vy *= -1
        
        # Jitter movement to look like a real flight controller
        self.vx += random.uniform(-0.1, 0.1)
        self.vy += random.uniform(-0.1, 0.1)
        self.vx = max(-2, min(2, self.vx))
        self.vy = max(-2, min(2, self.vy))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("BHEESHM: Tactical Simulator (Offline Mode)")
    
    # LOAD ASSETS
    try:
        bg = pygame.image.load("basecamp.png")
        bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    except:
        bg = None

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 18, bold=True)
    small_font = pygame.font.SysFont("arial", 12)

    # Initialize Swarm with starting positions in their respective sectors
    swarm = {
        1: Drone(1, 250, 375), # Center of Alpha
        2: Drone(2, 750, 375)  # Center of Bravo
    }
    global MASTER_ID

    running = True
    try:
        while running:
            current_time = time.time()
            
            # 1. DRAW BACKGROUND & SECTORS
            if bg: screen.blit(bg, (0, 0))
            else: screen.fill((10, 15, 20))
            
            pygame.draw.line(screen, CYAN, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)
            screen.blit(font.render("SECTOR ALPHA", True, CYAN), (50, 20))
            screen.blit(font.render("SECTOR BRAVO", True, CYAN), (WIDTH//2 + 50, 20))

            # 2. CAPTURE UDP DATA (If hardware is plugged in)
            try:
                while True:
                    data, addr = sock.recvfrom(1024)
                    msg = data.decode('utf-8').split(',')
                    if len(msg) == 4:
                        d_id, d_x, d_y, d_bat = int(msg[0]), float(msg[1]), float(msg[2]), int(msg[3])
                        if d_id in swarm:
                            drone = swarm[d_id]
                            drone.x, drone.y, drone.battery = d_x, d_y, d_bat
                            drone.last_seen = current_time
                            drone.is_physical = True # Hardware override active
            except BlockingIOError: pass

            # 3. UPDATE DRONES (Simulate or Use Hardware)
            for d_id, drone in swarm.items():
                # If no hardware packet in 3 seconds, switch to Simulation
                if current_time - drone.last_seen > HEARTBEAT_TIMEOUT:
                    drone.is_physical = False
                    drone.simulate_behavior(MASTER_ID)
                
                # Determine Visual State
                color = RED if d_id == MASTER_ID else (ORANGE if drone.is_physical else VIRTUAL_BLUE)
                status_text = "MASTER (ANCHOR)" if d_id == MASTER_ID else "SCOUT"
                mode_text = "[LIVE]" if drone.is_physical else "[SIMULATED]"

                # 4. DRAWING
                pos = (int(drone.x), int(drone.y))
                pygame.draw.circle(screen, color, pos, 15)
                pygame.draw.circle(screen, WHITE, pos, 15, 2)
                
                label = font.render(f"ID:{d_id} | {status_text}", True, WHITE)
                meta = small_font.render(f"{mode_text} BATT: {drone.battery}%", True, WHITE)
                
                screen.blit(label, (drone.x + 20, drone.y - 20))
                screen.blit(meta, (drone.x + 20, drone.y))

            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False

            pygame.display.flip()
            clock.tick(FPS)
    finally:
        csv_file.close()
        pygame.quit()

if __name__ == "__main__":
    main()