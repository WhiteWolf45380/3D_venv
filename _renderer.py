import pygame
import numpy as np
import math


class Renderer:    
    def __init__(self, main, quality=0.5):
        self.main = main
        self.pov = main.pov
        self.quality = quality
