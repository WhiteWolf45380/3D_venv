import numpy as np
import math
from _vector import Vector


class Pov:
    """Caméra 3D first-person avec matrices view et projection"""
    
    def __init__(self, main):
        self.main = main
        self.pos = np.array([0.0, 2.0, -8.0], dtype=np.float32)
        self.yaw = 0.0
        self.pitch = 0.0
        
        # Projection
        self.fov = 75.0
        self.znear = 0.1
        self.zfar = 1000.0
        
        self.update_matrices()
    
    def update_matrices(self):
        """Calcule les matrices view et projection"""
        # Projection matrix (perspective)
        aspect = self.main.screen_width / self.main.screen_height
        f = 1.0 / math.tan(math.radians(self.fov) * 0.5)
        zn, zf = self.znear, self.zfar
        
        self.proj = np.array([
            [f/aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (zf+zn)/(zn-zf), (2*zf*zn)/(zn-zf)],
            [0, 0, -1, 0]
        ], dtype=np.float32)
        
        # Direction vectors
        cy, sy = math.cos(self.yaw), math.sin(self.yaw)
        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        
        # Forward vector (where camera looks)
        self.forward = np.array([sy*cp, sp, cy*cp], dtype=np.float32)
        self.forward /= np.linalg.norm(self.forward)
        
        # Right and up vectors
        world_up = np.array([0, 1, 0], dtype=np.float32)
        self.right = np.cross(world_up, self.forward)
        self.right /= np.linalg.norm(self.right) + 1e-8
        self.up = np.cross(self.forward, self.right)
        
        # View matrix (camera transform)
        R = np.stack([self.right, self.up, self.forward])
        self.view = np.eye(4, dtype=np.float32)
        self.view[:3, :3] = R
        self.view[:3, 3] = -R @ self.pos
    
    def move(self, offset):
        """Déplace la caméra selon [right, up, forward]"""
        self.pos += self.right * offset[0]
        self.pos += self.up * offset[1]
        self.pos += self.forward * offset[2]
        self.update_matrices()
    
    def rotate(self, dyaw, dpitch):
        """Rotation de la caméra"""
        self.yaw += dyaw
        self.pitch = np.clip(self.pitch + dpitch, -math.pi/2 + 0.01, math.pi/2 - 0.01)
        self.update_matrices()