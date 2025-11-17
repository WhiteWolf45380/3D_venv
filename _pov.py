import pygame
import math
from _vector import Vector


class Pov:
    def __init__(self, main):
        """formalités"""
        self.main = main
        self.env = self.main.env

        """attributs"""
        # centre POV
        self.pos = Vector(0, 0, 0) # (x, y, z)
        self.vect = Vector(1, 0, 0) # (-x>, -y>, -z>) : valeur max: 1
        self.norm = 0 # distance center -> écran
        self.fov = 80 # degrés

        # écran POV
        self.size = [192]
        self.size.append(int(self.size[0] * self.main.screen_height / self.main.screen_width))
        self.world_up = Vector(0, 1, 0) # vecteur fixe pointant vers le haut
        self.center = Vector()
        self.right = Vector()
        self.up = Vector()
    
    def update(self):
        """miste à jour"""
        self.update_norm()
        self.update_center()
        self.update_right()
        self.update_up()
    
    @property
    def x(self):
        """coordinée x du centre"""
        return self.pos[0]
    
    @property
    def y(self):
        """coordinée y du centre"""
        return self.pos[1]
    
    @property
    def z(self):
        """coordinée z du centre"""
        return self.pos[2]
    
    @property
    def dx(self):
        """vecteur x"""
        return self.vect[0]
    
    @property
    def dy(self):
        """vecteur y"""
        return self.vect[1]
    
    @property
    def dz(self):
        """vecteur z"""
        return self.vect[2]
    
    @property
    def width(self):
        """largeur de l'écran de projection"""
        return self.size[0]
    
    @property
    def height(self):
        """hauteur de l'écran de projection"""
        return self.size[1]
    
    def update_norm(self):
        """calcul de la distance focale"""
        self.norm = self.width / (2 * math.tan(math.radians(self.fov / 2)))
    
    def update_center(self):
        """met à jour le centre de l'écran de projection"""
        self.center[0] = self.x + self.dx * self.norm
        self.center[1] = self.y + self.dy * self.norm
        self.center[2] = self.z + self.dz * self.norm
    
    def update_right(self):
        """met à jour le vecteur vers la droite de l'écran de projection"""
        self.right = self.vect * self.world_up
        self.right.normalize()
    
    def update_up(self):
        """met à jour le vecteur vers le haut de l'écran de projection"""
        self.up = self.vect * self.right
        self.up.normalize()
    
    def get_pixel(self, i: int, j: int):
        """retourne la position virtuelle d'un pixel de l'écran de projection"""
        pixel = self.center + self.right * (j - self.width / 2) - self.up * (i - self.height / 2)
