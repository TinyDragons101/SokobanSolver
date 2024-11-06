import math
import os
import pygame
import threading

from src.utils import *

pygame.init()

# Config path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(CURRENT_DIR, "images")

# Config display
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

FPS = 30

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)

BACKGROUND_COLOR = (185, 160, 80)

DARKEN_COLOR = (0, 0, 0, 200)

BUTTON_COLOR = (71, 38, 17)
SELECTED_BUTTON_COLOR = (141, 78, 36)

TEXT_COLOR = (180, 88, 38)

GAME_COLOR = (20, 18, 20)

# Define position & size
BUTTON_WIDTH = 300
BUTTON_HEIGHT = 65

TEXT_SIZE = 54

MINI_FRAME_LEFT = 480
MINI_FRAME_TOP = 385
MINI_FRAME_WIDTH = 316
MINI_FRAME_HEIGHT = 244
MINI_FRAME_BORDER_SIZE = 2
MINI_FRAME_THICK = 2

FRAME_LEFT = 480
FRAME_TOP = 100
FRAME_WIDTH = 790
FRAME_HEIGHT = 610
FRAME_BORDER_SIZE = 5
FRAME_THICK = 5

MINI_TILE_SIZE = 20
TILE_SIZE = 50

# Class for normal button & polygon button
class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR, text_color=TEXT_COLOR, text_size=TEXT_SIZE):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.font = pygame.font.Font(None, text_size)
        self.font.set_italic(True)
        self.text_surface = self.font.render(text, True, text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        surface.blit(self.text_surface, self.text_rect)

    def change_color(self, color):
        self.color = color
        
    def is_selected(self, pos):
        return self.rect.collidepoint(pos)
    
class PolygonButton:
    def __init__(self, polygon, color=BUTTON_COLOR):
        self.polygon = polygon
        self.color = color

    def draw(self, surface):
        self.rect = pygame.draw.polygon(surface, self.color, self.polygon)
        
    def change_color(self, color):
        self.color = color

    def is_selected(self, pos):
        return self.rect.collidepoint(pos)

### Variables for start screen
starting = True

levels = os.listdir(CURRENT_DIR)
levels = [filename for filename in levels if filename[0:2] == "in"]
level_index = 0

# Variables for visualizing algorithm
initial_game_state = None
game_state = None
pos_of_ares = None
stone_weight = None
pos_of_stones = None
stones = None
previous_move = None

# Variables for graphics
title = pygame.image.load(os.path.join(IMAGE_DIR, "title.png"))

mini_board_frame = pygame.Rect(MINI_FRAME_LEFT, MINI_FRAME_TOP, MINI_FRAME_WIDTH, MINI_FRAME_HEIGHT)

wall = pygame.image.load(os.path.join(IMAGE_DIR, "wall.png"))
ares_back = pygame.image.load(os.path.join(IMAGE_DIR, "ares_back.png"))
ares_front = pygame.image.load(os.path.join(IMAGE_DIR, "ares_front.png"))
ares_left = pygame.image.load(os.path.join(IMAGE_DIR, "ares_left.png"))
ares_right = pygame.image.load(os.path.join(IMAGE_DIR, "ares_right.png"))
stone = pygame.image.load(os.path.join(IMAGE_DIR, "stone.png"))
stone_on_switch = pygame.image.load(os.path.join(IMAGE_DIR, "stone_on_switch.png"))

fit_tile_size = None
fit_wall = None
fit_ares_back = None
fit_ares_front = None
fit_ares_left = None
fit_ares_right = None
fit_stone = None
fit_stone_on_switch = None

# Variables for buttons
level_decrease_button = PolygonButton([(470, 479), (470, 539), (420, 509)])
level_increase_button = PolygonButton([(810, 479), (810, 539), (860, 509)])

start_button = Button((SCREEN_WIDTH - BUTTON_WIDTH) // 2, 640, BUTTON_WIDTH, BUTTON_HEIGHT, "START")

# Variables for loading
loading = False
current_angle = math.pi / 2

### Functions for start screen

# Load level from input file for minimap
def load_level():
    global initial_game_state
    global game_state
    global pos_of_ares
    global stone_weight
    global pos_of_stones
    global stones
    global previous_move
    global fit_tile_size
    global fit_wall
    global fit_ares_back
    global fit_ares_front
    global fit_ares_left
    global fit_ares_right
    global fit_stone
    global fit_stone_on_switch

    initial_game_state, stone_weight = get_game_state(os.path.join(CURRENT_DIR, levels[level_index]))
    game_state = np.copy(initial_game_state)
    pos_of_stones = [tuple(x) for x in np.argwhere((game_state == 3) | (game_state == 5))]
    stones = dict()
    for index, pos in enumerate(pos_of_stones):
        stones[pos] = stone_weight[index]
    pos_of_ares = np.argwhere((game_state == 2) | (game_state == 6))[0]
    previous_move = 'd'

    width = game_state.shape[1] * MINI_TILE_SIZE
    height = game_state.shape[0] * MINI_TILE_SIZE
    fit_tile_size = min(int((MINI_FRAME_WIDTH - 8)/ width * MINI_TILE_SIZE), int((MINI_FRAME_HEIGHT - 8)/ height * MINI_TILE_SIZE))
    fit_wall = pygame.transform.scale(wall, (fit_tile_size, fit_tile_size))
    fit_ares_back = pygame.transform.scale(ares_back, (fit_tile_size, fit_tile_size))
    fit_ares_front = pygame.transform.scale(ares_front, (fit_tile_size, fit_tile_size))
    fit_ares_left = pygame.transform.scale(ares_left, (fit_tile_size, fit_tile_size))
    fit_ares_right = pygame.transform.scale(ares_right, (fit_tile_size, fit_tile_size))
    fit_stone = pygame.transform.scale(stone, (fit_tile_size, fit_tile_size))
    fit_stone_on_switch = pygame.transform.scale(stone_on_switch, (fit_tile_size, fit_tile_size))

# Draw mini maze & real maze
def draw_maze(screen, font_size, frame_left=FRAME_LEFT, frame_top=FRAME_TOP, frame_width=FRAME_WIDTH, frame_height=FRAME_HEIGHT, tile_size=TILE_SIZE):
    width = game_state.shape[1] * fit_tile_size
    height = game_state.shape[0] * fit_tile_size
    game_surface = pygame.Surface((width, height))

    font = pygame.font.Font(None, int(fit_tile_size / tile_size * font_size))

    game_surface.fill(GAME_COLOR)

    # Draw maze grid
    for i in range(game_state.shape[0]):
        for j in range(game_state.shape[1]):
            if game_state[i, j] == -1:
                pygame.draw.rect(game_surface, BACKGROUND_COLOR, (j * fit_tile_size, i * fit_tile_size, fit_tile_size, fit_tile_size))
            if game_state[i, j] == 1:
                game_surface.blit(fit_wall, (j * fit_tile_size, i * fit_tile_size))
            elif game_state[i, j] == 2 or game_state[i, j] == 6:
                if game_state[i, j] == 6:
                    center = (j * fit_tile_size + fit_tile_size // 2, i * fit_tile_size + fit_tile_size // 2)
                    pygame.draw.polygon(game_surface, RED, [
                        (center[0] - fit_tile_size // 4, center[1]),
                        (center[0], center[1] - fit_tile_size // 4),
                        (center[0] + fit_tile_size // 4, center[1]),
                        (center[0], center[1] + fit_tile_size // 4),
                    ])
                if previous_move == 'u':
                    game_surface.blit(fit_ares_back, (j * fit_tile_size, i * fit_tile_size))
                elif previous_move == 'r':
                    game_surface.blit(fit_ares_right, (j * fit_tile_size, i * fit_tile_size))
                elif previous_move == 'd':
                    game_surface.blit(fit_ares_front, (j * fit_tile_size, i * fit_tile_size))
                elif previous_move == 'l':
                    game_surface.blit(fit_ares_left, (j * fit_tile_size, i * fit_tile_size))
            elif game_state[i, j] == 3:
                game_surface.blit(fit_stone, (j * fit_tile_size, i * fit_tile_size))
                center = (j * fit_tile_size + fit_tile_size // 2, i * fit_tile_size + fit_tile_size // 2)
                pygame.draw.circle(game_surface, WHITE, center, fit_tile_size // 4)
                weight_text = font.render(str(stones[(i, j)]), True, BLACK)
                weight_rect = weight_text.get_rect(center=center)
                game_surface.blit(weight_text, weight_rect)
            elif game_state[i, j] == 4:
                center = (j * fit_tile_size + fit_tile_size // 2, i * fit_tile_size + fit_tile_size // 2)
                pygame.draw.polygon(game_surface, RED, [
                    (center[0] - fit_tile_size // 4, center[1]),
                    (center[0], center[1] - fit_tile_size // 4),
                    (center[0] + fit_tile_size // 4, center[1]),
                    (center[0], center[1] + fit_tile_size // 4),
                ])
            elif game_state[i, j] == 5:
                game_surface.blit(fit_stone_on_switch, (j * fit_tile_size, i * fit_tile_size))
                center = (j * fit_tile_size + fit_tile_size // 2, i * fit_tile_size + fit_tile_size // 2)
                pygame.draw.circle(game_surface, WHITE, center, fit_tile_size // 4)
                weight_text = font.render(str(stones[(i, j)]), True, BLACK)
                weight_rect = weight_text.get_rect(center=center)
                game_surface.blit(weight_text, weight_rect)

    screen.blit(game_surface, (frame_left + (frame_width - width) // 2, (frame_top + (frame_height - height) // 2)))

# Draw start screen
def draw_start_screen(screen):
    font = pygame.font.Font(None, int((8 / 9) * TEXT_SIZE))
    font.set_italic(True)
    choose_level_text = font.render("Choose level", True, BUTTON_COLOR)
    choose_level_rect = choose_level_text.get_rect(center=(640, 280))
    level_text = font.render(levels[level_index], True, TEXT_COLOR)
    level_rect = level_text.get_rect(center=(640, 340))

    screen.fill(BACKGROUND_COLOR)
    screen.blit(title, (0, 0))
    screen.blit(choose_level_text, choose_level_rect)
    screen.blit(level_text, level_rect)
    level_decrease_button.draw(screen)
    level_increase_button.draw(screen)
    pygame.draw.rect(screen, BUTTON_COLOR, mini_board_frame, MINI_FRAME_BORDER_SIZE, MINI_FRAME_THICK)
    draw_maze(screen, 12, MINI_FRAME_LEFT, MINI_FRAME_TOP, MINI_FRAME_WIDTH, MINI_FRAME_HEIGHT, MINI_TILE_SIZE)
    start_button.draw(screen)

# Draw loading during executing algorithm
def draw_loading(screen):
    darken_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    
    center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    radius = 80
    width = 30
    loading_rect = pygame.Rect(center[0] - radius, center[1] - radius, radius * 2, radius * 2)

    darken_surface.fill(DARKEN_COLOR)
    pygame.draw.circle(darken_surface, BACKGROUND_COLOR, center, radius, width)
    pygame.draw.arc(darken_surface, WHITE, loading_rect, current_angle - 3 * math.pi / 2, current_angle, width)

    screen.blit(darken_surface, (0, 0))

### Variables for game screen
gaming = False

algorithms = ['BFS', 'DFS', 'UCS', 'A*']
algorithm_index = 0

# Variables for visualizing algorithm
all_steps = None
steps = None
step_index = None
all_weights = None
weight = None
previous_states = None

frame_cnt = 0

# Variables for buttons
return_button = PolygonButton([(20, 20), (20, 80), (60, 80), (60, 20)])
return_button_selected = False

algorithm_left_button = PolygonButton([(90, 250), (90, 310), (50, 280)])
algorithm_right_button = PolygonButton([(290, 250), (290, 310), (330, 280)])

back_button = PolygonButton([(780, 40), (835, 40), (835, 80), (780, 80)], BACKGROUND_COLOR)
back_button_selected = False

play_pause_button = PolygonButton([(860, 30), (900, 30), (900, 90), (860, 90)], BACKGROUND_COLOR)
play_pause_button_selected = False

next_button = PolygonButton([(925, 40), (980, 40), (980, 80), (925, 80)], BACKGROUND_COLOR)
next_button_selected = False

reset_button = PolygonButton([(1210, 30), (1270, 30), (1270, 90), (1210, 90)], BACKGROUND_COLOR)
reset_button_selected = False

board_frame = pygame.Rect(FRAME_LEFT, FRAME_TOP, FRAME_WIDTH, FRAME_HEIGHT)

# Variables for load complete event
LOAD_COMPLETE_EVENT = pygame.USEREVENT + 1

# Variable for playing algorithm
playing = False

### Functions for game screen

# Execute search or load search results from file
def load():
    global algorithm_index
    global all_steps
    global step_index
    global all_weights
    global weight
    global previous_move
    global previous_states
    global frame_cnt
    global fit_tile_size
    global fit_wall
    global fit_ares_back
    global fit_ares_front
    global fit_ares_left
    global fit_ares_right
    global fit_stone
    global fit_stone_on_switch
    
    algorithm_index = 0

    all_steps, all_weights = execute_search(levels[level_index])

    step_index = 0
    weight = 0
    previous_move = 'd'
    previous_states = []

    width = game_state.shape[1] * TILE_SIZE
    height = game_state.shape[0] * TILE_SIZE
    fit_tile_size = min(int((FRAME_WIDTH - 20)/ width * TILE_SIZE), int((FRAME_HEIGHT - 20)/ height * TILE_SIZE))
    fit_wall = pygame.transform.scale(wall, (fit_tile_size, fit_tile_size))
    fit_ares_back = pygame.transform.scale(ares_back, (fit_tile_size, fit_tile_size))
    fit_ares_front = pygame.transform.scale(ares_front, (fit_tile_size, fit_tile_size))
    fit_ares_left = pygame.transform.scale(ares_left, (fit_tile_size, fit_tile_size))
    fit_ares_right = pygame.transform.scale(ares_right, (fit_tile_size, fit_tile_size))
    fit_stone = pygame.transform.scale(stone, (fit_tile_size, fit_tile_size))
    fit_stone_on_switch = pygame.transform.scale(stone_on_switch, (fit_tile_size, fit_tile_size))

    pygame.event.post(pygame.event.Event(LOAD_COMPLETE_EVENT))

# Draw game screen
def draw_game_screen(screen):
    font = pygame.font.Font(None, TEXT_SIZE)
    step_text = font.render("Step: " + str(step_index) + "/" + str(len(steps)), True, BUTTON_COLOR)
    weight_text = font.render("Weight: " + str(weight) + "/" + str(all_weights[algorithms[algorithm_index]]), True, BUTTON_COLOR)
    algorithm_text = font.render("Algorithm: ", True, BUTTON_COLOR)
    algortihm_chosen_text = font.render(algorithms[algorithm_index], True, BUTTON_COLOR)
    algortihm_chosen_rect = algortihm_chosen_text.get_rect(center=(190, 280))

    screen.fill(BACKGROUND_COLOR)

    return_button.draw(screen)
    pygame.draw.rect(screen, WHITE, (25, 25, 30, 55))
    if return_button_selected:
        pygame.draw.polygon(screen, SELECTED_BUTTON_COLOR, [(26, 26), (26, 80), (50, 90), (50, 16)])
    else:  
        pygame.draw.polygon(screen, BUTTON_COLOR, [(26, 26), (26, 80), (50, 90), (50, 16)])
    pygame.draw.circle(screen, WHITE, (45, 53), 2)

    algorithm_left_button.draw(screen)
    algorithm_right_button.draw(screen)
    screen.blit(step_text, (50, 100))
    screen.blit(weight_text, (50, 150))
    screen.blit(algorithm_text, (50, 200))
    screen.blit(algortihm_chosen_text, algortihm_chosen_rect)

    back_button.draw(screen)
    if back_button_selected:
        pygame.draw.polygon(screen, SELECTED_BUTTON_COLOR, [(820, 40), (820, 80), (780, 60)])
        pygame.draw.rect(screen, SELECTED_BUTTON_COLOR, (825, 40, 10, 40))
    else:
        pygame.draw.polygon(screen, BUTTON_COLOR, [(820, 40), (820, 80), (780, 60)])
        pygame.draw.rect(screen, BUTTON_COLOR, (825, 40, 10, 40))

    play_pause_button.draw(screen)
    if playing:
        if play_pause_button_selected:
            pygame.draw.rect(screen, SELECTED_BUTTON_COLOR, (860, 30, 15, 60))
            pygame.draw.rect(screen, SELECTED_BUTTON_COLOR, (885, 30, 15, 60))
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, (860, 30, 15, 60))
            pygame.draw.rect(screen, BUTTON_COLOR, (885, 30, 15, 60))
    else:
        if play_pause_button_selected:
            pygame.draw.polygon(screen, SELECTED_BUTTON_COLOR, [(860, 30), (860, 90), (900, 60)])
        else:
            pygame.draw.polygon(screen, BUTTON_COLOR, [(860, 30), (860, 90), (900, 60)])

    next_button.draw(screen)
    if next_button_selected:
        pygame.draw.rect(screen, SELECTED_BUTTON_COLOR, (925, 40, 10, 40))
        pygame.draw.polygon(screen, SELECTED_BUTTON_COLOR, [(940, 40), (940, 80), (980, 60)])
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, (925, 40, 10, 40))
        pygame.draw.polygon(screen, BUTTON_COLOR, [(940, 40), (940, 80), (980, 60)])

    reset_button.draw(screen)
    if reset_button_selected:
        pygame.draw.polygon(screen, SELECTED_BUTTON_COLOR, [(1240, 30), (1240, 55), (1215, 42.5)])
        pygame.draw.rect(screen, SELECTED_BUTTON_COLOR, (1240, 35, 25, 15))
        pygame.draw.rect(screen, SELECTED_BUTTON_COLOR, (1250, 50, 15, 35))
        pygame.draw.rect(screen, SELECTED_BUTTON_COLOR, (1230, 70, 20, 15))
        pygame.draw.rect(screen, SELECTED_BUTTON_COLOR, (1215, 55, 15, 30))
    else:
        pygame.draw.polygon(screen, BUTTON_COLOR, [(1240, 30), (1240, 55), (1215, 42.5)])
        pygame.draw.rect(screen, BUTTON_COLOR, (1240, 35, 25, 15))
        pygame.draw.rect(screen, BUTTON_COLOR, (1250, 50, 15, 35))
        pygame.draw.rect(screen, BUTTON_COLOR, (1230, 70, 20, 15))
        pygame.draw.rect(screen, BUTTON_COLOR, (1215, 55, 15, 30))  
    
    pygame.draw.rect(screen, BUTTON_COLOR, board_frame, FRAME_BORDER_SIZE, FRAME_THICK)
    draw_maze(screen, 30)
    
# Move to previous state
def back_game_state():
    global game_state
    global pos_of_ares
    global step_index
    global weight
    global previous_move
    global previous_states

    if len(previous_states) == 0:
        return
    
    game_state = previous_states.pop()
    step_index -= 1
    if steps[step_index].isupper(): 
        pos_of_stone = pos_of_ares
        pos_of_ares = np.argwhere((game_state == 2) | (game_state == 6))[0]
        old_pos_of_stone = 2 * pos_of_stone - pos_of_ares
        stones[tuple(pos_of_stone)] = stones[tuple(old_pos_of_stone)]
        stones.pop(tuple(old_pos_of_stone))
        weight -= stones[tuple(pos_of_stone)]
    else:
        pos_of_ares = np.argwhere((game_state == 2) | (game_state == 6))[0]
    previous_move = 'd' if step_index == 0 else steps[step_index - 1].lower()

# Move to next_state
def next_game_state():
    global game_state
    global pos_of_ares
    global step_index
    global weight
    global previous_move
    global previous_states
    global playing

    if step_index == len(steps):
        if playing:
            playing = False
        return
    
    previous_states.append(np.copy(game_state))

    step = steps[step_index]
    
    # Update ares
    x, y = pos_of_ares
    if game_state[x, y] == 6: 
        game_state[x, y] = 4
    else: 
        game_state[x, y] = 0
    if step.lower() == 'u':
        new_pos_of_ares = np.array([x - 1, y])
    elif step.lower() == 'd':
        new_pos_of_ares = np.array([x + 1, y])
    elif step.lower() == 'l':
        new_pos_of_ares = np.array([x, y - 1])
    elif step.lower() == 'r':
        new_pos_of_ares = np.array([x, y + 1])
    x, y = new_pos_of_ares
    if game_state[x, y] == 4 or game_state[x, y] == 5: 
        game_state[x, y] = 6
    else: 
        game_state[x, y] = 2

    # Update stone if step is a push
    if step.isupper():
        pos_of_stone = 2 * new_pos_of_ares - pos_of_ares
        stones[tuple(pos_of_stone)] = stones[tuple(new_pos_of_ares)]
        stones.pop(tuple(new_pos_of_ares))
        weight += stones[tuple(pos_of_stone)]
        x, y = pos_of_stone
        if game_state[x, y] == 4:
            game_state[x, y] = 5
        else: 
            game_state[x, y] = 3 

    pos_of_ares = new_pos_of_ares
    step_index += 1
    previous_move = step.lower()

# Reset to initial state
def reset():
    global game_state
    global pos_of_ares
    global stones
    global step_index
    global weight
    global previous_move
    global previous_states
    global playing

    
    game_state = np.copy(initial_game_state)
    pos_of_stones = [tuple(x) for x in np.argwhere((game_state == 3) | (game_state == 5))]
    stones = dict()
    for index, pos in enumerate(pos_of_stones):
        stones[pos] = stone_weight[index]
    pos_of_ares = np.argwhere((game_state == 2) | (game_state == 6))[0]
    step_index = 0
    weight = 0
    previous_move = 'd'
    previous_states = []

    if playing:
        playing = False

# Display settings
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sokoban")

# Prerequisite
load_level()

# Game loop
running = True

while running:
    if starting:
        draw_start_screen(screen)
        if loading:
            draw_loading(screen)
            current_angle = current_angle - math.pi / 6
            if current_angle <= 0:
                current_angle += 2 * math.pi

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                if not loading:
                    if start_button.is_selected(event.pos):
                        start_button.change_color(SELECTED_BUTTON_COLOR)
                    else:
                        start_button.change_color(BUTTON_COLOR)
                    if level_decrease_button.is_selected(event.pos):
                        level_decrease_button.change_color(SELECTED_BUTTON_COLOR)
                    else:
                        level_decrease_button.change_color(BUTTON_COLOR)
                    if level_increase_button.is_selected(event.pos):
                        level_increase_button.change_color(SELECTED_BUTTON_COLOR)
                    else:
                        level_increase_button.change_color(BUTTON_COLOR)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not loading:
                    if start_button.is_selected(event.pos):
                        start_button.change_color(BUTTON_COLOR)
                        threading.Thread(target=load).start()
                        loading = True
                    elif level_decrease_button.is_selected(event.pos):
                        level_decrease_button.change_color(BUTTON_COLOR)
                        level_index = (level_index - 1 + len(levels)) % len(levels)
                        load_level()
                    elif level_increase_button.is_selected(event.pos):
                        level_increase_button.change_color(BUTTON_COLOR)
                        level_index = (level_index + 1) % len(levels)
                        load_level()
            elif event.type == LOAD_COMPLETE_EVENT:
                current_angle = math.pi / 2
                steps = all_steps[algorithms[algorithm_index]]
                if starting and loading:
                    loading = False
                    starting = False
                    gaming = True

    elif gaming:
        if playing:
            if frame_cnt == 0:
                next_game_state()
            frame_cnt = (frame_cnt + 1) % 6
        draw_game_screen(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                if return_button.is_selected(event.pos):
                    return_button.change_color(SELECTED_BUTTON_COLOR)
                    return_button_selected = True
                else:
                    return_button.change_color(BUTTON_COLOR)
                    return_button_selected = False
                if algorithm_left_button.is_selected(event.pos):
                    algorithm_left_button.change_color(SELECTED_BUTTON_COLOR)
                else:
                    algorithm_left_button.change_color(BUTTON_COLOR)
                if algorithm_right_button.is_selected(event.pos):
                    algorithm_right_button.change_color(SELECTED_BUTTON_COLOR)
                else:
                    algorithm_right_button.change_color(BUTTON_COLOR)
                if back_button.is_selected(event.pos) and not playing:
                    back_button_selected = True
                else:
                    back_button_selected = False
                if play_pause_button.is_selected(event.pos):
                    play_pause_button_selected = True
                else:
                    play_pause_button_selected = False
                if next_button.is_selected(event.pos) and not playing:
                    next_button_selected = True
                else:
                    next_button_selected = False
                if reset_button.is_selected(event.pos):
                    reset_button_selected = True
                else:
                    reset_button_selected = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if return_button.is_selected(event.pos):
                    return_button.change_color(BUTTON_COLOR)
                    return_button_selected = False
                    if playing:
                        playing = False
                    gaming = False
                    starting = True
                    load_level()
                elif algorithm_left_button.is_selected(event.pos):
                    algorithm_left_button.change_color(BUTTON_COLOR)
                    algorithm_index = (algorithm_index - 1 + len(algorithms)) % len(algorithms)
                    steps = all_steps[algorithms[algorithm_index]]
                    reset()
                elif algorithm_right_button.is_selected(event.pos):
                    algorithm_right_button.change_color(BUTTON_COLOR)
                    algorithm_index = (algorithm_index + 1) % len(algorithms)
                    steps = all_steps[algorithms[algorithm_index]]
                    reset()
                if back_button.is_selected(event.pos) and not playing:
                    back_button_selected = False
                    back_game_state()
                elif play_pause_button.is_selected(event.pos):
                    play_pause_button_selected = False
                    playing = not playing
                elif next_button.is_selected(event.pos) and not playing:
                    next_button_selected = False
                    next_game_state()
                elif reset_button.is_selected(event.pos):
                    reset_button_selected = False
                    reset()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not playing:
                    back_game_state()
                elif event.key == pygame.K_SPACE:
                    playing = not playing
                elif event.key == pygame.K_RIGHT and not playing:
                    next_game_state()

    pygame.display.flip()
    pygame.time.Clock().tick(FPS)

pygame.quit()