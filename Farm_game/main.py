import pygame
import sys
import json
from settings import *
from player import Player
from inventory import Inventory
from crafting import Crafting
from world import World
from animal import Animal
from npc import NPC
from time_system import TimeSystem
from ui import UI
from plot_system import PlotSystem

class FarmGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pixel Farm - Harvest Valley")
        self.clock = pygame.time.Clock()
        
        # Game objects
        self.player = Player((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 ))
        self.world = World()
        self.world.create_default_map()
        
        # Animals
        self.animals = pygame.sprite.Group()
        self.animals.add(Animal((300, 300), "chicken"))
        self.animals.add(Animal((350, 320), "chicken"))
        self.animals.add(Animal((500, 400), "cow"))
        
        # NPCs
        self.npcs = pygame.sprite.Group()
        self.shopkeeper = NPC((100, 150), "shopkeeper")
        self.mayor = NPC((SCREEN_WIDTH - 100, 150), "mayor")
        self.npcs.add(self.shopkeeper, self.mayor)
        
        # Show welcome message
        self.show_notification("Welcome! Press F near Shopkeeper to trade!")
        self.notification_timer = 300  # Show for 5 seconds
        
        # Systems
        self.inventory = Inventory()
        self.crafting = Crafting()
        self.time_system = TimeSystem()
        self.ui = UI()
        self.plot_system = PlotSystem()
        
        # Game state
        self.show_grid = False
        self.notification = ""
        self.notification_timer = 0
        self.paused = False
        
        # Interaction
        self.nearby_npc = None
        self.nearby_animal = None
        self.interaction_distance = 60  # Pixel distance for F key interaction
        
        self.font = pygame.font.Font(None, 24)
        
    def handle_events(self):
        """Handle all game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_game()
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.KEYDOWN:
                # F key - Interact with nearby NPCs/Animals
                if event.key == pygame.K_f:
                    if self.nearby_npc:
                        self.interact_with_npc(self.nearby_npc)
                    elif self.nearby_animal:
                        self.interact_with_animal(self.nearby_animal)
                
                # L key - Toggle plot lock at mouse position
                elif event.key == pygame.K_l:
                    mouse_pos = pygame.mouse.get_pos()
                    grid_x = mouse_pos[0] // TILE_SIZE
                    grid_y = mouse_pos[1] // TILE_SIZE
                    grid_pos = (grid_x, grid_y)
                    
                    if self.plot_system.is_claimed(grid_pos):
                        success, message = self.plot_system.toggle_lock(grid_pos)
                        if message:
                            self.show_notification(message)
                
                # Tool selection
                elif event.key == pygame.K_t:
                    self.player.change_tool()
                    self.show_notification(f"Tool: {self.player.current_tool.replace('_', ' ').title()}")
                    
                # Hotbar selection (1-5)
                elif event.key == pygame.K_1:
                    self.inventory.selected_hotbar_slot = 0
                elif event.key == pygame.K_2:
                    self.inventory.selected_hotbar_slot = 1
                elif event.key == pygame.K_3:
                    self.inventory.selected_hotbar_slot = 2
                elif event.key == pygame.K_4:
                    self.inventory.selected_hotbar_slot = 3
                elif event.key == pygame.K_5:
                    self.inventory.selected_hotbar_slot = 4
                    
                # Toggle systems
                elif event.key == pygame.K_e:
                    self.inventory.toggle_inventory()
                elif event.key == pygame.K_c:
                    self.crafting.toggle_menu()
                elif event.key == pygame.K_i:
                    self.show_grid = not self.show_grid
                elif event.key == pygame.K_h:
                    self.show_notification("Shopkeeper is in top-left area with 'SHOP' label!")
                    
                # Close shop with ESC
                elif event.key == pygame.K_ESCAPE:
                    if self.shopkeeper.shop_mode:
                        self.shopkeeper.shop_mode = None
                    else:
                        self.save_game()
                        pygame.quit()
                        sys.exit()
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Handle inventory clicks first
                if self.inventory.show_full_inventory and event.button == 1:
                    if self.inventory.handle_inventory_click(mouse_pos):
                        continue
                
                # Don't process tool/interact clicks if inventory is open
                if self.inventory.show_full_inventory:
                    continue
                
                # Handle crafting menu clicks
                if self.crafting.show_menu and event.button == 1:
                    if self.crafting.handle_click(mouse_pos, self.inventory):
                        self.show_notification("Item crafted!")
                        
                # Handle shop clicks
                elif self.shopkeeper.shop_mode and event.button == 1:
                    action, result, message = self.shopkeeper.handle_shop_click(
                        mouse_pos, self.player, self.inventory
                    )
                    if message:
                        self.show_notification(message)
                    
                # Left click - use tool
                elif event.button == 1 and not self.crafting.show_menu:
                    self.use_tool(mouse_pos)
                    
                # Right click - claim or sell plots
                elif event.button == 3:
                    if self.shopkeeper.shop_mode:
                        self.shopkeeper.shop_mode = None
                    else:
                        grid_x = mouse_pos[0] // TILE_SIZE
                        grid_y = mouse_pos[1] // TILE_SIZE
                        grid_pos = (grid_x, grid_y)
                        
                        # Check if plot is already claimed - if so, try to sell
                        if self.plot_system.is_claimed(grid_pos):
                            success, message = self.plot_system.sell_plot(grid_pos, self.player, self.world)
                            if message:
                                self.show_notification(message)
                        else:
                            # Try to claim plot
                            success, message = self.plot_system.claim_plot(grid_pos, self.player, self.world)
                            if success or message:
                                self.show_notification(message)
    
    def check_nearby_entities(self):
        """Check for nearby NPCs and animals for F key interaction"""
        player_pos = pygame.math.Vector2(self.player.rect.center)
        
        # Check NPCs
        self.nearby_npc = None
        for npc in self.npcs:
            npc_pos = pygame.math.Vector2(npc.rect.center)
            distance = player_pos.distance_to(npc_pos)
            if distance <= self.interaction_distance:
                self.nearby_npc = npc
                break
        
        # Check animals (only if no NPC nearby)
        self.nearby_animal = None
        if not self.nearby_npc:
            for animal in self.animals:
                animal_pos = pygame.math.Vector2(animal.rect.center)
                distance = player_pos.distance_to(animal_pos)
                if distance <= self.interaction_distance:
                    self.nearby_animal = animal
                    break
    
    def interact_with_npc(self, npc):
        """Interact with an NPC"""
        dialogue = npc.talk()
        # Shop is now handled through the NPC's shop_mode
    
    def interact_with_animal(self, animal):
        """Interact with an animal"""
        # Try to collect product first
        product, value = animal.collect_product()
        if product:
            self.inventory.add_item(product, 1)
            self.show_notification(f"Collected {product}! Sell to shopkeeper!")
        else:
            # Feed animal if no product
            animal.feed()
            self.show_notification(f"Fed {animal.animal_type}!")
                        
    def use_tool(self, pos):
        """Use the currently equipped tool"""
        tool = self.player.current_tool
        
        if tool == "hoe":
            # Till soil - ONLY on claimed plots
            grid_x = pos[0] // TILE_SIZE
            grid_y = pos[1] // TILE_SIZE
            grid_pos = (grid_x, grid_y)
            
            if not self.plot_system.is_claimed(grid_pos):
                self.show_notification("Must claim plot first! (Right-click grass)")
                return
            
            if self.player.use_energy(5):
                if self.world.till(pos):
                    self.show_notification("Soil tilled!")
                    
        elif tool == "watering_can":
            # Water crops and soil
            if self.player.use_energy(3):
                if self.world.water(pos):
                    self.show_notification("Watered!")
                    
        elif tool == "hand":
            # Plant or harvest
            crop_type = self.inventory.get_selected_seed()
            if crop_type:
                seed_name = f"{crop_type}_seed"
                if self.inventory.use(seed_name):
                    if self.world.plant(pos, crop_type):
                        self.show_notification(f"Planted {crop_type}!")
                    else:
                        # Refund seed if planting failed
                        self.inventory.add_item(seed_name, 1)
            else:
                # Try to harvest - NO direct money, just add to inventory
                crop_type, value = self.world.harvest(pos)
                if crop_type:
                    self.inventory.add_item(crop_type, 1)
                    self.show_notification(f"Harvested {crop_type}! Sell to shopkeeper!")
                    
        elif tool == "axe":
            # Chop trees for wood
            tile = self.world.get_tile_at_pos(pos)
            if tile and tile.kind == "T" and self.player.use_energy(10):
                self.inventory.add_item("wood", 3)
                self.show_notification("Chopped wood! +3 wood")
                
        elif tool == "scythe":
            # Clear grass
            tile = self.world.get_tile_at_pos(pos)
            if tile and tile.kind == "G" and self.player.use_energy(2):
                self.show_notification("Cleared grass!")
                
    def show_notification(self, message):
        """Show a notification message"""
        self.notification = message
        self.notification_timer = 120  # 2 seconds at 60 FPS
        
    def update(self, dt):
        """Update all game systems"""
        if self.paused:
            return
            
        keys = pygame.key.get_pressed()
        
        # Update systems
        self.player.update(keys, dt)
        self.world.update()
        self.time_system.update(dt)
        
        # Check for nearby entities
        self.check_nearby_entities()
        
        # Update animals
        for animal in self.animals:
            animal.update(dt)
            
        # Update NPCs
        for npc in self.npcs:
            npc.update(dt)
            
        # Update notification
        if self.notification_timer > 0:
            self.notification_timer -= 1
            if self.notification_timer == 0:
                self.notification = ""
                
    def draw(self):
        """Draw everything"""
        # Clear screen
        self.screen.fill(BLACK)
        
        # Draw world
        self.world.tiles.draw(self.screen)
        
        # Draw claimed plot indicators
        self.plot_system.draw_claimed_indicators(self.screen)
        
        # Draw grid if enabled
        if self.show_grid:
            self.world.draw_grid(self.screen)
            
        # Draw crops
        self.world.crops.draw(self.screen)
        
        # Draw crop status indicators
        for crop in self.world.crops:
            crop.draw_status(self.screen)
        
        # Draw animals
        self.animals.draw(self.screen)
        for animal in self.animals:
            animal.draw_status(self.screen)
            
        # Draw NPCs
        self.npcs.draw(self.screen)
        for npc in self.npcs:
            npc.draw_label(self.screen)
            npc.draw_dialogue(self.screen)
            
        # Draw player
        self.screen.blit(self.player.image, self.player.rect)
        
        # Draw interaction prompt
        if self.nearby_npc:
            self.draw_interaction_prompt(self.nearby_npc.rect.centerx, self.nearby_npc.rect.top - 30, 
                                        f"Press [F] to talk to {self.nearby_npc.npc_type.title()}")
        elif self.nearby_animal:
            action = "Collect" if self.nearby_animal.has_product else "Feed"
            self.draw_interaction_prompt(self.nearby_animal.rect.centerx, self.nearby_animal.rect.top - 30,
                                        f"Press [F] to {action}")
        
        # Draw claimable/sellable plot hint (only if inventory not open)
        if not self.inventory.show_full_inventory:
            mouse_pos = pygame.mouse.get_pos()
            self.plot_system.draw_claimable_hint(self.screen, mouse_pos, self.world, self.player)
        
        # Apply darkness for night
        if self.time_system.is_night():
            darkness = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            darkness.set_alpha(self.time_system.get_darkness_alpha())
            darkness.fill((0, 0, 40))
            self.screen.blit(darkness, (0, 0))
            
        # Draw UI
        self.ui.draw_player_stats(self.screen, self.player, self.time_system)
        self.ui.draw_controls(self.screen)
        
        # Draw inventory (hotbar always visible, full inventory when toggled)
        self.inventory.draw(self.screen)
        
        # Draw crafting menu
        self.crafting.draw_menu(self.screen, self.inventory)
        
        # Draw shop menus
        if self.shopkeeper.shop_mode:
            self.shopkeeper.draw_shop_menu(self.screen)
            self.shopkeeper.draw_buy_menu(self.screen, self.player.money)
            self.shopkeeper.draw_sell_menu(self.screen, self.inventory, self.player.money)
                
        # Draw notification
        if self.notification:
            self.ui.draw_notification(self.screen, self.notification)
            
        # Update display
        pygame.display.flip()
    
    def draw_interaction_prompt(self, x, y, text):
        """Draw interaction prompt above entity"""
        prompt_font = pygame.font.Font(None, 18)
        text_surface = prompt_font.render(text, True, WHITE)
        
        # Background
        padding = 6
        bg_width = text_surface.get_width() + padding * 2
        bg_height = text_surface.get_height() + padding * 2
        bg_x = x - bg_width // 2
        bg_y = y
        
        bg = pygame.Surface((bg_width, bg_height))
        bg.set_alpha(220)
        bg.fill((40, 40, 40))
        self.screen.blit(bg, (bg_x, bg_y))
        
        # Border
        pygame.draw.rect(self.screen, YELLOW, (bg_x, bg_y, bg_width, bg_height), 2)
        
        # Text
        text_x = bg_x + padding
        text_y = bg_y + padding
        self.screen.blit(text_surface, (text_x, text_y))
        
    def save_game(self):
        """Save game state"""
        save_data = {
            "player": {
                "pos": self.player.rect.center,
                "money": self.player.money,
                "energy": self.player.energy
            },
            "inventory": self.inventory.items,
            "hotbar": self.inventory.hotbar,
            "time": {
                "time": self.time_system.time,
                "day": self.time_system.day,
                "season": self.time_system.season
            },
            "plots": self.plot_system.save_data()
        }
        
        try:
            with open("save_game.json", "w") as f:
                json.dump(save_data, f, indent=2)
            print("Game saved!")
        except Exception as e:
            print(f"Error saving game: {e}")
            
    def load_game(self):
        """Load game state"""
        try:
            with open("save_game.json", "r") as f:
                save_data = json.load(f)
                
            # Restore player
            self.player.rect.center = tuple(save_data["player"]["pos"])
            self.player.money = save_data["player"]["money"]
            self.player.energy = save_data["player"]["energy"]
            
            # Restore inventory
            self.inventory.items = save_data["inventory"]
            
            # Restore hotbar
            if "hotbar" in save_data:
                self.inventory.hotbar = save_data["hotbar"]
            
            # Restore time
            self.time_system.time = save_data["time"]["time"]
            self.time_system.day = save_data["time"]["day"]
            self.time_system.season = save_data["time"]["season"]
            
            # Restore plots
            if "plots" in save_data:
                self.plot_system.load_data(save_data["plots"])
            
            print("Game loaded!")
            return True
        except FileNotFoundError:
            print("No save file found, starting new game")
            return False
        except Exception as e:
            print(f"Error loading game: {e}")
            return False
            
    def run(self):
        """Main game loop"""
        # Try to load save
        self.load_game()
        
        while True:
            dt = self.clock.tick(FPS) / 16.67  # Normalize to 60 FPS
            
            self.handle_events()
            self.update(dt)
            self.draw()

if __name__ == "__main__":
    game = FarmGame()
    game.run()