import pygame
import random
import socket
import csv
import time

# --- NETWORK & LOGGING CONFIG ---
UDP_IP = "0.0.0.0"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)

# Create/Open CSV file for training data
csv_file = open('swarm_telemetry_data.csv', mode='w', newline='')
csv_writer = csv.writer(csv_file)
# Header: ID, X, Y, Battery, Label (0=Normal, 1=Attack)
csv_writer.writerow(['node_id', 'pos_x', 'pos_y', 'battery', 'label'])

# --- RADAR CONFIG ---
WIDTH, HEIGHT = 800, 600
FPS = 30
NUM_DRONES = 5
BG_COLOR = (10, 15, 20)
NODE_COLOR = (0, 255, 0)
REAL_COLOR = (255, 150, 0)
MASTER_COLOR = (255, 50, 50)
LINK_COLOR = (0, 150, 255)

class Drone:
    def __init__(self, drone_id):
        self.id = drone_id
        self.x = random.randint(100, WIDTH - 100)
        self.y = random.randint(100, HEIGHT - 100)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)
        self.battery = random.randint(50, 100)
        self.is_alive = True
        self.is_master = False
        self.is_physical = False

    def move(self):
        if not self.is_alive or self.is_physical: return
        self.x += self.vx
        self.y += self.vy
        if self.x <= 0 or self.x >= WIDTH: self.vx *= -1
        if self.y <= 0 or self.y >= HEIGHT: self.vy *= -1

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("BHEESHM: Data Collection Mode")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 15, bold=True)

    swarm = [Drone(i) for i in range(1, NUM_DRONES + 1)]
    swarm[0].is_master = True

    print("[SYSTEM] Recording telemetry to swarm_telemetry_data.csv...")

    running = True
    try:
        while running:
            screen.fill(BG_COLOR)
            
            # 1. Capture and Log UDP Packets
            try:
                while True:
                    data, addr = sock.recvfrom(1024)
                    message = data.decode('utf-8')
                    parts = message.split(',')
                    
                    if len(parts) == 4:
                        d_id = int(parts[0])
                        d_x = float(parts[1])
                        d_y = float(parts[2])
                        d_bat = int(parts[3])

                        # AI TRAINING LOGIC: 
                        # If coordinates are exactly 50,50, we label it as ATTACK (1)
                        # In a real scenario, this would be based on "impossible" movement.
                        label = 1 if (d_x == 50.0 and d_y == 50.0) else 0
                        csv_writer.writerow([d_id, d_x, d_y, d_bat, label])

                        for drone in swarm:
                            if drone.id == d_id:
                                drone.x, drone.y, drone.battery = d_x, d_y, d_bat
                                drone.is_physical = True
            except BlockingIOError:
                pass

            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False

            # Draw Logic
            for drone in swarm:
                drone.move()
                color = MASTER_COLOR if drone.is_master else (REAL_COLOR if drone.is_physical else NODE_COLOR)
                pygame.draw.circle(screen, color, (int(drone.x), int(drone.y)), 10)
                screen.blit(font.render(f"ID:{drone.id}", True, (255, 255, 255)), (drone.x + 12, drone.y - 12))

            pygame.display.flip()
            clock.tick(FPS)
    finally:
        csv_file.close()
        pygame.quit()
        print("[SYSTEM] Data collection complete. File saved.")

if __name__ == "__main__":
    main()