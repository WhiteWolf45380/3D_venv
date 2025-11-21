import pygame
import sys
import os
from _env import Environnement
from _pov import Pov
from _renderer import Renderer


# _________________________- Main -_________________________
class Main:
    def __init__(self):
        """variables utiles"""
        self.running = True # état du logiciel
        self.clock = pygame.time.Clock() # clock pygame
        self.fps_max = 60 # limite de fps
        self.dt = 0 # delta time utilisé pour les animations

        """pygame"""
        pygame.init()

        # écran virtuel
        self.screen_width = 1920
        self.screen_height = 1080
        self.screen = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.screen.fill((255, 255, 255))

        # écran intermédiaire (taille réelle mais sans bandes noires)
        self.screen_final_width = self.screen_width
        self.screen_final_height = self.screen_height
        self.screen_x_offset = 0 # bandes verticales
        self.screen_y_offset = 0 # bandes horizontales

        # écran réel
        self.screen_resized_width = 1280
        self.screen_resized_height = 720
        self.screen_resized = pygame.display.set_mode((self.screen_resized_width, self.screen_resized_height), pygame.RESIZABLE, pygame.SRCALPHA)

        # plein écran
        self.fullscreen = False
        self.windowed_width = self.screen_resized_width
        self.windowed_height = self.screen_resized_height

        # design de la fenêtre
        pygame.display.set_caption("Environnement virtuel 3D")  # titre de la fenêtre
        # pygame.display.set_icon(pygame.image.load(self.get_path("assets/icon.png")))  # icone de la fenêtre

        # curseur
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        self.mouse_x = self.screen_width / 2
        self.mouse_y = self.screen_height / 2
        self.mouse_out = False # curseur en dehors de l'écran

        """objets"""
        self.env = Environnement(self)
        self.pov = Pov(self)
        self.renderer = Renderer(self)
    
    def loop(self):
        """loop principal du logiciel"""
        while self.running:
            self.dt = self.clock.tick(self.fps_max) / 1000 # limite de fps
            self.calc_screen_offsets() # adadptation des dimensions de l'écran

            # souris
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if not self.screen_x_offset <= mouse_x <= self.screen_resized_width - self.screen_x_offset or not self.screen_y_offset <= mouse_y <= self.screen_resized_height - self.screen_y_offset: # limite à l'écran
                self.mouse_out = True
            else:
                self.mouse_out = False
            self.mouse_x = (mouse_x - self.screen_x_offset) / (self.screen_final_width / self.screen_width) # conversion de la coordonée x
            self.mouse_y = (mouse_y - self.screen_y_offset) / (self.screen_final_height / self.screen_height) # conversion de la coordonée y

            # vérification des entrées utilisateur
            self.handle_inputs()
            self.handle_pressed()

            # mouse look
            mx, my = pygame.mouse.get_rel()
            if mx != 0 or my != 0:
                self.pov.rotate(mx * 0.04, my * 0.04)
            print(1 / self.dt)
            # mise à jour de l'environnement
            self.renderer.draw_scene()

            # mise à jour de l'écran
            self.blit_screen_resized()
            pygame.display.update()

    def handle_inputs(self):
        """vérification des entrées utilisateur"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # fermeture de la fenêtre
                self.close_window()
            
            elif event.type == pygame.VIDEORESIZE:
                # sauvegarde des dimensions fenêtrées
                if not self.fullscreen:
                    self.windowed_width = event.w
                    self.windowed_height = event.h
                self.pov.update_projection_matrix()
            
            elif event.type == pygame.KEYDOWN:
                # toggle mode du plein écran
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                    self.update_projection_matrix()
    
    def handle_pressed(self):
        keys = pygame.key.get_pressed() # clés pressées

        # déplacement
        speed = 3.0 * self.dt
        if keys[pygame.K_z]:
            self.pov.move([0,0, speed])
        if keys[pygame.K_s]:
            self.pov.move([0,0,-speed])
        if keys[pygame.K_q]:
            self.pov.move([-speed,0,0])
        if keys[pygame.K_d]:
            self.pov.move([speed,0,0])
        if keys[pygame.K_SPACE]:
            self.pov.move([0,speed,0])
        if keys[pygame.K_a]:
            self.pov.move([0,-speed,0])

    def toggle_fullscreen(self):
        """bascule entre mode fenêtré et plein écran"""
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            # passage en plein écran
            self.screen_resized = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            # retour en mode fenêtré
            os.environ['SDL_VIDEO_CENTERED'] = '1'
            self.screen_resized = pygame.display.set_mode(
                (self.windowed_width, self.windowed_height), 
                pygame.RESIZABLE
            )
        
        # recalcul immédiat des dimensions
        self.screen_resized_width = self.screen_resized.get_width()
        self.screen_resized_height = self.screen_resized.get_height()
        self.calc_screen_offsets()
    
    def calc_screen_offsets(self):
        """calcul les décalages dû aux dimensions de fenêtre incompatibles"""
        # récupération des dimensions de la fenêtre réelle
        self.screen_resized_width = self.screen_resized.get_width()
        self.screen_resized_height = self.screen_resized.get_height()

        # on prend le ratio min
        scale = min(
            self.screen_resized_width / self.screen_width,
            self.screen_resized_height / self.screen_height
        )

        # nouvelle taille de l’écran virtuel
        self.screen_final_width = int(self.screen_width * scale)
        self.screen_final_height = int(self.screen_height * scale)

        # centrage dans la fenêtre
        self.screen_x_offset = (self.screen_resized_width - self.screen_final_width) // 2
        self.screen_y_offset = (self.screen_resized_height - self.screen_final_height) // 2

    def blit_screen_resized(self):
        """redimensionne l'écran virtuel sur l'écran réel"""
        new_screen = pygame.transform.smoothscale(self.screen, (self.screen_final_width, self.screen_final_height))
        self.screen_resized.fill((0, 0, 0)) # pour les bandes noires
        self.screen_resized.blit(new_screen, (self.screen_x_offset, self.screen_y_offset))

    @staticmethod
    def get_path(relative_path, folder=False):
        """Obtention du chemin absolu des assets"""
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS if not folder else os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        return os.path.join(base_path, relative_path)

    def close_window(self):
        """fonction de fermeture du logiciel"""
        pygame.display.quit()
        self.running = False
        sys.exit()

# _________________________- Démarrage -_________________________
main = Main()
main.loop()