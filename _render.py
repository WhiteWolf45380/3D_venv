import pygame
import numpy as np


class Render:
    def __init__(self, main):
        """formalités"""
        self.main = main
        self.pov = self.main.pov

        """buffer réel"""
        self.quality = 0.1 # réglage de la qualité (max 1)
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
        # calcule des positions de pixels
        all_pixels = self.pov.get_all_pixels(self.pixels_width, self.pixels_height)
    
        # calcule des directions des rayons
        ray_origins = np.full_like(all_pixels, self.pov.pos.coordinates)
        ray_directions = all_pixels - ray_origins

        # normalisation vectorisée
        norms = np.linalg.norm(ray_directions, axis=2, keepdims=True)
        ray_directions = ray_directions / norms
        
        # intersections avec la géométrie
        colors = self.trace_rays(ray_origins, ray_directions)
        
        # stockage des couleurs
        self.pixels = colors.tolist()
    
    def trace_rays(self, ray_origins, ray_directions):
        """
        Calcule les intersections de tous les rayons avec la scène
        """
        H, W, _ = ray_origins.shape
        
        # Initialisation : couleur de fond
        colors = self.get_sky_gradient(ray_directions)
        
        # Distance minimale pour chaque pixel (pour gérer l'occlusion)
        min_distances = np.full((H, W), np.inf)
        
        # Pour chaque objet de la scène
        for obj in self.main.env.objects:
            # Chaque objet calcule ses propres intersections !
            hit_mask, distances, hit_points, normals = obj.intersect(
                ray_origins, ray_directions
            )
            
            # On garde seulement les objets les plus proches
            closer_mask = (hit_mask) & (distances < min_distances)
            
            if np.any(closer_mask):
                # Calcul de l'éclairage
                obj_colors = self.compute_lighting(
                    hit_points[closer_mask], 
                    normals[closer_mask], 
                    obj.color
                )
                
                # Mise à jour des couleurs et distances
                colors[closer_mask] = obj_colors
                min_distances[closer_mask] = distances[closer_mask]
        
        return colors

    def get_sky_gradient(self, ray_directions):
        """Crée un joli dégradé de ciel bleu"""
        t = 0.5 * (ray_directions[..., 1] + 1.0)
        
        sky_top = np.array([135, 206, 235])
        sky_bottom = np.array([255, 255, 255])
        
        colors = (1 - t)[..., np.newaxis] * sky_bottom + t[..., np.newaxis] * sky_top
        return colors

    def compute_lighting(self, hit_points, normals, base_color):
        """Calcul d'éclairage diffus simple"""
        # Direction de la lumière
        light_dir = np.array([1.0, 1.0, 1.0])
        light_dir = light_dir / np.linalg.norm(light_dir)
        
        # Éclairage diffus
        diffuse = np.maximum(0, np.sum(normals * light_dir, axis=1))
        
        # Lumière ambiante + diffuse
        ambient = 0.3
        intensity = ambient + (1 - ambient) * diffuse
        
        # Application à la couleur
        result = base_color * intensity[..., np.newaxis]
        
        return np.clip(result, 0, 255)
