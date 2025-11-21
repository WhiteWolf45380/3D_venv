import numpy as np


class Environnement:
    """environnement 3D contenant les objets de la scène"""
    
    def __init__(self, main):
        self.main = main
        self.objects = []

        # cube
        cube1 = Cube([0, 0, -5], 1.0)
        self.add(cube1)

    def add(self, obj: object):
        """ajoute un objet à la scène"""
        self.objects.append(obj)
    
    def get_screen_triangles(self):
        """renvoie l'ensemble des triangles à afficher"""
        triangles = [] # liste de tous les triangles
        for obj in self.objects: # parcours l'ensemble des objets
            mesh = obj.mesh # raccourci

            # récupération des vertexs dans l'espace NDC
            V_ndc, V_clip_mask = mesh.get_ndc_vertices(self.main.pov.view_matrix, self.main.pov.projection_matrix, mask=True)

            # récupération des vertexs à l'écran
            V_screen = mesh.get_screen_vertices(V_ndc, (self.main.screen_width, self.main.screen_height))

            # formation des triangles
            for i, index in enumerate(mesh.indexes):
                visible = (V_clip_mask[index[0]] | V_clip_mask[index[1]] | V_clip_mask[index[2]])
                if not visible: # hors frustum
                    continue
                triangles.append([
                    V_screen[index[0]],
                    V_screen[index[1]],
                    V_screen[index[2]],
                    mesh.get_color(i)
                ])
        return triangles

class Mesh:
    """Ensemble de triangles formant un objet"""

    def __init__(self, vertices: list, indexes : list, colors=(255, 0, 0)):
        self.vertices = np.array(vertices, dtype=np.float32) # points du mesh
        self.vertices_homogeneous = np.hstack([self.vertices, np.ones((self.vertices.shape[0], 1), dtype=np.float32)]) # ajoute une colonne de 1
        self.indexes = np.array(indexes, dtype=np.int32) # indexes des points formant des triangles
        self.colors = colors
        self.unicolor = isinstance(colors, tuple)
    
    def get_color(self, i: int):
        """renvoie la couleur du triangle ou de l'objet"""
        if self.unicolor:
            return self.colors
        return self.colors[i]

    def get_ndc_vertices(self, view_matrix, projection_matrix, mask: bool=False):
        """renvoie les vertexs dans l'espace NDC"""
        # reshape vers (N, 4)
        V_h = self.vertices_homogeneous

        # transformation dans le repère de la caméra
        V_camera = V_h @ view_matrix.T

        # transformation dans l'espace de découpage
        V_clip = V_camera @ projection_matrix.T

        # clipping
        if mask:
            w = V_clip[:, 3]
            V_clip_mask = (
                (V_clip[:,0] >= -w) &
                (V_clip[:,0] <=  w) &
                (V_clip[:,1] >= -w) &
                (V_clip[:,1] <=  w) &
                (V_clip[:,2] >=  -w) &
                (V_clip[:,2] <=  w)
            )

        # division perspective
        V_ndc = V_clip[:, :3] / V_clip[:, 3:4]

        return (V_ndc, V_clip_mask) if mask else V_ndc
    
    def get_screen_vertices(self, V_ndc, size: tuple):
        """renvoie les vertexs en pixels"""
        V_screen = np.empty_like(V_ndc) # crée une matrice vide (N, 4)

        V_screen[:,0] = (V_ndc[:,0] + 1) * 0.5 * size[0]            # x
        V_screen[:,1] = (1 - (V_ndc[:,1] + 1) * 0.5) * size[1]      # y
        V_screen[:,2] = V_ndc[:,2]                                  # z

        return V_screen


class Cube:
    """forme géométrique cubique de l'espace"""

    def __init__(self, pos: list, size: float, color=(255, 0, 0)):
        self.color = color
        half = size / 2

        # 2 coins opposés
        x0, x1 = pos[0] - half, pos[0] + half
        y0, y1 = pos[1] - half, pos[1] + half
        z0, z1 = pos[2] - half, pos[2] + half

        # 8 sommets
        self.vertices = [
            [x0, y0, z0],
            [x1, y0, z0],
            [x1, y1, z0],
            [x0, y1, z0],
            [x0, y0, z1],
            [x1, y0, z1],
            [x1, y1, z1],
            [x0, y1, z1],
        ]

        # 12 triangles (indices)
        self.indexes = [
            # face arrière (z0)
            [0,1,2], [0,2,3],
            # face avant (z1)
            [4,5,6], [4,6,7],
            # face gauche (x0)
            [0,3,7], [0,7,4],
            # face droite (x1)
            [1,5,6], [1,6,2],
            # face basse (y0)
            [0,1,5], [0,5,4],
            # face haute (y1)
            [3,2,6], [3,6,7],
        ]

        # mesh
        self.mesh = Mesh(self.vertices, self.indexes, colors=self.color)