import numpy as np


class Environnement:
    """Environnement 3D contenant les objets de la scène"""
    
    def __init__(self, main):
        self.main = main
        self.objects = []
