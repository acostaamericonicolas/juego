import pygame
import sys, random, re
from button import *
from config import *
from class_auto import Auto
from class_diamante import *
from class_vidas import *
from class_contrarios import *
import json

pygame.init()
pygame.mixer.init()

# Tamaño de pantalla
screen = pygame.display.set_mode(screen_size)
# Nombre de Aplicacion
pygame.display.set_caption('Python Speed')

#sonidos
sound = pygame.mixer.Sound(path_sonido_colision)
sound_diamante = pygame.mixer.Sound(path_sonido_diamante)
sound_inicio2 = pygame.mixer.Sound(path_sonido_inicio2)
sound_game_over = pygame.mixer.Sound(path_sonido_game_over)
sound_acelerar = pygame.mixer.Sound(path_sonido_acelerar)
sound_vida = pygame.mixer.Sound(path_sonido_vida)


fondo = pygame.image.load(path_ruta).convert()
fondo = pygame.transform.scale(fondo, screen_size)
fondo_alto = fondo.get_height()


auto = Auto(path_auto, SIZE_AUTO,(screen.get_width()//2, screen.get_height()-20))
auto_mov_left = Auto(path_auto_mov_izq, SIZE_AUTO,(screen.get_width()//2, screen.get_height()-20))

clock = pygame.time.Clock() #controlar la velocidad

menu_principal = pygame.image.load(image_folder + "menu.png").convert_alpha()

def guardar_ranking(path_ranking_json, player, score):
    ranking = {
        "player": player,
        "score": str(score)
    }
    with open(path_ranking_json, "a") as archivo:
        json.dump(ranking, archivo)
        archivo.write("\n")

def mostrar_puntaje():
    font = pygame.font.Font(path_fuente, 20)
    text = font.render("SCORE: " + str(score), True, NEGRO)
    screen.blit(text, (10, 40))

def mostrar_vidas():
    font = pygame.font.Font(path_fuente, 25)
    text = font.render("Vidas: " + str(vidas), True, NEGRO)
    screen.blit(text, (10, 10))

def mostrar_game_over():
    global score
    global vidas

    sound_game_over.play()
    game_over = pygame.image.load(image_folder + "game_over.jpg").convert()
    game_over = pygame.transform.scale(game_over, (screen_size))
    screen.blit(game_over, (0, 0))
    font = pygame.font.Font(path_fuente, 40)

    # Variables para el nombre del jugador
    player_name = ""

    # Bucle principal para ingresar el nombre
    entering_name = True
    while entering_name:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    entering_name = False
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    player_name += event.unicode

        # Limpiar la ventana
        screen.fill((0, 0, 0))

        text = font.render("GAME OVER: " + "Score:" + str(score), True, (255, 255, 255))
        screen.blit(text, (120, 280))
        # Mostrar el nombre ingresado dentro del rectángulo
        name_text = font.render("Player Name: " + player_name, True, (255, 255, 255))
        screen.blit(name_text, (120 + 10, 360 + 10))

        pygame.display.flip()

    guardar_ranking(path_ranking_json, player_name, score)

    pygame.display.flip()
    #pygame.time.delay(3000)  # Pausa el juego durante 3 segundos
    

rivales_group = pygame.sprite.Group()

def crear_rival():
    global timer

    if len(rivales_group) < MAX_RIVALES:  # Verificar la cantidad actual de rivales
        timer += 1  # Incrementar el temporizador en cada iteración

        if timer >= FRECUENCIA_RIVALES:  # Controlar la frecuencia de aparición de los rivales
            x = random.randint(auto.rect.left, auto.rect.right)  # Posición X aleatoria dentro del área del auto
            y = random.randint(-200, -50)  # Posición Y aleatoria arriba de la pantalla

            # Crear un auto rival con una imagen aleatoria
            if random.random() < 0.5:
                rival = Rival(image_folder + "autoblanco.png", SIZE_RIVAL, (x, y))
            elif random.random() > 0.5 and random.random() < 0.8:
                rival = Rival(image_folder + "autoverde.png", SIZE_RIVAL, (x, y))
            else:
                rival = Rival(image_folder + "autoamarillo.png", SIZE_RIVAL, (x, y))
            rivales_group.add(rival)

            timer = 0  # Reiniciar el temporizador después de crear un nuevo rival

            # Establecer posición Y negativa para que aparezcan arriba
            rival.rect.y = y

def rival_colision():
    global vidas
    global score

    colisiones = pygame.sprite.spritecollide(auto, rivales_group, True)
    colisiones_diamantes = pygame.sprite.spritecollide(auto, diamantes_group, True)
    colisiones_vidas = pygame.sprite.spritecollide(auto, vidas_group, True)

    if colisiones:
        sound.play()
        sound_acelerar.stop()
        vidas -= 10  # Descuenta un 10% de vida por colisión con un rival
        explosion_imagen = pygame.image.load(image_folder + "explosion.png").convert_alpha()
        explosion_rect = explosion_imagen.get_rect()
        explosion_rect.center = colisiones[0].rect.center  # Posición de la primera colisión
        screen.blit(explosion_imagen, explosion_rect)
        pygame.time.delay(250)  # Pausa el juego durante 1 segundos

    if colisiones_diamantes:
        sound_diamante.play()
        score += 10
    
    if colisiones_vidas:
        sound_vida.play()
        vidas += 10

def start_game():
    global pos_fondo, timer, vidas, score
    pos_fondo = 0
    timer = 0
    vidas = 30
    score = 0
    velocidad_auto = 5
    direccion_auto = (0, 0)

    while True:

        clock.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT:
                    auto.velocidad_x = -SPEED_AUTO
                    sound_acelerar.play()
                    
                    auto.image = pygame.image.load(path_auto_mov_izq).convert_alpha()
                    auto.image = pygame.transform.scale(auto.image, (auto.rect.width, auto.rect.height))

                    
                elif evento.key == pygame.K_RIGHT:
                    auto.velocidad_x = SPEED_AUTO
                    sound_acelerar.play()

                    auto.image = pygame.image.load(path_auto_mov_der).convert_alpha()
                    auto.image = pygame.transform.scale(auto.image, (auto.rect.width, auto.rect.height))

                    

                elif evento.key == pygame.K_UP:
                    auto.velocidad_y = -SPEED_AUTO
                    sound_acelerar.play()
                    auto.image = pygame.image.load(path_auto_mov_up).convert_alpha()
                    auto.image = pygame.transform.scale(auto.image, (auto.rect.width, auto.rect.height))
                    
                    #auto.activar_nitro(auto, nitros)
                elif evento.key == pygame.K_DOWN:
                    auto.velocidad_y = SPEED_AUTO
                    sound_acelerar.play()
                    auto.image = pygame.image.load(path_auto_mov_down).convert_alpha()
                    auto.image = pygame.transform.scale(auto.image, (auto.rect.width, auto.rect.height))
                    

            elif evento.type == pygame.KEYUP:
                auto.image = pygame.image.load(path_auto).convert_alpha()
                auto.image = pygame.transform.scale(auto.image, (auto.rect.width, auto.rect.height))
                    
                if evento.key == pygame.K_LEFT:
                    auto.velocidad_x = 0
                    
                elif evento.key == pygame.K_RIGHT:
                    auto.velocidad_x = 0
                    

                elif evento.key == pygame.K_UP:
                    auto.velocidad_y = 0
                    
                elif evento.key == pygame.K_DOWN:
                    auto.velocidad_y = 0
                    

        pos_fondo += 5 # movimiento al fondo/calle

        if auto.rect.left <= 0:
            auto.rect.left = 0
        elif auto.rect.right > screen.get_width():
            auto.rect.right = screen.get_width()
        elif auto.rect.bottom > screen.get_height():
            auto.rect.bottom = screen.get_height()

        crear_rival()
        rivales_group.update()

        crear_diamante()
        diamantes_group.update()

        crear_vida()
        vidas_group.update()

        screen.blit(fondo, (0, pos_fondo))
        screen.blit(fondo, (0, pos_fondo - fondo_alto))

        mostrar_vidas()
        mostrar_puntaje()

        screen.blit(auto.image, auto.rect)
        auto.update()

        for rival in rivales_group:
            rival.update()

        rivales_group.draw(screen)
        auto.update()
        

        rival_colision()

        # Verificar si se necesita reiniciar la posición del fondo
        if pos_fondo >= fondo_alto:
            pos_fondo = 0

        if vidas <= 0:
            # Acción a realizar cuando las vidas llegan a cero (por ejemplo, reiniciar el juego o mostrar "Game Over")
            # Reiniciar el juego
            pos_fondo = 0
            timer = 0
            sound_game_over.play()
            mostrar_game_over()
            main_menu()



        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:  # Si se presiona la tecla Enter
                main_menu()  # Regresar al menú principal

        colisiones_diamantes = pygame.sprite.spritecollide(auto, diamantes_group, True)

        if colisiones_diamantes:
            sound_diamante.play()
            score += 10

        colisiones_vidas = pygame.sprite.spritecollide(auto, vidas_group, True)

        if colisiones_vidas:
            sound_vida.play()
            vidas += 10

        # Actualizar la posición del auto en función de la dirección y velocidad
        auto.rect.x += velocidad_auto * direccion_auto[0]
        auto.rect.y += velocidad_auto * direccion_auto[1]

        diamantes_group.update()
        diamantes_group.draw(screen)

        vidas_group.update()
        vidas_group.draw(screen)

        pygame.display.flip()
        clock.tick(80)

def get_font(size):
    return pygame.font.Font(path_fuente, size)

def options():
    while True:
        sound_inicio2.play()
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        screen.fill("white")

        OPTIONS_TEXT = get_font(20).render("← IZQUIERDA, → DERECHA, ↓ ABAJO, ↑ ARRIBA " , True,"Black") 
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(400, 50))
        screen.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = Button(image=None, pos=(640, 460),
                              text_input="BACK", font=get_font(60), base_color="Black", hovering_color="Pink")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    sound_inicio2.stop()
                    main_menu()

        pygame.display.update()

def ranking():
    while True:
        sound_inicio2.play()
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()
        
        screen.fill("white")

        OPTIONS_TEXT = get_font(60).render("- - - TOP PLAYERS - - -" , True,"Black") 

        titulo_text = get_font(30).render(f"   TOP       PLAYER       SCORE", True, "Black")
        titulo_rect = titulo_text.get_rect(center=(400, 130))

        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(400, 50))
        
        screen.blit(OPTIONS_TEXT, OPTIONS_RECT)
        screen.blit(titulo_text, titulo_rect)

        OPTIONS_BACK = Button(image=None, pos=(690, 560),
                              text_input="BACK", font=get_font(60), base_color="Black", hovering_color="Pink")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    sound_inicio2.stop()
                    main_menu()


        lista_score_ordenado = []
        with open(path_ranking_json, "r") as archivo:
        #ordeno los datos por score en orden descendente
            #Mostrar los datos en forma descendente
            cadena = ""
            for i in archivo:
                cadena += i
            # Separar los elementos utilizando "{"
            elementos = cadena.split("{")
            # Filtrar los elementos que contienen "}"
            elementos = [elemento for elemento in elementos if "}" in elemento]
            # Ordenar los elementos por score en orden descendente
            elementos_ordenados = sorted(elementos, key=lambda x: int(x.split('"score": "')[1].split('"')[0]), reverse=True)
            # Imprimir los elementos ordenados
            for elemento in elementos_ordenados:
                elemento = "{" + elemento.strip()
                lista_score_ordenado.append(elemento)

            y=180
            top = 1
            for dato in lista_score_ordenado:
                diccionario = json.loads(dato)
                player = diccionario["player"]
                score = diccionario["score"]

                if top <= 10:
                    top_text = get_font(25).render(f"{top}", True, "Black")
                    top_rect = top_text.get_rect(center=(260, y))
                    player_text = get_font(25).render(f"{player}", True, "Black")
                    player_rect = player_text.get_rect(center=(400, y))
                    score_text = get_font(25).render(f"{score}", True, "Black")
                    score_rect = score_text.get_rect(center=(530, y))
                    top+=1

                screen.blit(top_text, top_rect)
                screen.blit(score_text, score_rect)
                screen.blit(player_text, player_rect)
                y+=30


        pygame.display.update()

def main_menu():
    while True:
        sound_inicio2.play()
        screen.blit(menu_principal, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        PLAY_BUTTON = Button(image=pygame.image.load(image_folder + "Opciones.png"), pos=(640, 250),
                             text_input="PLAY", font=get_font(30), base_color="#3b3b3b", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load(image_folder + "Opciones.png"), pos=(640, 340),
                                text_input="Instrucciones", font=get_font(30), base_color="#3b3b3b",
                                hovering_color="White")
        RANKING_BUTTON = Button(image=pygame.image.load(image_folder + "Opciones.png"), pos=(640, 410),
                        text_input="Ranking Player", font=get_font(30), base_color="#3b3b3b",
                        hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load(image_folder + "Opciones.png"), pos=(640, 480),
                             text_input="QUIT", font=get_font(30), base_color="#3b3b3b", hovering_color="White")

        PLAY_BUTTON.changeColor(MENU_MOUSE_POS)
        OPTIONS_BUTTON.changeColor(MENU_MOUSE_POS)
        RANKING_BUTTON.changeColor(MENU_MOUSE_POS)
        QUIT_BUTTON.changeColor(MENU_MOUSE_POS)

        PLAY_BUTTON.update(screen)
        OPTIONS_BUTTON.update(screen)
        RANKING_BUTTON.update(screen)
        QUIT_BUTTON.update(screen)



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.time.wait(500)

                    
                    sound_inicio2.stop()
                    start_game()  # Llamar a la función "start_game()" para iniciar el juego
                elif OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    sound_inicio2.stop()
                    options()  # Llamar a la función "options()" para mostrar las instrucciones
                elif RANKING_BUTTON.checkForInput(MENU_MOUSE_POS):
                    sound_inicio2.stop()
                    ranking()  # Llamar a la función "ranking()" para mostrar el top de players
                elif QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    sound_inicio2.stop()
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu()




