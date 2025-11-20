import numpy as np
import math

class Pov:
    def __init__(self, main):
        """formalités"""
        self.main = main

        """position"""
        self.pos = np.array([0, 0, 0], dtype=np.float32)

        self.yaw = 0 # rotation caméra (gauche/droite)
        self.pitch = 0 # rotation caméra (haut/bas)

        self.world_up = np.array([0, 1, 0], dtype=np.float32) # vecteur vers le haut de l'espace
        self.forward = None # vecteur vers l'avant
        self.right = None # vecteur vers la droite
        self.up = None # vecteur vers le haut

        """projection"""
        self.fov = 60 # angle du cone de vision

        self.view_matrice = None

        """initialisation"""
        self.update_matrice()
    
    @property
    def x(self):
        """position sur l'axe x"""
        return self.pos[0]
    
    @property
    def y(self):
        """position sur l'axe y"""
        return self.pos[1]
    
    @property
    def z(self):
        """position sur l'axe z"""
        return self.pos[2]
    
    def update_matrice(self, dirs=True):
        """actualisation de la matrice de vue"""
        if dirs: # calcul des vecteurs directionnels
            self.update_directions()
        
        # matrice de vue
        f = self.forward
        r = self.right
        u = self.up
        p = self.pos
        self.view_matrice = np.array(
            [[  r[0],   r[1],   r[2],   -np.dot(r, p)],
             [  u[0],   u[1],   u[2],   -np.dot(u, p)],
             [  -f[0],  -f[1],  -f[2],  -np.dot(f, p)],
             [  0,      0,      0,      1],]
            , dtype=np.float32)
    
    def update_directions(self):
        """actualise les vecteurs directionnels"""
        self.forward = self.calc_forward()
        self.right = self.calc_right()
        self.up = self.calc_up()
    
    def calc_forward(self):
        """actualise le vecteur vers l'avant de la caméra"""
        # valeurs trigonométriques
        yaw_cos = np.cos(np.radians(self.yaw))
        yaw_sin = np.sin(np.radians(self.yaw))
        pitch_cos = np.cos(np.radians(self.pitch))
        pitch_sin = np.sin(np.radians(self.pitch))
        # vecteur directionnel
        return  np.array([
            yaw_sin * pitch_cos,    # x
            pitch_sin,              # y
            -yaw_cos * pitch_cos,   # z
        ], dtype=np.float32)
    
    def calc_right(self):
        """actualise le vecteur vers la droite de la caméra"""
        right = np.cross(self.forward, self.world_up)
        return right / np.linalg.norm(right)

    def calc_up(self):
        """actualise le vecteir vers le haut de la caméra"""
        up = np.cross(self.right, self.forward)
        return up / np.linalg.norm(up)
 
    def move(self, offset):
        """déplacement de la caméra"""
        self.pos += self.right * offset[0]
        self.pos += self.up * offset[1]
        self.pos += self.forward * offset[2]
        self.update_matrice(dirs=False)

    def rotate(self, dyaw, dpitch):
        """rotation de la caméra"""
        self.yaw += dyaw
        self.pitch = np.clip(self.pitch + dpitch, -89, 89)
        self.update_matrice()
