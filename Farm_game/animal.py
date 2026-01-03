import pygame
import random
from settings import *

class Animal(pygame.sprite.Sprite):
    ANIMAL_TYPES = {
        "chicken": {
            "color": (255, 255, 255),
            "size": (20, 18),
            "product": "egg",
            "product_time": 60,
            "product_value": 25,
            "speed": 1.2,
            "wander_radius": 100,
            "feed_cooldown": 180  # 3 seconds at 60 FPS
        },
        "cow": {
            "color": (139, 90, 43),
            "size": (28, 24),
            "product": "milk",
            "product_time": 120,
            "product_value": 30,
            "speed": 0.8,
            "wander_radius": 80,
            "feed_cooldown": 180
        },
        "sheep": {
            "color": (245, 245, 245),
            "size": (24, 20),
            "product": "wool",
            "product_time": 50,
            "product_value": 30,
            "speed": 1.0,
            "wander_radius": 90,
            "feed_cooldown": 180
        }
    }
    
    def __init__(self, pos, animal_type="chicken"):
        super().__init__()
        
        self.animal_type = animal_type
        self.data = self.ANIMAL_TYPES[animal_type]
        
        # Create animal sprite
        width, height = self.data["size"]
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.create_sprite()
        
        self.rect = self.image.get_rect(center=pos)
        
        # Store home position for wandering
        self.home_pos = pygame.math.Vector2(pos)
        self.position = pygame.math.Vector2(pos)
        
        # Movement behavior
        self.speed = self.data["speed"]
        self.base_speed = self.speed
        self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
        
        # Behavior timers
        self.change_direction_timer = 0
        self.change_direction_delay = random.randint(60, 180)
        self.pause_timer = 0
        self.is_paused = random.choice([True, False])
        self.pause_duration = random.randint(30, 120) if self.is_paused else 0
        
        # Movement state
        self.wander_radius = self.data["wander_radius"]
        self.movement_state = random.choice(["wander", "pause", "roam"])
        self.state_timer = random.randint(120, 300)
        
        # Animal state system - proper cycle
        # States: "has_product" -> "needs_feed" -> "cooldown" -> "producing" -> "has_product"
        self.state = "has_product"  # Start with product ready
        self.product_timer = 0
        self.feed_cooldown_timer = 0
        self.feed_cooldown_duration = self.data["feed_cooldown"]
        
        # Legacy support
        self.happiness = 100
        
    def create_sprite(self):
        """Create animal visual representation"""
        color = self.data["color"]
        width, height = self.data["size"]
        
        if self.animal_type == "chicken":
            # Body
            pygame.draw.ellipse(self.image, color, (2, 6, 16, 12))
            # Head
            pygame.draw.circle(self.image, color, (14, 6), 5)
            # Beak
            pygame.draw.polygon(self.image, (255, 165, 0), 
                              [(17, 6), (22, 5), (22, 7)])
            # Eye
            pygame.draw.circle(self.image, BLACK, (15, 5), 1)
            # Comb
            pygame.draw.circle(self.image, RED, (14, 2), 2)
            # Legs
            pygame.draw.line(self.image, (255, 165, 0), (8, 18), (8, 16), 2)
            pygame.draw.line(self.image, (255, 165, 0), (12, 18), (12, 16), 2)
            
        elif self.animal_type == "cow":
            # Body
            pygame.draw.ellipse(self.image, color, (2, 8, 24, 14))
            # Head
            pygame.draw.ellipse(self.image, color, (20, 6, 8, 10))
            # Spots
            pygame.draw.circle(self.image, BLACK, (8, 12), 3)
            pygame.draw.circle(self.image, BLACK, (16, 14), 2)
            # Eyes
            pygame.draw.circle(self.image, BLACK, (24, 9), 1)
            # Horns
            pygame.draw.line(self.image, (200, 200, 200), (22, 6), (20, 4), 2)
            pygame.draw.line(self.image, (200, 200, 200), (26, 6), (28, 4), 2)
            # Legs
            for x in [6, 10, 16, 20]:
                pygame.draw.line(self.image, color, (x, 22), (x, 20), 2)
                
        elif self.animal_type == "sheep":
            # Fluffy body
            pygame.draw.circle(self.image, color, (12, 12), 10)
            pygame.draw.circle(self.image, color, (8, 10), 6)
            pygame.draw.circle(self.image, color, (16, 10), 6)
            # Head (darker)
            pygame.draw.circle(self.image, (50, 50, 50), (18, 8), 4)
            # Eye
            pygame.draw.circle(self.image, BLACK, (19, 7), 1)
            # Legs
            for x in [6, 10, 14, 18]:
                pygame.draw.line(self.image, (50, 50, 50), (x, 20), (x, 18), 2)
    
    def choose_new_direction(self):
        """Choose a new random direction"""
        distance_from_home = self.position.distance_to(self.home_pos)
        
        if distance_from_home > self.wander_radius * 1.5:
            direction_to_home = self.home_pos - self.position
            if direction_to_home.length() > 0:
                self.direction = direction_to_home.normalize()
                self.direction.x += random.uniform(-0.3, 0.3)
                self.direction.y += random.uniform(-0.3, 0.3)
                if self.direction.length() > 0:
                    self.direction = self.direction.normalize()
        else:
            angle = random.uniform(0, 2 * 3.14159)
            self.direction = pygame.math.Vector2(
                random.uniform(-1, 1),
                random.uniform(-1, 1)
            )
            if self.direction.length() > 0:
                self.direction = self.direction.normalize()
    
    def change_movement_state(self):
        """Change between different movement behaviors"""
        states = ["wander", "pause", "roam", "wander", "roam"]
        self.movement_state = random.choice(states)
        
        if self.movement_state == "pause":
            self.is_paused = True
            self.pause_duration = random.randint(30, 120)
            self.pause_timer = 0
            self.speed = 0
        elif self.movement_state == "wander":
            self.is_paused = False
            self.speed = self.base_speed * random.uniform(0.5, 1.0)
            self.choose_new_direction()
        else:
            self.is_paused = False
            self.speed = self.base_speed * random.uniform(0.7, 1.3)
            self.choose_new_direction()
        
        self.state_timer = random.randint(120, 300)
                
    def update(self, dt):
        """Update animal behavior"""
        # State management
        self.state_timer -= 1
        if self.state_timer <= 0:
            self.change_movement_state()
        
        # Animal state machine
        if self.state == "cooldown":
            # Waiting for cooldown to finish after feeding
            self.feed_cooldown_timer -= 1
            if self.feed_cooldown_timer <= 0:
                # Cooldown finished, start producing
                self.state = "producing"
                self.product_timer = 0
                
        elif self.state == "producing":
            # Producing the product
            self.product_timer += dt
            if self.product_timer >= self.data["product_time"]:
                # Product ready!
                self.state = "has_product"
                self.product_timer = 0
                # Brief pause when product is ready
                self.is_paused = True
                self.pause_duration = 30
                self.pause_timer = 0
        
        # Handle pausing
        if self.is_paused:
            self.pause_timer += 1
            if self.pause_timer >= self.pause_duration:
                self.is_paused = False
                self.speed = self.base_speed * random.uniform(0.7, 1.2)
                self.choose_new_direction()
        else:
            # Random movement direction changes
            self.change_direction_timer += 1
            
            if self.change_direction_timer >= self.change_direction_delay:
                self.choose_new_direction()
                self.change_direction_timer = 0
                self.change_direction_delay = random.randint(60, 180)
                
                if random.random() < 0.2:
                    self.is_paused = True
                    self.pause_duration = random.randint(20, 60)
                    self.pause_timer = 0
                    self.speed = 0
            
            # Move using float position for smooth movement
            self.position.x += self.direction.x * self.speed
            self.position.y += self.direction.y * self.speed
            
            # Update rect position from float position
            self.rect.centerx = int(self.position.x)
            self.rect.centery = int(self.position.y)
            
            # Keep on screen with bouncing
            if self.rect.left < 0:
                self.position.x = self.rect.width // 2
                self.direction.x = abs(self.direction.x)
            elif self.rect.right > SCREEN_WIDTH:
                self.position.x = SCREEN_WIDTH - self.rect.width // 2
                self.direction.x = -abs(self.direction.x)
                
            if self.rect.top < 0:
                self.position.y = self.rect.height // 2
                self.direction.y = abs(self.direction.y)
            elif self.rect.bottom > SCREEN_HEIGHT:
                self.position.y = SCREEN_HEIGHT - self.rect.height // 2
                self.direction.y = -abs(self.direction.y)
            
            if (self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH or 
                self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT):
                if random.random() < 0.5:
                    self.choose_new_direction()
            
    def feed(self):
        """Feed the animal - only when in needs_feed state"""
        if self.state == "needs_feed":
            # Start cooldown
            self.state = "cooldown"
            self.feed_cooldown_timer = self.feed_cooldown_duration
            self.happiness = min(100, self.happiness + 20)
            # Brief pause when being fed
            self.is_paused = True
            self.pause_duration = 20
            self.pause_timer = 0
            return True
        return False
        
    def collect_product(self):
        """Collect animal product - only when in has_product state"""
        if self.state == "has_product":
            # Transition to needs_feed state
            self.state = "needs_feed"
            return self.data["product"], self.data["product_value"]
        return None, 0
    
    def can_collect(self):
        """Check if product can be collected"""
        return self.state == "has_product"
    
    def can_feed(self):
        """Check if animal can be fed"""
        return self.state == "needs_feed"
    
    def get_state_info(self):
        """Get human-readable state information"""
        if self.state == "has_product":
            return "Ready to collect!"
        elif self.state == "needs_feed":
            return "Hungry - needs feeding"
        elif self.state == "cooldown":
            time_left = int(self.feed_cooldown_timer / 60)
            return f"Digesting... ({time_left}s)"
        elif self.state == "producing":
            progress = int((self.product_timer / self.data["product_time"]) * 100)
            return f"Producing... ({progress}%)"
        return ""
        
    def draw_status(self, surface):
        """Draw status indicators above animal"""
        if self.state == "has_product":
            # Draw exclamation mark when product ready
            pygame.draw.circle(surface, YELLOW, 
                             (self.rect.centerx, self.rect.top - 10), 4)
            pygame.draw.circle(surface, YELLOW, 
                             (self.rect.centerx, self.rect.top - 16), 2)
                             
        elif self.state == "needs_feed":
            # Draw heart when hungry and needs feeding
            heart_x = self.rect.centerx
            heart_y = self.rect.top - 12
            pygame.draw.circle(surface, RED, (heart_x - 3, heart_y), 3)
            pygame.draw.circle(surface, RED, (heart_x + 3, heart_y), 3)
            pygame.draw.polygon(surface, RED, [
                (heart_x - 6, heart_y),
                (heart_x, heart_y + 6),
                (heart_x + 6, heart_y)
            ])
            
        elif self.state == "cooldown":
            # Draw clock icon when on cooldown (digesting)
            clock_x = self.rect.centerx
            clock_y = self.rect.top - 12
            pygame.draw.circle(surface, GRAY, (clock_x, clock_y), 4)
            pygame.draw.circle(surface, WHITE, (clock_x, clock_y), 4, 1)
            # Clock hand
            pygame.draw.line(surface, WHITE, (clock_x, clock_y), (clock_x, clock_y - 3), 1)
            
        elif self.state == "producing":
            # Draw animated dots when producing
            import time
            dots = int(time.time() * 2) % 4  # 0-3 dots animation
            dot_str = "." * dots
            # Draw small progress indicator
            pygame.draw.circle(surface, (100, 200, 100), 
                             (self.rect.centerx, self.rect.top - 10), 3)