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
        self.aspect = self.main.screen_width / self.main.screen_height # ratio d'aspect
        self.near = 1 # distance minimal d'affichage
        self.far = 1000.0 # distance maximale d'affichage

        self.view_matrix = None # matrice relative à la caméra
        self.projection_matrix = None # matrice de projection

        """initialisation"""
        self.update_view_matrix()
        self.update_projection_matrix()
    
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
    
    # ___________________________________________________________ Matrices ___________________________________________________________
    def update_view_matrix(self, dirs=True):
        """actualisation de la matrice de vue"""
        if dirs: # calcul des vecteurs directionnels
            self.update_directions()
        f = self.forward
        r = self.right
        u = self.up
        p = self.pos
        self.view_matrix = np.array(
            [[  r[0],   r[1],   r[2],   -np.dot(r, p)], # axe x
             [  u[0],   u[1],   u[2],   -np.dot(u, p)], # axe y
             [  -f[0],  -f[1],  -f[2],   np.dot(f, p)], # axe z
             [  0,      0,      0,      1]]             # canal de translation
            , dtype=np.float32)

    def update_projection_matrix(self):
        """actualisation de la matrice de projection"""
        r = 1 / np.tan(math.radians(self.fov) / 2)  # conversion en radians
        n = self.near                               # limite proche
        f = self.far                                # limite éloignée
        self.projection_matrix = np.array(
            [[r/self.aspect,    0,      0,      0],                     # mise à l'échelle horizontale
             [0,    r,      0,      0],                                 # mise à l'échelle verticale
             [0,    0,      -(f + n) / (f - n), -2 * f * n / (f - n)],    # encodage de la profondeur
             [0,    0,      -1,     0]]                                 # division perspective
             , dtype=np.float32
        )

    # ___________________________________________________________ Vecteurs directionnels ___________________________________________________________    
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
            pitch_cos * yaw_sin,      # x
            -pitch_sin,               # y
            -pitch_cos * yaw_cos,     # z
        ], dtype=np.float32)
    
    def calc_right(self):
        """actualise le vecteur vers la droite de la caméra"""
        right = np.cross(self.forward, self.world_up)
        return right / np.linalg.norm(right)

    def calc_up(self):
        """actualise le vecteir vers le haut de la caméra"""
        up = np.cross(self.right, self.forward)
        return up / np.linalg.norm(up)
    
    # ___________________________________________________________ Méthodes dynamiques ___________________________________________________________
    def move(self, offset):
        """déplacement de la caméra"""
        self.pos += self.right * offset[0]
        self.pos += self.world_up * offset[1]
        self.pos += self.forward * offset[2]
        self.update_view_matrix(dirs=False)

    def rotate(self, dyaw, dpitch):
        """rotation de la caméra"""
        self.yaw += dyaw
        self.pitch = np.clip(self.pitch + dpitch, -89, 89)
        self.update_view_matrix()

    def change_fov(self, fov: int):
        """change la fov"""
        self.fov = fov
        self.update_projection_matrix()