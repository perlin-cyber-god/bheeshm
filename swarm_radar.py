import pygame
import random
import time

# --- CONFIG ---
WIDTH, HEIGHT = 1200, 750 # Extra width for the Sidebar UI
RADAR_WIDTH = 1000
FPS = 30

# Colors
BG_DARK = (5, 10, 15)
UI_PANEL = (20, 30, 40)
CYAN = (0, 255, 255)
GREEN = (0, 255, 100)
RED = (255, 50, 50)
WHITE = (220, 220, 220)

class VirtualDrone:
    def __init__(self, id, start_x, start_y, color):
        self.id = id
        self.x, self.y = start_x, start_y
        self.color = color
        self.battery = 100
        self.path = [] # For breadcrumbs/coverage
        self.target = None # For "Target Pursuit"
        self.angle = random.uniform(0, 360)
        self.speed = 2

    def update(self):
        # 1. Battery Logic
        self.battery -= 0.02
        
        # 2. Movement Logic (Patrol vs Pursuit)
        if self.target:
            # Move towards target
            tx, ty = self.target
            dx, dy = tx - self.x, ty - self.y
            dist = (dx**2 + dy**2)**0.5
            if dist > 5:
                self.x += (dx/dist) * 3
                self.y += (dy/dist) * 3
            else:
                self.target = None # Target reached/cleared
        else:
            # Standard Patrol Logic
            self.x += random.uniform(-2, 2)
            self.y += random.uniform(-2, 2)

        # Stay in bounds
        self.x = max(50, min(RADAR_WIDTH-50, self.x))
        self.y = max(50, min(HEIGHT-50, self.y))
        
        # Record path for heatmap/coverage
        if len(self.path) > 50: self.path.pop(0)
        self.path.append((int(self.x), int(self.y)))

def draw_sidebar(screen, drones, targets):
    pygame.draw.rect(screen, UI_PANEL, (RADAR_WIDTH, 0, 200, HEIGHT))
    pygame.draw.line(screen, CYAN, (RADAR_WIDTH, 0), (RADAR_WIDTH, HEIGHT), 2)
    
    font = pygame.font.SysFont("monospace", 16, bold=True)
    screen.blit(font.render("BHEESHM C2", True, CYAN), (RADAR_WIDTH+40, 20))
    
    y_offset = 80
    for d in drones:
        # Battery Bars
        screen.blit(font.render(f"DRONE {d.id}", True, WHITE), (RADAR_WIDTH+20, y_offset))
        pygame.draw.rect(screen, (50, 50, 50), (RADAR_WIDTH+20, y_offset+25, 160, 10))
        bar_color = GREEN if d.battery > 50 else (RED if d.battery < 20 else (255, 255, 0))
        pygame.draw.rect(screen, bar_color, (RADAR_WIDTH+20, y_offset+25, 1.6*d.battery, 10))
        y_offset += 70

    # Threat List
    screen.blit(font.render("THREATS DETECTED", True, RED), (RADAR_WIDTH+10, 400))
    for i, t in enumerate(targets):
        screen.blit(font.render(f"OBJ-{i}: {int(t[0])},{int(t[1])}", True, WHITE), (RADAR_WIDTH+20, 430 + (i*25)))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("BHEESHM: Advanced Tactical Digital Twin")
    
    try:
        bg = pygame.image.load("basecamp.png")
        bg = pygame.transform.scale(bg, (RADAR_WIDTH, HEIGHT))
    except:
        bg = None

    drones = [
        VirtualDrone(1, 200, 300, RED),
        VirtualDrone(2, 700, 400, (255, 165, 0))
    ]
    
    targets = [] # List of (x, y) enemy positions
    clock = pygame.time.Clock()
    running = True

    while running:
        # 1. DRAW BASE
        if bg: screen.blit(bg, (0, 0))
        else: screen.fill(BG_DARK)

        # 2. TARGET GENERATION (Simulate an "Enemy" appearing)
        if random.random() < 0.005 and len(targets) < 5:
            targets.append((random.randint(100, RADAR_WIDTH-100), random.randint(100, HEIGHT-100)))

        # 3. UPDATE & DRAW DRONES
        for d in drones:
            d.update()
            
            # Check for nearest target
            if not d.target and targets:
                d.target = targets[0] # Simplest logic: go to the first target

            # Draw Search Trail (Heatmap Effect)
            for p in d.path:
                pygame.draw.circle(screen, d.color, p, 2, 0)

            # Draw Drone
            pygame.draw.circle(screen, d.color, (int(d.x), int(d.y)), 12)
            pygame.draw.circle(screen, WHITE, (int(d.x), int(d.y)), 12, 2)
            
            # Scanning Radius (The AI "Eye")
            pygame.draw.circle(screen, d.color, (int(d.x), int(d.y)), 80, 1)

            # Check if target is cleared (Drone within 80px range)
            if d.target and ((d.x - d.target[0])**2 + (d.y - d.target[1])**2)**0.5 < 80:
                if d.target in targets: targets.remove(d.target)

        # 4. DRAW TARGETS
        for t in targets:
            pygame.draw.line(screen, RED, (t[0]-10, t[1]-10), (t[0]+10, t[1]+10), 3)
            pygame.draw.line(screen, RED, (t[0]+10, t[1]-10), (t[0]-10, t[1]+10), 3)

        # 5. UI PANEL
        draw_sidebar(screen, drones, targets)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()