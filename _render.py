import pygame
import numpy as np


class Render:
    def __init__(self, main):
        """formalités"""
        self.main = main
        self.pov = self.main.pov

        """buffer réel"""
        self.quality = 0.02 # réglage de la qualité (max 1)
        self.pixels_width = int(self.main.screen_width * self.quality)
        self.pixels_height = int(self.main.screen_height * self.quality)
        self.pixels = [[(255, 255, 255) for x in range(self.pixels_width)] for y in range(self.pixels_height)]

    def update(self):
        self.update_pixels()
        self.blit_pixels()
    
    def blit_pixels(self):
        """affichage des pixels à l'écran"""
        # conversion ton buffer en array numpy
        array = np.array(self.pixels, dtype=np.uint8)
        array = np.transpose(array, (1, 0, 2)) # inversion width height

        # transformation en surface temporaire
        surface = pygame.surfarray.make_surface(array)
        scaled_surface = pygame.transform.scale(surface, (self.main.screen_width, self.main.screen_height))

        # affichage
        self.main.screen.blit(scaled_surface, (0, 0))

    def update_pixels(self):
        """actualise les pixels"""
        ratio_w = self.pov.width / self.pixels_width
        ratio_h = self.pov.height / self.pixels_height
        for i in range(len(self.pixels)):
            for j in range(len(self.pixels[i])):
                self.pov.get_pixel(round(i * ratio_h), round(j * ratio_w))
