import pygame
import math

class Renderer:

    CLEAR_COLOR = (35, 35, 35)

    BLACK_COLOR = (0, 0, 0)

    CAR_BOT_COLOR = (220, 80, 80)
    CAR_AI_COLOR = (80, 80, 220)

    CAR_ARROW_COLOR = (255, 255, 40)

    def __init__(self, width, height, car_size_x, car_size_y, bckg_width, bckg_height, background_file=""):
        self.width = width
        self.height = height
        self.background_file = background_file

        self.car_size_x = car_size_x
        self.car_size_y = car_size_y

        self.background_img = None
        self.background_rect = None

        self.bckg_width = bckg_width
        self.bckg_height = bckg_height

        if len(self.background_file) > 0:
            img = pygame.image.load(background_file)
            img.convert()
            self.background_img = img
            self.background_rect = img.get_rect()
            self.background_rect.center = self.width//2, self.height//2
        

        self.car_ai_surface = pygame.Surface((self.car_size_x, self.car_size_y))
        self.car_ai_surface.set_colorkey(self.BLACK_COLOR)
        self.car_ai_surface.fill(self.CAR_AI_COLOR)
        pygame.draw.polygon(self.car_ai_surface, self.CAR_ARROW_COLOR, [(self.car_size_x*0.5, self.car_size_y*0.2), (self.car_size_x*0.5, self.car_size_y*0.8), (self.car_size_x*0.9, self.car_size_y*0.5)], 1)
        self.car_ai_copy = self.car_ai_surface.copy()
        self.car_ai_copy.set_colorkey(self.BLACK_COLOR)
        self.rect_ai = self.car_ai_copy.get_rect()

        self.car_bot_surface = pygame.Surface((self.car_size_x, self.car_size_y))
        self.car_bot_surface.set_colorkey(self.BLACK_COLOR)
        self.car_bot_surface.fill(self.CAR_BOT_COLOR)
        pygame.draw.polygon(self.car_bot_surface, self.CAR_ARROW_COLOR, [(self.car_size_x*0.5, self.car_size_y*0.2), (self.car_size_x*0.5, self.car_size_y*0.8), (self.car_size_x*0.9, self.car_size_y*0.5)], 1)
        self.car_bot_copy = self.car_bot_surface.copy()
        self.car_bot_copy.set_colorkey(self.BLACK_COLOR)
        self.rect_bot = self.car_bot_copy.get_rect()
    
    def render_reset(self, screen):
        screen.fill(self.CLEAR_COLOR)

    def render_background(self, screen, center_x, center_y):
        if self.bckg_width == self.width and self.bckg_height == self.height:
            self.background_rect.center = (self.width/2), (self.height/2)
        else:
            cx = (self.bckg_width//2) - center_x + self.width//2
            cy = (self.bckg_height//2) - center_y + self.height//2
            self.background_rect.center = max(-(self.bckg_width//2), min((self.bckg_width//2), cx)), max(-(self.bckg_height//2), min((self.bckg_height//2), cy))
        screen.blit(self.background_img, self.background_rect)
    
    def render_car(self, screen, center_x, center_y, px, py, rot, is_ai=True):
        if is_ai:
            image = pygame.transform.rotate(self.car_ai_surface, math.pi/2 - rot*180/math.pi)
        else:
            image = pygame.transform.rotate(self.car_bot_surface, math.pi/2 - rot*180/math.pi)
        cx = max(min(self.bckg_width - self.width//2, center_x), self.width//2)
        cy = max(min(self.bckg_height - self.height//2, center_y), self.height//2)
        fx = - cx + center_x + self.width//2
        fy = - cy + center_y + self.height//2
        pfx = center_x - px
        pfy = center_y - py
        rect = image.get_rect(center = (int(fx - pfx), int(fy - pfy)))
        screen.blit(image, rect)

