import numpy as np

class DataManager:
    """Classe pour gérer l'import de fichiers .obj"""
    
    def __init__(self, env):
        self.env = env
        self.vertices = []
        self.indexes = []

    def load_obj(self, filepath: str):
        """Charge un fichier .obj et extrait les vertices et faces"""
        self.vertices = []
        self.indexes = []

        filepath = self.env.main.get_path(filepath)
        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith('v '):
                    # vertex
                    parts = line.strip().split()
                    x, y, z = map(float, parts[1:4])
                    self.vertices.append([x, y, z])
                
                elif line.startswith('f '):
                    # face (triangle ou quad)
                    parts = line.strip().split()[1:]
                    face_indices = []
                    for p in parts:
                        # chaque élément peut être 'v', 'v/vt', 'v//vn' ou 'v/vt/vn'
                        idx = int(p.split('/')[0]) - 1  # OBJ indices commencent à 1
                        face_indices.append(idx)
                    
                    # convertir en triangles si nécessaire
                    if len(face_indices) == 3:
                        self.indexes.append(face_indices)
                    elif len(face_indices) == 4:
                        # quad → deux triangles
                        self.indexes.append([face_indices[0], face_indices[1], face_indices[2]])
                        self.indexes.append([face_indices[0], face_indices[2], face_indices[3]])
                    else:
                        # polygone à plus de 4 sommets → triangulation simple (fan)
                        for i in range(1, len(face_indices) - 1):
                            self.indexes.append([face_indices[0], face_indices[i], face_indices[i+1]])

        # convertir en np.array pour usage direct
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.indexes = np.array(self.indexes, dtype=np.int32)

        return self.vertices, self.indexes