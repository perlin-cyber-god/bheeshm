import pygame
import random
import socket

# --- NETWORK CONFIGURATION ---
UDP_IP = "0.0.0.0"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False) # CRITICAL: Tells the socket not to freeze the radar screen

# --- RADAR CONFIGURATION ---
WIDTH, HEIGHT = 800, 600
FPS = 30
NUM_DRONES = 5

BG_COLOR = (10, 15, 20)
NODE_COLOR = (0, 255, 0)       # Green (Fake Drone)
REAL_COLOR = (255, 150, 0)     # Orange (YOUR PHYSICAL ESP-12F)
MASTER_COLOR = (255, 50, 50)   # Red (Master)
LINK_COLOR = (0, 150, 255)

class Drone:
    def __init__(self, drone_id):
        self.id = drone_id
        self.x = random.randint(100, WIDTH - 100)
        self.y = random.randint(100, HEIGHT - 100)
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.battery = random.randint(50, 100)
        self.is_alive = True
        self.is_master = False
        self.is_physical = False # Tracks if it's the ESP-12F

    def move(self):
        if not self.is_alive or self.is_physical:
            return # Dead drones stop, and PHYSICAL drones are moved by UDP, not math!
        
        self.x += self.vx
        self.y += self.vy
        if self.x <= 0 or self.x >= WIDTH: self.vx *= -1
        if self.y <= 0 or self.y >= HEIGHT: self.vy *= -1

def elect_new_master(drones):
    alive_drones = [d for d in drones if d.is_alive]
    if not alive_drones: return None
    new_master = max(alive_drones, key=lambda d: d.battery)
    new_master.is_master = True
    return new_master

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("VYUHA: Live Hardware-in-the-Loop Radar")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 15, bold=True)

    swarm = [Drone(i) for i in range(1, NUM_DRONES + 1)]
    swarm[0].is_master = True
    master_node = swarm[0]

    running = True
    while running:
        screen.fill(BG_COLOR)

        # 1. Listen to the Airwaves (ESP-12F UDP Data)
        try:
            while True: # Drain all incoming packets
                data, addr = sock.recvfrom(1024)
                message = data.decode('utf-8')
                parts = message.split(',')
                
                if len(parts) == 4:
                    d_id = int(parts[0])
                    d_x = float(parts[1])
                    d_y = float(parts[2])
                    d_bat = int(parts[3])
                    
                    # Find the drone and update it physically
                    for drone in swarm:
                        if drone.id == d_id:
                            drone.x = d_x
                            drone.y = d_y
                            drone.battery = d_bat
                            drone.is_physical = True
        except BlockingIOError:
            pass # No UDP packets right now, just keep drawing the screen

        # 2. Key Presses (Kill Switch)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_k: 
                    if master_node and master_node.is_alive:
                        master_node.is_alive = False
                        master_node.is_master = False
                        master_node = elect_new_master(swarm)

        # 3. Move Fake Drones & Draw Links
        for drone in swarm: drone.move()
        if master_node:
            for drone in swarm:
                if drone.is_alive and not drone.is_master:
                    pygame.draw.line(screen, LINK_COLOR, (drone.x, drone.y), (master_node.x, master_node.y), 2)

        # 4. Draw Drones
        for drone in swarm:
            color = (50, 50, 50)
            if drone.is_alive:
                if drone.is_master: color = MASTER_COLOR
                elif drone.is_physical: color = REAL_COLOR # Make ESP-12F Orange!
                else: color = NODE_COLOR
            
            pygame.draw.circle(screen, color, (int(drone.x), int(drone.y)), 10)
            text_surface = font.render(f"ID:{drone.id} B:{drone.battery}%", True, (255, 255, 255))
            screen.blit(text_surface, (drone.x + 12, drone.y - 12))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()