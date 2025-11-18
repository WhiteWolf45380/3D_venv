import pygame
import numpy as np


class Environnement:
    def __init__(self, main):
        """formalités"""
        self.main = main

        """objets"""
        self.objects = []

        # Ajoute des objets de test
        self.objects.append(Sphere([5, 0, 0], 1.0, [255, 100, 100]))      # rouge
        self.objects.append(Sphere([5, -2, 1], 0.8, [100, 255, 100]))     # verte
        self.objects.append(Sphere([5, 2, -1], 0.6, [100, 100, 255]))     # bleue
        self.objects.append(Plane([0, -2, 0], [0, 1, 0], [200, 200, 200])) # sol gris


class Sphere:
    def __init__(self, center, radius, color):
        self.type = "sphere"
        self.center = np.array(center)
        self.radius = radius
        self.color = np.array(color)


class Sphere:
    def __init__(self, center, radius, color):
        self.type = "sphere"
        self.center = np.array(center, dtype=np.float64)
        self.radius = radius
        self.color = np.array(color, dtype=np.float64)
    
    def intersect(self, ray_origins, ray_directions):
        """
        Intersection ray-sphere vectorisée pour TOUS les rayons à la fois
        
        ray_origins: array shape (H, W, 3)
        ray_directions: array shape (H, W, 3)
        
        retourne: hit_mask, distances, hit_points, normals
        """
        # Vecteur du centre de la sphère vers l'origine du rayon
        oc = ray_origins - self.center  # shape: (H, W, 3)
        
        # Coefficients de l'équation quadratique at² + bt + c = 0
        a = np.sum(ray_directions * ray_directions, axis=2)  # shape: (H, W)
        b = 2.0 * np.sum(oc * ray_directions, axis=2)        # shape: (H, W)
        c = np.sum(oc * oc, axis=2) - self.radius**2         # shape: (H, W)
        
        # Discriminant
        discriminant = b*b - 4*a*c  # shape: (H, W)
        
        # Masque des pixels qui intersectent la sphère
        hit_mask = discriminant > 0  # shape: (H, W) - boolean
        
        # Initialisation des résultats
        H, W, _ = ray_origins.shape
        distances = np.full((H, W), np.inf)
        hit_points = np.zeros((H, W, 3))
        normals = np.zeros((H, W, 3))
        
        if np.any(hit_mask):
            # Distance jusqu'à l'intersection (on prend la plus proche)
            sqrt_disc = np.sqrt(discriminant[hit_mask])
            t1 = (-b[hit_mask] - sqrt_disc) / (2.0 * a[hit_mask])
            t2 = (-b[hit_mask] + sqrt_disc) / (2.0 * a[hit_mask])
            
            # On prend la distance positive la plus proche
            t = np.where((t1 > 0) & (t1 < t2), t1, t2)
            
            # Filtrer les distances négatives (derrière la caméra)
            valid = t > 0
            if np.any(valid):
                # Point d'intersection
                hit_points[hit_mask] = (
                    ray_origins[hit_mask] + 
                    ray_directions[hit_mask] * t[..., np.newaxis]
                )
                
                # Normale à la surface (normalisée)
                normals[hit_mask] = hit_points[hit_mask] - self.center
                norms = np.linalg.norm(normals[hit_mask], axis=1, keepdims=True)
                normals[hit_mask] = normals[hit_mask] / norms
                
                distances[hit_mask] = t
        
        return hit_mask, distances, hit_points, normals


class Plane:
    def __init__(self, point, normal, color):
        self.type = "plane"
        self.point = np.array(point, dtype=np.float64)
        self.normal = np.array(normal, dtype=np.float64)
        self.normal = self.normal / np.linalg.norm(self.normal)  # normaliser
        self.color = np.array(color, dtype=np.float64)
    
    def intersect(self, ray_origins, ray_directions):
        """
        Intersection ray-plane vectorisée
        
        Équation du plan : (P - P0) · N = 0
        Équation du rayon : P = O + t*D
        Solution : t = (P0 - O) · N / (D · N)
        """
        H, W, _ = ray_origins.shape
        
        # Produit scalaire direction · normale
        denom = np.sum(ray_directions * self.normal, axis=2)  # shape: (H, W)
        
        # Éviter division par zéro (rayon parallèle au plan)
        hit_mask = np.abs(denom) > 1e-6
        
        distances = np.full((H, W), np.inf)
        hit_points = np.zeros((H, W, 3))
        normals = np.zeros((H, W, 3))
        
        if np.any(hit_mask):
            # Distance jusqu'à l'intersection
            p0o = self.point - ray_origins[hit_mask]
            t = np.sum(p0o * self.normal, axis=1) / denom[hit_mask]
            
            # Filtrer les intersections derrière la caméra
            valid = t > 0
            hit_mask_copy = hit_mask.copy()
            hit_mask[hit_mask_copy] = valid
            
            if np.any(valid):
                # Point d'intersection
                hit_points[hit_mask] = (
                    ray_origins[hit_mask] + 
                    ray_directions[hit_mask] * t[valid][..., np.newaxis]
                )
                
                # La normale est constante pour un plan
                normals[hit_mask] = self.normal
                distances[hit_mask] = t[valid]
        
        return hit_mask, distances, hit_points, normals