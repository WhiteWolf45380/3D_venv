import numpy as np


class Mesh:
    """Mesh 3D avec vertices, triangles et normales"""
    
    def __init__(self, vertices, triangles, color=(200, 200, 200)):
        self.vertices = np.array(vertices, dtype=np.float32)
        self.triangles = np.array(triangles, dtype=np.int32)
        self.color = np.array(color, dtype=np.float32)
        self.compute_normals()
    
    def compute_normals(self):
        """Calcule les normales par vertex (moyenne des normales de faces)"""
        self.normals = np.zeros_like(self.vertices)
        
        for tri in self.triangles:
            i0, i1, i2 = tri
            p0, p1, p2 = self.vertices[tri]
            
            # Normale de face
            edge1 = p1 - p0
            edge2 = p2 - p0
            normal = np.cross(edge1, edge2)
            norm = np.linalg.norm(normal)
            if norm > 1e-8:
                normal /= norm
            
            # Accumule sur chaque vertex
            self.normals[i0] += normal
            self.normals[i1] += normal
            self.normals[i2] += normal
        
        # Normalise
        norms = np.linalg.norm(self.normals, axis=1)[:, None]
        self.normals = np.where(norms > 1e-8, self.normals / norms, 0)
    
    @staticmethod
    def cube(size=1.0, color=(220, 100, 80)):
        """Crée un cube"""
        s = size / 2
        vertices = np.array([
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],  # face arrière
            [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s]      # face avant
        ], dtype=np.float32)
        
        triangles = np.array([
            [0, 1, 2], [0, 2, 3],  # face arrière
            [4, 6, 5], [4, 7, 6],  # face avant
            [0, 4, 5], [0, 5, 1],  # côté gauche
            [1, 5, 6], [1, 6, 2],  # côté droit
            [2, 6, 7], [2, 7, 3],  # haut
            [3, 7, 4], [3, 4, 0]   # bas
        ], dtype=np.int32)
        
        return Mesh(vertices, triangles, color)
    
    @staticmethod
    def plane(size=10.0, subdivisions=1, color=(150, 150, 150)):
        """Crée un plan horizontal (sol)"""
        s = size / 2
        step = size / subdivisions
        vertices = []
        
        for i in range(subdivisions + 1):
            for j in range(subdivisions + 1):
                x = -s + j * step
                z = -s + i * step
                vertices.append([x, 0, z])
        
        vertices = np.array(vertices, dtype=np.float32)
        
        triangles = []
        for i in range(subdivisions):
            for j in range(subdivisions):
                idx = i * (subdivisions + 1) + j
                triangles.append([idx, idx + subdivisions + 1, idx + 1])
                triangles.append([idx + 1, idx + subdivisions + 1, idx + subdivisions + 2])
        
        triangles = np.array(triangles, dtype=np.int32)
        
        return Mesh(vertices, triangles, color)

class Environnement:
    """Environnement 3D contenant les objets de la scène"""
    
    def __init__(self, main):
        self.main = main
        self.objects = []
        self.setup_scene()
    
    def setup_scene(self):
        """Crée la scène de base"""        
        # Cubes
        cube1 = Mesh.cube(size=2.0, color=(220, 100, 80))
        cube1.vertices[:, 1] += 1.0  # élève le cube
        cube1.vertices[:, 0] -= 3.0  # décale à gauche
        self.objects.append(cube1)
        
        cube2 = Mesh.cube(size=1.5, color=(80, 220, 100))
        cube2.vertices[:, 1] += 0.75
        cube2.vertices[:, 0] += 3.0  # décale à droite
        self.objects.append(cube2)
        
        cube3 = Mesh.cube(size=1.0, color=(100, 100, 220))
        cube3.vertices[:, 1] += 0.5
        cube3.vertices[:, 2] += 4.0  # décale devant
        self.objects.append(cube3)