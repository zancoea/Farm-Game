import pygame
from settings import *
from crop import Crop

class Inventory:
    def __init__(self):
        # Main inventory storage (36 slots)
        self.items = {
            "wheat_seed": INITIAL_SEEDS,
            "carrot_seed": 5,
            "tomato_seed": 3,
            "corn_seed": 2,
            "wheat": 0,
            "carrot": 0,
            "tomato": 0,
            "corn": 0,
            "wood": 0,
            "stone": 0,
        }
        
        # Hotbar (5 slots) - stores item names
        self.hotbar = ["wheat_seed", "carrot_seed", "tomato_seed", "corn_seed", None]
        self.selected_hotbar_slot = 0
        
        # UI state
        self.show_full_inventory = False
        self.selected_inventory_item = None
        
        # Fonts
        self.font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 16)
        
        # Item categories for display
        self.item_categories = {
            "Seeds": ["wheat_seed", "carrot_seed", "tomato_seed", "corn_seed"],
            "Crops": ["wheat", "carrot", "tomato", "corn"],
            "Resources": ["wood", "stone"],
            "Products": ["egg", "milk", "wool"],
            "Crafted": ["fence", "scarecrow", "chest"]
        }
        
    def add_item(self, item, amount=1):
        """Add item to inventory"""
        if item in self.items:
            self.items[item] += amount
        else:
            self.items[item] = amount
            
    def remove_item(self, item, amount=1):
        """Remove item from inventory"""
        if item in self.items and self.items[item] >= amount:
            self.items[item] -= amount
            return True
        return False
        
    def has_item(self, item, amount=1):
        """Check if inventory has item"""
        return self.items.get(item, 0) >= amount
        
    def use(self, item):
        """Use one of an item"""
        return self.remove_item(item, 1)
    
    def toggle_inventory(self):
        """Toggle full inventory display"""
        self.show_full_inventory = not self.show_full_inventory
        
    def get_selected_item(self):
        """Get currently selected item from hotbar"""
        selected_item = self.hotbar[self.selected_hotbar_slot]
        if selected_item and self.has_item(selected_item):
            return selected_item
        return None
    
    def get_selected_seed(self):
        """Get currently selected seed type from hotbar"""
        selected_item = self.get_selected_item()
        if selected_item and selected_item.endswith("_seed"):
            return selected_item.replace("_seed", "")
        return None
    
    def set_hotbar_slot(self, slot, item_name):
        """Set an item in a hotbar slot"""
        if 0 <= slot < 5:
            self.hotbar[slot] = item_name
    
    def handle_inventory_click(self, pos, screen_width, screen_height):
        """Handle clicks on the full inventory screen"""
        if not self.show_full_inventory:
            return False
        
        panel_width = min(600, screen_width - 40)
        panel_height = min(600, screen_height - 40)
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        # Check if click is inside panel
        if not (panel_x <= pos[0] <= panel_x + panel_width and 
                panel_y <= pos[1] <= panel_y + panel_height):
            hotbar_result = self.handle_integrated_hotbar_click(pos, panel_x, panel_y, panel_width, panel_height)
            if hotbar_result:
                return True
            return False
        
        # Check inventory grid clicks
        slot_size = min(70, (panel_width - 80) // 6)
        slots_per_row = 6
        start_x = panel_x + 30
        start_y = panel_y + 75
        slot_spacing = 10
        
        slot_index = 0
        all_items = list(self.items.keys())
        
        for row in range(6):
            for col in range(6):
                if slot_index >= len(all_items):
                    break
                
                x = start_x + col * (slot_size + slot_spacing)
                y = start_y + row * (slot_size + slot_spacing)
                
                if x <= pos[0] <= x + slot_size and y <= pos[1] <= y + slot_size:
                    item_name = all_items[slot_index]
                    count = self.items.get(item_name, 0)
                    
                    if count > 0:
                        self.selected_inventory_item = item_name
                        return True
                
                slot_index += 1
        
        hotbar_result = self.handle_integrated_hotbar_click(pos, panel_x, panel_y, panel_width, panel_height)
        if hotbar_result:
            return True
        
        return False
    
    def handle_integrated_hotbar_click(self, pos, panel_x, panel_y, panel_width, panel_height):
        """Handle clicks on integrated hotbar slots"""
        slot_size = 64
        spacing = 8
        total_width = (slot_size * 5) + (spacing * 4)
        start_x = panel_x + (panel_width - total_width) // 2
        start_y = panel_y + panel_height - slot_size - 30
        
        for i in range(5):
            x = start_x + i * (slot_size + spacing)
            y = start_y
            
            if x <= pos[0] <= x + slot_size and y <= pos[1] <= y + slot_size:
                if self.selected_inventory_item:
                    self.hotbar[i] = self.selected_inventory_item
                    self.selected_inventory_item = None
                    return True
                else:
                    self.selected_hotbar_slot = i
                    return True
        
        return False
    
    def handle_hotbar_click(self, pos, screen_width, screen_height):
        """Handle clicks on hotbar slots when inventory is closed"""
        slot_size = 64
        spacing = 8
        total_width = (slot_size * 5) + (spacing * 4)
        start_x = (screen_width - total_width) // 2
        start_y = screen_height - slot_size - 20
        
        for i in range(5):
            x = start_x + i * (slot_size + spacing)
            y = start_y
            
            if x <= pos[0] <= x + slot_size and y <= pos[1] <= y + slot_size:
                self.selected_hotbar_slot = i
                return True
        
        return False
    
    def draw_hotbar(self, surface, screen_width, screen_height):
        """Draw the hotbar at bottom center of screen"""
        slot_size = 64
        spacing = 8
        total_width = (slot_size * 5) + (spacing * 4)
        start_x = (screen_width - total_width) // 2
        start_y = screen_height - slot_size - 20
        
        for i in range(5):
            x = start_x + i * (slot_size + spacing)
            y = start_y
            
            is_selected = i == self.selected_hotbar_slot
            color = (100, 100, 100) if is_selected else (60, 60, 60)
            pygame.draw.rect(surface, color, (x, y, slot_size, slot_size))
            pygame.draw.rect(surface, WHITE if is_selected else GRAY, 
                           (x, y, slot_size, slot_size), 3 if is_selected else 2)
            
            item_name = self.hotbar[i]
            if item_name and item_name in self.items:
                count = self.items.get(item_name, 0)
                
                self.draw_item_icon(surface, item_name, x + slot_size // 2, y + 20)
                
                count_text = self.font.render(str(count), True, WHITE)
                text_bg = pygame.Surface((count_text.get_width() + 4, count_text.get_height() + 2))
                text_bg.fill((0, 0, 0))
                text_bg.set_alpha(180)
                surface.blit(text_bg, (x + 3, y + slot_size - 24))
                surface.blit(count_text, (x + 5, y + slot_size - 22))
                
                display_name = item_name.replace("_", " ").replace(" seed", "").title()
                if len(display_name) > 8:
                    display_name = display_name[:7] + "."
                name_text = self.small_font.render(display_name, True, WHITE)
                name_x = x + slot_size // 2 - name_text.get_width() // 2
                surface.blit(name_text, (name_x, y + 40))
            
            num_text = self.small_font.render(str(i + 1), True, YELLOW if is_selected else GRAY)
            surface.blit(num_text, (x + 4, y + 4))
    
    def draw_integrated_hotbar(self, surface, panel_x, panel_y, panel_width, panel_height):
        """Draw the hotbar integrated into the inventory panel"""
        slot_size = 64
        spacing = 8
        total_width = (slot_size * 5) + (spacing * 4)
        start_x = panel_x + (panel_width - total_width) // 2
        start_y = panel_y + panel_height - slot_size - 30
        
        hotbar_label = self.font.render("Hotbar", True, YELLOW)
        label_x = panel_x + (panel_width - hotbar_label.get_width()) // 2
        surface.blit(hotbar_label, (label_x, start_y - 25))
        
        for i in range(5):
            x = start_x + i * (slot_size + spacing)
            y = start_y
            
            is_selected = i == self.selected_hotbar_slot
            color = (100, 100, 100) if is_selected else (60, 60, 60)
            pygame.draw.rect(surface, color, (x, y, slot_size, slot_size))
            pygame.draw.rect(surface, WHITE if is_selected else GRAY, 
                           (x, y, slot_size, slot_size), 3 if is_selected else 2)
            
            item_name = self.hotbar[i]
            if item_name and item_name in self.items:
                count = self.items.get(item_name, 0)
                
                self.draw_item_icon(surface, item_name, x + slot_size // 2, y + 20)
                
                count_text = self.font.render(str(count), True, WHITE)
                text_bg = pygame.Surface((count_text.get_width() + 4, count_text.get_height() + 2))
                text_bg.fill((0, 0, 0))
                text_bg.set_alpha(180)
                surface.blit(text_bg, (x + 3, y + slot_size - 24))
                surface.blit(count_text, (x + 5, y + slot_size - 22))
                
                display_name = item_name.replace("_", " ").replace(" seed", "").title()
                if len(display_name) > 8:
                    display_name = display_name[:7] + "."
                name_text = self.small_font.render(display_name, True, WHITE)
                name_x = x + slot_size // 2 - name_text.get_width() // 2
                surface.blit(name_text, (name_x, y + 40))
            
            num_text = self.small_font.render(str(i + 1), True, YELLOW if is_selected else GRAY)
            surface.blit(num_text, (x + 4, y + 4))
    
    def draw_full_inventory(self, surface, screen_width, screen_height):
        """Draw the full inventory screen with integrated hotbar - responsive"""
        if not self.show_full_inventory:
            return
        
        # Draw semi-transparent background overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Responsive panel dimensions
        panel_width = min(600, screen_width - 40)
        panel_height = min(600, screen_height - 40)
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        # Draw panel background
        bg = pygame.Surface((panel_width, panel_height))
        bg.fill((40, 40, 40))
        surface.blit(bg, (panel_x, panel_y))
        
        pygame.draw.rect(surface, WHITE, (panel_x, panel_y, panel_width, panel_height), 3)
        
        title = self.title_font.render("Inventory", True, WHITE)
        surface.blit(title, (panel_x + 20, panel_y + 15))
        
        close_text = self.font.render("Press E to close", True, GRAY)
        surface.blit(close_text, (panel_x + panel_width - 150, panel_y + 15))
        
        if self.selected_inventory_item:
            instruction = self.small_font.render(
                f"Selected: {self.selected_inventory_item.replace('_', ' ').title()} - Click hotbar slot to assign",
                True, YELLOW
            )
        else:
            instruction = self.small_font.render(
                "Click item to select, then click hotbar slot to assign",
                True, GRAY
            )
        surface.blit(instruction, (panel_x + 20, panel_y + 45))
        
        # Draw inventory grid with responsive slot size
        slot_size = min(70, (panel_width - 80) // 6)
        slots_per_row = 6
        start_x = panel_x + 30
        start_y = panel_y + 75
        slot_spacing = 10
        
        slot_index = 0
        all_items = list(self.items.keys())
        
        for row in range(6):
            for col in range(6):
                if slot_index >= len(all_items):
                    break
                
                x = start_x + col * (slot_size + slot_spacing)
                y = start_y + row * (slot_size + slot_spacing)
                
                item_name = all_items[slot_index]
                count = self.items.get(item_name, 0)
                is_selected = item_name == self.selected_inventory_item
                
                slot_color = (80, 100, 80) if is_selected else (60, 60, 60)
                pygame.draw.rect(surface, slot_color, (x, y, slot_size, slot_size))
                border_color = YELLOW if is_selected else GRAY
                border_width = 3 if is_selected else 2
                pygame.draw.rect(surface, border_color, (x, y, slot_size, slot_size), border_width)
                
                if count > 0:
                    self.draw_item_icon(surface, item_name, x + slot_size // 2, y + 15)
                    
                    count_text = self.font.render(str(count), True, WHITE)
                    text_bg = pygame.Surface((count_text.get_width() + 4, count_text.get_height() + 2))
                    text_bg.fill((0, 0, 0))
                    text_bg.set_alpha(180)
                    surface.blit(text_bg, (x + 3, y + slot_size - 24))
                    surface.blit(count_text, (x + 5, y + slot_size - 22))
                    
                    display_name = item_name.replace("_", " ").title()
                    if len(display_name) > 9:
                        display_name = display_name[:8] + "."
                    name_text = self.small_font.render(display_name, True, WHITE)
                    name_x = x + slot_size // 2 - name_text.get_width() // 2
                    surface.blit(name_text, (name_x, y + 45))
                else:
                    display_name = item_name.replace("_", " ").title()
                    if len(display_name) > 9:
                        display_name = display_name[:8] + "."
                    name_text = self.small_font.render(display_name, True, (100, 100, 100))
                    name_x = x + slot_size // 2 - name_text.get_width() // 2
                    name_y = y + slot_size // 2 - name_text.get_height() // 2
                    surface.blit(name_text, (name_x, name_y))
                    
                    count_text = self.small_font.render("0", True, (100, 100, 100))
                    surface.blit(count_text, (x + 5, y + slot_size - 20))
                
                slot_index += 1
        
        separator_y = panel_y + panel_height - 120
        pygame.draw.line(surface, GRAY, (panel_x + 20, separator_y), (panel_x + panel_width - 20, separator_y), 2)
        
        self.draw_integrated_hotbar(surface, panel_x, panel_y, panel_width, panel_height)
    
    def draw_item_icon(self, surface, item_name, x, y):
        """Draw an icon for an item"""
        icon_colors = {
            "wheat_seed": (218, 165, 32),
            "carrot_seed": (255, 140, 0),
            "tomato_seed": (255, 50, 50),
            "corn_seed": (255, 215, 0),
            "wheat": (218, 165, 32),
            "carrot": (255, 140, 0),
            "tomato": (255, 50, 50),
            "corn": (255, 215, 0),
            "wood": (139, 69, 19),
            "stone": (128, 128, 128),
            "egg": (255, 255, 200),
            "milk": (255, 255, 255),
            "wool": (245, 245, 245),
            "fence": (139, 69, 19),
            "scarecrow": (218, 165, 32),
            "chest": (101, 67, 33),
        }
        
        color = icon_colors.get(item_name, WHITE)
        
        if item_name.endswith("_seed"):
            pygame.draw.circle(surface, color, (x, y), 8)
            pygame.draw.circle(surface, (0, 0, 0), (x, y), 8, 1)
        elif item_name in ["wheat", "carrot", "tomato", "corn"]:
            pygame.draw.circle(surface, color, (x, y), 12)
            pygame.draw.circle(surface, (255, 255, 255), (x - 3, y - 3), 3)
        elif item_name == "wood":
            pygame.draw.rect(surface, color, (x - 10, y - 8, 20, 16))
            pygame.draw.rect(surface, (101, 67, 33), (x - 10, y - 8, 20, 16), 2)
        elif item_name == "stone":
            points = [(x, y - 10), (x + 10, y), (x, y + 10), (x - 10, y)]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (80, 80, 80), points, 2)
        elif item_name in ["egg", "milk", "wool"]:
            pygame.draw.ellipse(surface, color, (x - 10, y - 8, 20, 16))
            pygame.draw.ellipse(surface, (200, 200, 200), (x - 10, y - 8, 20, 16), 2)
        else:
            pygame.draw.rect(surface, color, (x - 10, y - 10, 20, 20))
            pygame.draw.rect(surface, WHITE, (x - 10, y - 10, 20, 20), 2)
    
    def draw(self, surface, screen_width, screen_height):
        """Draw inventory UI"""
        if self.show_full_inventory:
            self.draw_full_inventory(surface, screen_width, screen_height)
        else:
            self.draw_hotbar(surface, screen_width, screen_height)