import pygame
import numpy as np
import math


class Render:
    """Renderer 3D avec rasterization et z-buffer"""
    
    def __init__(self, main, quality=0.5):
        self.main = main
        self.pov = main.pov
        self.quality = quality
        
        # lumière directionnelle
        self.light_dir = np.array([0.5, 3, 1], dtype=np.float32)
        self.light_dir /= np.linalg.norm(self.light_dir)
        
        self.resize_buffers()
    
    def resize_buffers(self):
        """Redimensionne les buffers selon la qualité"""
        w, h = self.main.screen_width, self.main.screen_height
        self.pw = int(w * self.quality)
        self.ph = int(h * self.quality)
        
        # Buffers
        self.color_buffer = np.zeros((self.ph, self.pw, 3), dtype=np.uint8)
        self.z_buffer = np.full((self.ph, self.pw), np.inf, dtype=np.float32)
    
    def clear(self):
        """Efface les buffers"""
        self.color_buffer.fill(50)  # background gris foncé
        self.z_buffer.fill(np.inf)
    
    def present(self):
        """Affiche le buffer à l'écran"""
        # Transpose car pygame veut (width, height, 3)
        surf = pygame.surfarray.make_surface(self.color_buffer.transpose(1, 0, 2))
        surf = pygame.transform.scale(surf, (self.main.screen_width, self.main.screen_height))
        self.main.screen.blit(surf, (0, 0))
    
    def draw_scene(self):
        """Dessine tous les objets de la scène"""
        for mesh in self.main.env.objects:
            self.draw_mesh(mesh)
    
    def draw_mesh(self, mesh):
        """Dessine un mesh avec backface culling et z-buffer"""
        # Transformation des vertices
        V_homo = np.c_[mesh.vertices, np.ones(len(mesh.vertices))]
        
        # View space
        cam_space = V_homo @ self.pov.view.T
        
        # Clip space
        clip_space = cam_space @ self.pov.proj.T
        
        # NDC (normalized device coordinates)
        w = clip_space[:, 3:4]
        w = np.where(np.abs(w) < 1e-8, 1e-8, w)  # évite division par zéro
        ndc = clip_space[:, :3] / w
        
        # Screen space
        xs = (ndc[:, 0] * 0.5 + 0.5) * (self.pw - 1)
        ys = (-ndc[:, 1] * 0.5 + 0.5) * (self.ph - 1)
        zs = cam_space[:, 2]  # depth en camera space, pas NDC!
        
        # Rasterization par triangle
        for tri_idx, tri in enumerate(mesh.triangles):
            i0, i1, i2 = tri
            
            # Clipping frustum simple : skip si tous les vertices sont en dehors
            z0, z1, z2 = zs[i0], zs[i1], zs[i2]
            
            # Triangle complètement derrière near plane
            if z0 <= self.pov.znear and z1 <= self.pov.znear and z2 <= self.pov.znear:
                continue
            
            # Triangle avec vertices derrière near plane (skip pour simplicité)
            if z0 <= self.pov.znear or z1 <= self.pov.znear or z2 <= self.pov.znear:
                continue
            
            # Screen coords
            x0, y0 = xs[i0], ys[i0]
            x1, y1 = xs[i1], ys[i1]
            x2, y2 = xs[i2], ys[i2]
            
            # Backface culling (cross product 2D)
            cross_z = (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)
            if cross_z >= 0:
                continue  # backface
            
            # Frustum culling : skip si triangle complètement hors écran
            if (max(x0, x1, x2) < 0 or min(x0, x1, x2) >= self.pw or
                max(y0, y1, y2) < 0 or min(y0, y1, y2) >= self.ph):
                continue
            
            # Bounding box
            minx = int(max(0, math.floor(min(x0, x1, x2))))
            maxx = int(min(self.pw - 1, math.ceil(max(x0, x1, x2))))
            miny = int(max(0, math.floor(min(y0, y1, y2))))
            maxy = int(min(self.ph - 1, math.ceil(max(y0, y1, y2))))
            
            if minx > maxx or miny > maxy:
                continue
            
            # Grille de pixels
            gx, gy = np.meshgrid(np.arange(minx, maxx + 1), np.arange(miny, maxy + 1))
            gx = gx.astype(np.float32) + 0.5  # centre du pixel
            gy = gy.astype(np.float32) + 0.5
            
            # Coordonnées barycentriques
            denom = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
            if abs(denom) < 1e-9:
                continue
            
            w0 = ((y1 - y2) * (gx - x2) + (x2 - x1) * (gy - y2)) / denom
            w1 = ((y2 - y0) * (gx - x2) + (x0 - x2) * (gy - y2)) / denom
            w2 = 1 - w0 - w1
            
            # Masque des pixels dans le triangle
            mask = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
            if not np.any(mask):
                continue
            
            # Interpolation de la profondeur (depth en camera space)
            z0, z1, z2 = zs[i0], zs[i1], zs[i2]
            z_interp = w0 * z0 + w1 * z1 + w2 * z2
            
            # Indices des pixels valides
            gy_valid = gy[mask].astype(int)
            gx_valid = gx[mask].astype(int)
            z_valid = z_interp[mask]
            
            # Z-buffer test
            depth_test = z_valid < self.z_buffer[gy_valid, gx_valid]
            if not np.any(depth_test):
                continue
            
            # Pixels finaux à dessiner
            wy = gy_valid[depth_test]
            wx = gx_valid[depth_test]
            wz = z_valid[depth_test]
            
            # Update z-buffer
            self.z_buffer[wy, wx] = wz
            
            # Interpolation des normales
            n0 = mesh.normals[i0]
            n1 = mesh.normals[i1]
            n2 = mesh.normals[i2]
            
            w0_shading = w0[mask][depth_test][:, None]
            w1_shading = w1[mask][depth_test][:, None]
            w2_shading = w2[mask][depth_test][:, None]
            
            normals_interp = n0 * w0_shading + n1 * w1_shading + n2 * w2_shading
            norms = np.linalg.norm(normals_interp, axis=1, keepdims=True)
            normals_interp = np.where(norms > 1e-8, normals_interp / norms, 0)
            
            # Lighting (diffuse + ambient)
            diffuse = np.clip(normals_interp @ self.light_dir, 0, 1)
            ambient = 0.2
            intensity = diffuse * 0.8 + ambient
            
            # Couleur finale
            color = mesh.color[None, :] * intensity[:, None]
            color = np.clip(color, 0, 255).astype(np.uint8)
            
            self.color_buffer[wy, wx] = color