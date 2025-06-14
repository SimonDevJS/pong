import pygame as pg
import sys
import random
import math
from pygame import gfxdraw

# Initialize pygame
pg.init()

# Screen configuration
ANCHO_PANTALLA = 900
ALTO_PANTALLA = 600
pantalla = pg.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))

# Change title and icon
pg.display.set_caption('Pong Mejorado')
ruta_icon = "pong.png"  # Adjust path as needed
try:
    icono = pg.image.load(ruta_icon)
    pg.display.set_icon(icono)
except:
    print("No se pudo cargar el icono, usando uno predeterminado")

# Clock initialization
mi_reloj = pg.time.Clock()

# Color palette
BLANCO = (255, 255, 255)
COLOR_FONDO = (20, 20, 60)  # Darker blue for better contrast
AZUL = (70, 130, 220)
AZUL_CLARO = (100, 160, 255)
ROJO = (220, 70, 90)
ROJO_CLARO = (255, 100, 120)
NEGRO = (0, 0, 0)
GRIS = (100, 100, 100)
AMARILLO = (255, 255, 0)

# Sound initialization
pg.mixer.init()
try:
    sonido_golpe_paleta = pg.mixer.Sound('golpe_paleta.mp3')
    sonido_golpe_pared = pg.mixer.Sound('golpe_pared.mp3')
    sonido_punto = pg.mixer.Sound('punto.mp3')
    sonido_cuenta = pg.mixer.Sound('cuenta.mp3')
    sonido_inicio = pg.mixer.Sound('inicio.mp3')
    
    sonido_golpe_paleta.set_volume(0.5)
    sonido_golpe_pared.set_volume(0.5)
    sonido_punto.set_volume(0.5)
    sonido_cuenta.set_volume(0.3)
    sonido_inicio.set_volume(0.7)
except:
    print("No se pudieron cargar algunos sonidos")

# Paddle coordinates and dimensions
j1_x = 50
j1_y = 250
j2_x = 820
j2_y = 250
ANCHO_PALETA = 20
ALTO_PALETA = 100

# Ball coordinates and dimensions
pelota_x = 450
pelota_y = 300
ANCHO_PELOTA = 15
ALTO_PELOTA = 15
pelota_diferencia_x = 5  # Slightly faster
pelota_diferencia_y = 5
pelota_velocidad_base = 5  # Base speed for resets
pelota_max_velocidad = 8   # Maximum speed the ball can reach

# Initial scores
puntos_j1 = 0
puntos_j2 = 0

# Font initialization
pg.font.init()
calibri_bold_35 = pg.font.SysFont('Calibri Bold', 35)
calibri_bold_25 = pg.font.SysFont('Calibri Bold', 25)
calibri_bold_120 = pg.font.SysFont('Calibri Bold', 120)
calibri_bold_80 = pg.font.SysFont('Calibri Bold', 80)

# Create game elements
paleta_j1 = pg.Rect(j1_x, j1_y, ANCHO_PALETA, ALTO_PALETA)
paleta_j2 = pg.Rect(j2_x, j2_y, ANCHO_PALETA, ALTO_PALETA)
pelota = pg.Rect(pelota_x, pelota_y, ANCHO_PELOTA, ALTO_PELOTA)

# Particle system for visual effects
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 3)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(20, 40)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size - 0.1)
        return self.life > 0
    
    def draw(self, surface):
        pg.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

particles = []

# Game state variables
paused = False
countdown_active = False
countdown_value = 3
last_countdown_time = 0
screen_shake = 0
shake_intensity = 0

