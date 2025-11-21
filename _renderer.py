import pygame
import numpy as np


class Renderer:    
    def __init__(self, main, quality=0.5):
        self.main = main
        self.pov = main.pov
        self.quality = quality
    
    def draw_scene(self):
        # background
        self.main.screen.fill((50, 50, 50))

        triangles = self.main.env.screen_triangles

        for triangle in triangles: # dessin des triangles à l'écran
            pygame.draw.polygon(self.main.screen, triangle[3],  [(float(triangle[i][0]), float(triangle[i][1])) for i in range(3)])