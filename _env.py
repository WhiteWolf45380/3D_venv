import numpy as np


class Environnement:
    """environnement 3D contenant les objets de la scène"""
    
    def __init__(self, main):
        self.main = main
        self.objects = []

        # cube
        cube1 = Cube([0, 0, -10], 1, color=[(255, 0, 0), (0, 255, 0), (0, 0, 255)])
        self.add(cube1)

    def add(self, obj: object):
        """ajoute un objet à la scène"""
        self.objects.append(obj)
    
    @property
    def screen_triangles(self):
        """renvoie l'ensemble des triangles à afficher"""
        triangles = [] # liste de tous les triangles
        for obj in self.objects: # parcours l'ensemble des objets
            mesh = obj.mesh # raccourci

            # espace monde
            V_h = mesh.world_vertices()

            # référentiel de la caméra
            V_camera = mesh.camera_vertices(V_h, self.main.pov.view_matrix)

            # espace de découpage
            V_clip = mesh.clip_vertices(V_camera, self.main.pov.projection_matrix)

            # espace ndc
            V_ndc = mesh.ndc_vertices(V_clip)

            # mask frustum
            V_ndc_mask = mesh.ndc_mask(V_ndc)

            # récupération des vertexs à l'écran
            V_screen = mesh.screen_vertices(V_ndc, (self.main.screen_width, self.main.screen_height))

            # chaque triangle
            for i, index in enumerate(mesh.indexes):
                # back-face culling avec l'espace caméra
                triangle_camera = [V_camera[index[0]][:3], V_camera[index[1]][:3], V_camera[index[2]][:3]]
                normale = self.triangle_normale(triangle_camera)
                if not self.bf_culling(triangle_camera, normale):
                    continue

                # hors frustum
                visible = (V_ndc_mask[index[0]] | V_ndc_mask[index[1]] | V_ndc_mask[index[2]])
                if not visible:
                    continue

                # formation du triangle
                depth = (V_camera[index[0]][2] + V_camera[index[1]][2] + V_camera[index[2]][2]) / 3
                triangle = [V_screen[index[0]], V_screen[index[1]], V_screen[index[2]], depth, mesh.get_color(i)]

                triangles.append(triangle)
        return triangles
    
    def triangle_normale(self, triangle: list):
        """renvoie la normale d'un triangle"""
        return np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
    
    def bf_culling(self, triangle: list, normale):
        """vérifie la visibilité du triangle par black-face culling"""
        visible = np.dot(normale, triangle[0]) > 0
        return visible

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
    
    def world_vertices(self):
        """renvoie les vertexs dans l'espace monde"""
        # reshape vers (N, 4)
        return self.vertices_homogeneous
    
    def camera_vertices(self, V_h,  view_matrix):
        """renvoie les vertexs dans l'espace relatif à la caméra"""
        # transformation dans le repère de la caméra
        return V_h @ view_matrix.T
    
    def clip_vertices(self, V_camera, projection_matrix):
        """renvoie les vertexs dans l'espace de découpage"""
        # transformation dans l'espace de découpage
        return V_camera @ projection_matrix.T
    
    def ndc_vertices(self, V_clip):
        """renvoie les vertexs dans l'espace ndc [-1; 1]"""
        # division perspective
        return V_clip[:, :3] / V_clip[:, 3:4]
    
    def ndc_mask(self, V_ndc, marge: float=0.4):
        """renvoie le masque de présence dans le frustum"""
        return ((V_ndc[:,0] >= -(1+marge)) &
                (V_ndc[:,0] <=  (1+marge)) &
                (V_ndc[:,1] >= -(1+marge)) &
                (V_ndc[:,1] <=  (1+marge)) &
                (V_ndc[:,2] >= -(1+marge)) &
                (V_ndc[:,2] <=  (1+marge)))
    
    def screen_vertices(self, V_ndc, size: tuple):
        """renvoie les vertexs en pixels"""
        V_screen = np.empty_like(V_ndc) # crée une matrice vide (N, 4)

        V_screen[:,0] = (V_ndc[:,0] + 1) * 0.5 * size[0]            # x
        V_screen[:,1] = (1 - (V_ndc[:,1] + 1) * 0.5) * size[1]      # y
        V_screen[:,2] = V_ndc[:,2]                                  # z

        return V_screen


class Cube:
    """forme géométrique cubique de l'espace"""

    def __init__(self, pos: list, size: float, color=(255, 0, 0)):
        self.color = self.get_colors(color)
        half = size / 2

        # coin d'origine et opposé
        x0, x1 = pos[0] - half, pos[0] + half
        y0, y1 = pos[1] - half, pos[1] + half
        z0, z1 = pos[2] + half,pos[2] - half

        # 8 sommets
        self.vertices = [
            [x0, y0, z0],   # gauche bas devant
            [x1, y0, z0],   # droite bas devant
            [x1, y0, z1],   # droite bas derrière
            [x0, y0, z1],   # gauche bas derrière
            [x0, y1, z0],   # gauche haut devant
            [x1, y1, z0],   # droite haut devant
            [x1, y1, z1],   # droite haut derrière
            [x0, y1, z1],   # gauche haut derrière
        ]

        # 12 triangles (indices)
        self.indexes = [
            [4,1,0], [4,5,1], # face avant (z0)
            [6,3,2], [6,7,3], # face arrière (z1)
            [7,0,3], [7,4,0], # face gauche (x0)
            [5,2,1], [5,6,2], # face droite (x1)
            [0,2,3], [0,1,2], # face basse (y0)
            [7,5,4], [7,6,5], # face haute (y1)
        ]

        # mesh
        self.mesh = Mesh(self.vertices, self.indexes, colors=self.color)

    def get_colors(self, color):
        if isinstance(color, tuple):
            return color
        elif len(color) == 2:
            colors = []
            for _ in range(6):
                colors.append(color[0])
                color.append(color[1])
            return colors
        elif len(color) == 3:
            colors = []
            colors.append(color[0])
            colors.append(color[0])
            colors.append(color[0])
            colors.append(color[0])
            colors.append(color[1])
            colors.append(color[1])
            colors.append(color[1])
            colors.append(color[1])
            colors.append(color[2])
            colors.append(color[2])
            colors.append(color[2])
            colors.append(color[2])
            return colors
        else:
            return color[0]