def dibujar_pantalla():
    global screen_shake
    
    # Apply screen shake if active
    offset_x = random.randint(-screen_shake, screen_shake)
    offset_y = random.randint(-screen_shake, screen_shake)
    
    # Reduce shake intensity each frame
    if screen_shake > 0:
        screen_shake -= 1
    
    # Draw background with court markings
    pantalla.fill(COLOR_FONDO)
    
    # Draw center line
    for y in range(0, ALTO_PANTALLA, 30):
        pg.draw.rect(pantalla, GRIS, (ANCHO_PANTALLA // 2 - 2 + offset_x, y + offset_y, 4, 15))
    
    # Draw court outline
    pg.draw.rect(pantalla, GRIS, (10 + offset_x, 10 + offset_y, ANCHO_PANTALLA - 20, ALTO_PANTALLA - 20), 2)
    
    # Draw paddles with gradient effect
    draw_paddle(pantalla, paleta_j1.x + offset_x, paleta_j1.y + offset_y, ANCHO_PALETA, ALTO_PALETA, AZUL, AZUL_CLARO)
    draw_paddle(pantalla, paleta_j2.x + offset_x, paleta_j2.y + offset_y, ANCHO_PALETA, ALTO_PALETA, ROJO, ROJO_CLARO)
    
    # Draw ball with glow effect
    draw_ball(pantalla, pelota.x + offset_x, pelota.y + offset_y, ANCHO_PELOTA, ALTO_PELOTA, BLANCO)
    
    # Draw particles
    for particle in particles:
        if particle.update():
            particle.draw(pantalla)
        else:
            particles.remove(particle)
    
    # Draw scores
    texto_puntos_j1 = calibri_bold_35.render("PUNTOS J1: " + str(puntos_j1), True, AZUL_CLARO)
    texto_puntos_j2 = calibri_bold_35.render("PUNTOS J2: " + str(puntos_j2), True, ROJO_CLARO)
    pantalla.blit(texto_puntos_j1, (130, 20))
    pantalla.blit(texto_puntos_j2, (620, 20))
    
    # Draw countdown if active
    if countdown_active:
        countdown_text = calibri_bold_80.render(str(countdown_value), True, AMARILLO)
        pantalla.blit(countdown_text, (ANCHO_PANTALLA // 2 - countdown_text.get_width() // 2, 
                                      ALTO_PANTALLA // 2 - countdown_text.get_height() // 2))
    
    # Draw pause message if paused
    if paused:
        pause_text = calibri_bold_35.render("PAUSA", True, BLANCO)
        continue_text = calibri_bold_25.render("Presiona P para continuar", True, BLANCO)
        
        # Draw semi-transparent overlay
        overlay = pg.Surface((ANCHO_PANTALLA, ALTO_PANTALLA), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        pantalla.blit(overlay, (0, 0))
        
        pantalla.blit(pause_text, (ANCHO_PANTALLA // 2 - pause_text.get_width() // 2, 
                                  ALTO_PANTALLA // 2 - pause_text.get_height() // 2))
        pantalla.blit(continue_text, (ANCHO_PANTALLA // 2 - continue_text.get_width() // 2, 
                                     ALTO_PANTALLA // 2 + 50))

def draw_paddle(surface, x, y, width, height, color1, color2):
    # Draw paddle with rounded corners and gradient
    rect = pg.Rect(x, y, width, height)
    radius = 8
    
    # Create gradient effect
    for i in range(height):
        ratio = i / height
        color = blend_colors(color1, color2, ratio)
        pg.draw.line(surface, color, (x, y + i), (x + width - 1, y + i))
    
    # Draw rounded corners
    pg.draw.rect(surface, color1, rect, 0, radius)

def draw_ball(surface, x, y, width, height, color):
    # Draw ball with glow effect
    radius = width // 2
    center_x = x + radius
    center_y = y + radius
    
    # Draw glow
    for i in range(3):
        glow_radius = radius + i * 2
        alpha = 100 - i * 30
        glow_color = (255, 255, 255, alpha)
        glow_surface = pg.Surface((glow_radius * 2, glow_radius * 2), pg.SRCALPHA)
        pg.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surface, (center_x - glow_radius, center_y - glow_radius))
    
    # Draw main ball
    pg.draw.circle(surface, color, (center_x, center_y), radius)

def blend_colors(color1, color2, ratio):
    r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
    g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
    b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
    return (r, g, b)

def create_particles(x, y, count, color):
    for _ in range(count):
        particles.append(Particle(x, y, color))

def mostrar_menu_inicial():
    pantalla.fill(COLOR_FONDO)
    
    # Draw animated background
    for i in range(20):
        x = random.randint(0, ANCHO_PANTALLA)
        y = random.randint(0, ALTO_PANTALLA)
        size = random.randint(1, 3)
        pg.draw.circle(pantalla, BLANCO, (x, y), size)
    
    # Draw title with shadow effect
    titulo = calibri_bold_120.render("PONG", True, BLANCO)
    sombra = calibri_bold_120.render("PONG", True, AZUL)
    
    try:
        icono_escalado = pg.transform.scale(icono, (titulo.get_height(), titulo.get_height()))
        pantalla.blit(icono_escalado, (ANCHO_PANTALLA // 2 + titulo.get_width() // 2 + 10, ALTO_PANTALLA // 2 - 200))
    except:
        pass
    
    pantalla.blit(sombra, (ANCHO_PANTALLA // 2 - titulo.get_width() // 2 + 4, ALTO_PANTALLA // 2 - 200 + 4))
    pantalla.blit(titulo, (ANCHO_PANTALLA // 2 - titulo.get_width() // 2, ALTO_PANTALLA // 2 - 200))
    
    # Draw menu options with highlight boxes
    mensaje_inicio = calibri_bold_35.render("¿A cuántos puntos jugamos esta partida?", True, BLANCO)
    pantalla.blit(mensaje_inicio, (ANCHO_PANTALLA // 2 - mensaje_inicio.get_width() // 2, ALTO_PANTALLA // 2 - 100))
    
    # Draw option boxes
    options = [
        {"text": "5 puntos [1]", "key": pg.K_1, "value": 5},
        {"text": "10 puntos [2]", "key": pg.K_2, "value": 10},
        {"text": "50 puntos [3]", "key": pg.K_3, "value": 50}
    ]
    
    for i, option in enumerate(options):
        option_rect = pg.Rect(ANCHO_PANTALLA // 2 - 150, ALTO_PANTALLA // 2 - 30 + i * 50, 300, 40)
        pg.draw.rect(pantalla, GRIS, option_rect, 0, 10)
        
        option_text = calibri_bold_25.render(option["text"], True, BLANCO)
        pantalla.blit(option_text, (option_rect.centerx - option_text.get_width() // 2, 
                                   option_rect.centery - option_text.get_height() // 2))
    
    # Draw controls info
    controls_text = calibri_bold_25.render("Controles: W/S - Jugador 1, ↑/↓ - Jugador 2, P - Pausa", True, BLANCO)
    pantalla.blit(controls_text, (ANCHO_PANTALLA // 2 - controls_text.get_width() // 2, ALTO_PANTALLA - 50))
    
    pg.display.flip()
    
    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if e.type == pg.KEYDOWN:
                for option in options:
                    if e.key == option["key"]:
                        try:
                            sonido_inicio.play()
                        except:
                            pass
                        return option["value"]
        
        mi_reloj.tick(30)

def verificar_ganador(puntos_para_ganar):
    if puntos_j1 >= puntos_para_ganar:
        return 'Jugador 1'
    elif puntos_j2 >= puntos_para_ganar:
        return 'Jugador 2'
    return None

def mostrar_ganador(ganador):
    pantalla.fill(COLOR_FONDO)
    
    # Draw animated background
    for i in range(20):
        x = random.randint(0, ANCHO_PANTALLA)
        y = random.randint(0, ALTO_PANTALLA)
        size = random.randint(1, 3)
        pg.draw.circle(pantalla, BLANCO, (x, y), size)
    
    # Draw winner message with trophy icon
    color_ganador = AZUL if ganador == "Jugador 1" else ROJO
    mensaje = calibri_bold_35.render("¡Ha ganado " + ganador + "!", True, color_ganador)
    
    # Draw trophy
    trophy_height = 80
    trophy_y = ALTO_PANTALLA // 2 - 150
    
    # Draw trophy using shapes
    pg.draw.rect(pantalla, AMARILLO, (ANCHO_PANTALLA // 2 - 25, trophy_y + 50, 50, 30))
    pg.draw.rect(pantalla, AMARILLO, (ANCHO_PANTALLA // 2 - 15, trophy_y + 80, 30, 40))
    pg.draw.ellipse(pantalla, AMARILLO, (ANCHO_PANTALLA // 2 - 40, trophy_y, 80, 50))
    
    pantalla.blit(mensaje, (ANCHO_PANTALLA // 2 - mensaje.get_width() // 2, ALTO_PANTALLA // 2 - 50))
    
    # Draw replay options
    mensaje_reinicio = calibri_bold_25.render("¿Quieres volver a jugar?", True, BLANCO)
    pantalla.blit(mensaje_reinicio, (ANCHO_PANTALLA // 2 - mensaje_reinicio.get_width() // 2, ALTO_PANTALLA // 2 + 50))
    
    # Draw option boxes
    si_rect = pg.Rect(ANCHO_PANTALLA // 2 - 120, ALTO_PANTALLA // 2 + 100, 100, 40)
    no_rect = pg.Rect(ANCHO_PANTALLA // 2 + 20, ALTO_PANTALLA // 2 + 100, 100, 40)
    
    pg.draw.rect(pantalla, GRIS, si_rect, 0, 10)
    pg.draw.rect(pantalla, GRIS, no_rect, 0, 10)
    
    mensaje_si = calibri_bold_25.render("Sí [S]", True, BLANCO)
    mensaje_no = calibri_bold_25.render("No [N]", True, BLANCO)
    
    pantalla.blit(mensaje_si, (si_rect.centerx - mensaje_si.get_width() // 2, 
                              si_rect.centery - mensaje_si.get_height() // 2))
    pantalla.blit(mensaje_no, (no_rect.centerx - mensaje_no.get_width() // 2, 
                              no_rect.centery - mensaje_no.get_height() // 2))
    
    pg.display.flip()
    
    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_s:
                    return True
                if e.key == pg.K_n:
                    return False
        mi_reloj.tick(30)

def resetear_pelota_y_paletas():
    global pelota_x, pelota_y, pelota_diferencia_x, pelota_diferencia_y, j1_y, j2_y, countdown_active, countdown_value, last_countdown_time
    
    pelota_x = 450
    pelota_y = 300
    
    # Randomize initial direction
    pelota_diferencia_x = pelota_velocidad_base * random.choice([-1, 1])
    pelota_diferencia_y = pelota_velocidad_base * random.choice([-0.7, 0.7])
    
    j1_y = 250
    j2_y = 250
    
    # Start countdown
    countdown_active = True
    countdown_value = 3
    last_countdown_time = pg.time.get_ticks()

def iniciar_cuenta_regresiva():
    global countdown_active, countdown_value, last_countdown_time
    countdown_active = True
    countdown_value = 3
    last_countdown_time = pg.time.get_ticks()

def actualizar_cuenta_regresiva():
    global countdown_active, countdown_value, last_countdown_time
    
    if countdown_active:
        current_time = pg.time.get_ticks()
        if current_time - last_countdown_time >= 1000:  # 1 second
            countdown_value -= 1
            last_countdown_time = current_time
            
            try:
                sonido_cuenta.play()
            except:
                pass
            
            if countdown_value <= 0:
                countdown_active = False
                try:
                    sonido_inicio.play()
                except:
                    pass

# Main game loop
ejecutando = True

while ejecutando:
    # Show initial menu
    puntos_para_ganar = mostrar_menu_inicial()
    
    # Reset game state
    puntos_j1 = 0
    puntos_j2 = 0
    resetear_pelota_y_paletas()
    iniciar_cuenta_regresiva()
    
    jugando = True
    
    while jugando:
        # Check for game close
        for event in pg.event.get():
            if event.type == pg.QUIT:
                ejecutando = False
                jugando = False
                break
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_p:  # Toggle pause
                    paused = not paused
        
        if not ejecutando:
            break
        
        # Update countdown if active
        if countdown_active:
            actualizar_cuenta_regresiva()
        
        # Skip game logic if paused or countdown is active
        if not paused and not countdown_active:
            # Get pressed keys
            teclas = pg.key.get_pressed()
            
            # Update paddle positions
            paleta_j1.y = j1_y
            paleta_j2.y = j2_y
            pelota.x = pelota_x
            pelota.y = pelota_y
            
            # Update paddle 1 position
            if teclas[pg.K_w] and j1_y > 10:
                j1_y -= 7  # Slightly faster movement
            elif teclas[pg.K_s] and j1_y + ALTO_PALETA < ALTO_PANTALLA - 10:
                j1_y += 7
            
            # Update paddle 2 position
            if teclas[pg.K_UP] and j2_y > 10:
                j2_y -= 7
            elif teclas[pg.K_DOWN] and j2_y + ALTO_PALETA < ALTO_PANTALLA - 10:
                j2_y += 7
            
            # Update ball position
            pelota_x += pelota_diferencia_x
            pelota_y += pelota_diferencia_y
            
            # Check collisions
            if pelota.colliderect(paleta_j1):
                # Calculate bounce angle based on where the ball hits the paddle
                relative_intersect_y = (paleta_j1.y + (ALTO_PALETA / 2)) - pelota_y
                normalized_relative_intersect_y = relative_intersect_y / (ALTO_PALETA / 2)
                bounce_angle = normalized_relative_intersect_y * (math.pi / 4)  # Max 45 degrees
                
                # Calculate new velocity
                speed = min(math.sqrt(pelota_diferencia_x**2 + pelota_diferencia_y**2) + 0.2, pelota_max_velocidad)
                pelota_diferencia_x = speed * math.cos(bounce_angle)
                pelota_diferencia_y = -speed * math.sin(bounce_angle)
                
                # Visual and sound effects
                try:
                    sonido_golpe_paleta.play()
                except:
                    pass
                create_particles(pelota_x, pelota_y, 15, AZUL_CLARO)
                screen_shake = 3
                
            elif pelota.colliderect(paleta_j2):
                # Calculate bounce angle based on where the ball hits the paddle
                relative_intersect_y = (paleta_j2.y + (ALTO_PALETA / 2)) - pelota_y
                normalized_relative_intersect_y = relative_intersect_y / (ALTO_PALETA / 2)
                bounce_angle = normalized_relative_intersect_y * (math.pi / 4)  # Max 45 degrees
                
                # Calculate new velocity
                speed = min(math.sqrt(pelota_diferencia_x**2 + pelota_diferencia_y**2) + 0.2, pelota_max_velocidad)
                pelota_diferencia_x = -speed * math.cos(bounce_angle)
                pelota_diferencia_y = -speed * math.sin(bounce_angle)
                
                # Visual and sound effects
                try:
                    sonido_golpe_paleta.play()
                except:
                    pass
                create_particles(pelota_x, pelota_y, 15, ROJO_CLARO)
                screen_shake = 3
                
            elif pelota_y <= 10:
                pelota_diferencia_y = abs(pelota_diferencia_y)
                try:
                    sonido_golpe_pared.play()
                except:
                    pass
                create_particles(pelota_x, pelota_y, 10, BLANCO)
                
            elif pelota_y >= ALTO_PANTALLA - 10:
                pelota_diferencia_y = -abs(pelota_diferencia_y)
                try:
                    sonido_golpe_pared.play()
                except:
                    pass
                create_particles(pelota_x, pelota_y, 10, BLANCO)
                
            elif pelota_x <= 0 or pelota_x >= ANCHO_PANTALLA:
                try:
                    sonido_punto.play()
                except:
                    pass
                
                # Create many particles for scoring effect
                create_particles(pelota_x, pelota_y, 30, AMARILLO)
                screen_shake = 10
                
                if pelota_x >= ANCHO_PANTALLA:
                    puntos_j1 += 1
                elif pelota_x <= 0:
                    puntos_j2 += 1
                
                # Check for winner
                ganador = verificar_ganador(puntos_para_ganar)
                if ganador:
                    # Ask if they want to play again
                    if not mostrar_ganador(ganador):
                        ejecutando = False
                        jugando = False
                        break
                    else:
                        # If they want to play again, reset scores and continue
                        puntos_j1 = 0
                        puntos_j2 = 0
                        resetear_pelota_y_paletas()
                        break
                
                resetear_pelota_y_paletas()
        
        # Draw the screen
        dibujar_pantalla()
        
        # Update display
        pg.display.flip()
        mi_reloj.tick(60)

# Quit pygame
pg.quit()
sys.exit()
