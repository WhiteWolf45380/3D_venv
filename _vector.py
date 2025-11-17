import numpy as np


class Vector:
    def __init__(self, *coords):
        """crée un vecteur"""
        if len(coords) == 1 and hasattr(coords[0], "__iter__"):
            coords = tuple(coords[0])
        coords = coords + tuple(0 for _ in range(max(0, 3 - len(coords))))
        self.coordinates = np.array(coords, dtype=np.float64)
    
    # --- manipulation ---
    def __getitem__(self, i: int):
        """utilisation de la recherche par indice"""
        return self.coordinates[i] if i < len(self) else 0
    
    def __setitem__(self, i, value):
        """utilisation de la modification par indice"""
        self.coordinates[i] = value
    
    def __len__(self):
        """renvoie le nombre de dimensions du vecteur"""
        return len(self.coordinates)
    
    def __repr__(self):
        """renvoie une représentation du vecteur"""
        return f"Vector{tuple(map(round, self.coordinates.tolist()))}"
    
    # --- opérations ---
    def __add__(self, other):
        """addition vectorielle"""
        return Vector(self.coordinates + other.coordinates)

    def __sub__(self, other):
        """soustraction vectorielle"""
        return Vector(self.coordinates - other.coordinates)

    def __mul__(self, other):
        """multiplication vectorielle"""
        if isinstance(other, Vector): # produit vectoriel
            return self.cross(other)
        else: # produit par un scalaire
            return Vector(self.coordinates * other)
        
    def __rmul__(self, other):
        """produit par un scalaire"""
        return self * other
    
    def __matmul__(self, other):
        """produit scalaire"""
        return self.dot(other)

    @property
    def norm(self):
        """renvoie la norme du vecteur"""
        return float(np.linalg.norm(self.coordinates))
    
    def cross(self, other):
        """renvoie le produit vectoriel"""
        return Vector(np.cross(self.coordinates, other.coordinates))

    def dot(self, other):
        """renvoie le produit scalaire"""
        return float(np.dot(self.coordinates, other.coordinates))

    def normalize(self):
        """normalisation à 1 du vecteur"""
        n = self.norm
        if n != 0:
            self.coordinates /= n
        return self