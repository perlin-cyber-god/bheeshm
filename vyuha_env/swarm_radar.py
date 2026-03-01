import pygame
import random
import math

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 600
FPS = 30
NUM_DRONES = 5

# Colors (Tactical Radar Theme)
BG_COLOR = (10, 15, 20)        # Dark blue/black
GRID_COLOR = (0, 50, 0)        # Dark green radar grid
NODE_COLOR = (0, 255, 0)       # Green (Normal Drone)
MASTER_COLOR = (255, 50, 50)   # Red (Master Drone)
DEAD_COLOR = (50, 50, 50)      # Gray (Dead Drone)
LINK_COLOR = (0, 150, 255)     # Blue (RF Communication Link)

class Drone:
    def __init__(self, drone_id):
        self.id = drone_id
        self.x = random.randint(100, WIDTH - 100)
        self.y = random.randint(100, HEIGHT - 100)
        self.vx = random.uniform(-1, 1) # Velocity X
        self.vy = random.uniform(-1, 1) # Velocity Y
        self.battery = random.randint(50, 100) # Used for electing a new master
        self.is_alive = True
        self.is_master = False

    def move(self):
        if not self.is_alive:
            return # Dead drones fall to the ground / stop moving
        
        # Make them drift around like they are flying
        self.x += self.vx
        self.y += self.vy
        
        # Bounce off the walls
        if self.x <= 0 or self.x >= WIDTH: self.vx *= -1
        if self.y <= 0 or self.y >= HEIGHT: self.vy *= -1

def elect_new_master(drones):
    # Find all living drones
    alive_drones = [d for d in drones if d.is_alive]
    if not alive_drones:
        print("CRITICAL: All drones destroyed. Swarm offline.")
        return None
    
    # AI Logic: The drone with the highest battery becomes the new master
    new_master = max(alive_drones, key=lambda d: d.battery)
    new_master.is_master = True
    print(f"MESH HEALED: Drone {new_master.id} elected as new Master (Battery: {new_master.battery}%)")
    return new_master

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("VYUHA: Swarm Digital Twin")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 15, bold=True)

    # Initialize Swarm
    swarm = [Drone(i) for i in range(1, NUM_DRONES + 1)]
    
    # Force Drone 1 to be the initial master
    swarm[0].is_master = True
    master_node = swarm[0]
    print(f"INITIALIZED: Drone {master_node.id} is the Master.")

    running = True
    while running:
        screen.fill(BG_COLOR)

        # 1. Event Handling (Listening for our "Kill Switch")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_k: # Press 'K' to Kill the Master
                    if master_node and master_node.is_alive:
                        print(f"ALERT: Master Drone {master_node.id} Destroyed!")
                        master_node.is_alive = False
                        master_node.is_master = False
                        # Trigger the Self-Healing algorithm
                        master_node = elect_new_master(swarm)

        # 2. Move Drones
        for drone in swarm:
            drone.move()

        # 3. Draw RF Links (Mesh Network to Master)
        if master_node:
            for drone in swarm:
                if drone.is_alive and not drone.is_master:
                    pygame.draw.line(screen, LINK_COLOR, (drone.x, drone.y), (master_node.x, master_node.y), 2)

        # 4. Draw Drones and Info
        for drone in swarm:
            color = DEAD_COLOR
            if drone.is_alive:
                color = MASTER_COLOR if drone.is_master else NODE_COLOR
            
            pygame.draw.circle(screen, color, (int(drone.x), int(drone.y)), 10)
            
            # Draw Text (ID and Battery)
            info_text = f"ID:{drone.id} B:{drone.battery}%"
            text_surface = font.render(info_text, True, (255, 255, 255))
            screen.blit(text_surface, (drone.x + 12, drone.y - 12))

        # Instructions on screen
        instructions = font.render("Press 'K' to simulate Master Drone being shot down.", True, (200, 200, 200))
        screen.blit(instructions, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()