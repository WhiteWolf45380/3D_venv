import numpy as np


class Vector:
    """vecteur 3D optimisé avec numpy"""
    __slots__ = ['data']
    
    def __init__(self, x=0.0, y=0.0, z=0.0):
        if isinstance(x, (list, tuple, np.ndarray)):
            self.data = np.array(x, dtype=np.float32)[:3]
            if len(self.data) < 3:
                self.data = np.pad(self.data, (0, 3 - len(self.data)))
        else:
            self.data = np.array([x, y, z], dtype=np.float32)
    
    @property
    def x(self): return self.data[0]
    @property
    def y(self): return self.data[1]
    @property
    def z(self): return self.data[2]
    
    @x.setter
    def x(self, v): self.data[0] = v
    @y.setter
    def y(self, v): self.data[1] = v
    @z.setter
    def z(self, v): self.data[2] = v
    
    def __getitem__(self, i): return self.data[i]
    def __setitem__(self, i, v): self.data[i] = v
    def __repr__(self): return f"V({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"
    
    def __add__(self, other): return Vector(self.data + other.data)
    def __sub__(self, other): return Vector(self.data - other.data)
    def __mul__(self, s): return Vector(self.data * s)
    def __rmul__(self, s): return Vector(self.data * s)
    def __truediv__(self, s): return Vector(self.data / s)
    def __neg__(self): return Vector(-self.data)
    
    def dot(self, other): 
        return float(np.dot(self.data, other.data))
    
    def cross(self, other): 
        return Vector(np.cross(self.data, other.data))
    
    def length(self): 
        return float(np.linalg.norm(self.data))
    
    def normalized(self):
        l = self.length()
        return self / l if l > 1e-8 else Vector(0, 0, 0)
    
    def copy(self):
        return Vector(self.data.copy())