import math
import os
import pygame
import threading

from src.utils import *

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

FPS = 30

BACKGROUND_COLOR = (74, 60, 48)

BUTTON_WIDTH = 300
BUTTON_HEIGHT = 75
BUTTON_COLOR = (71, 38, 17)

TEXT_SIZE = 54
TEXT_COLOR = (140, 68, 28)

DARKEN_COLOR = (0, 0, 0, 200)

FRAME_LEFT = 480
FRAME_TOP = 100
FRAME_WIDTH = 790
FRAME_HEIGHT = 610
BORDER_SIZE = 5

GAME_COLOR = (20, 18, 20)
TILE_SIZE = 50
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(CURRENT_DIR, "images")
TESTS_DIR = os.path.join(CURRENT_DIR, "tests")

class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR, text_size=TEXT_SIZE, text_color=TEXT_COLOR):
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
        
    def is_selected(self, pos):
        return self.rect.collidepoint(pos)
    
class PolygonButton:
    def __init__(self, polygon, color=BUTTON_COLOR):
        self.polygon = polygon
        self.color = color

    def draw(self, surface):
        self.rect = pygame.draw.polygon(surface, self.color, self.polygon)
        
    def is_selected(self, pos):
        return self.rect.collidepoint(pos)

def draw_start_screen(screen):
    title = pygame.image.load(os.path.join(IMAGES_DIR, "title.png"))

    font = pygame.font.Font(None, int((8/9)*TEXT_SIZE))
    font.set_italic(True)
    choose_level_text = font.render("Choose level", True, BUTTON_COLOR)
    choose_level_rect = choose_level_text.get_rect(center=(640, 475))
    level_text = font.render(levels[current_level_index], True, TEXT_COLOR)
    level_rect = level_text.get_rect(center=(640, 540))

    screen.fill(BACKGROUND_COLOR)
    screen.blit(title, (0, 0))
    start_button.draw(screen)
    screen.blit(choose_level_text, choose_level_rect)
    screen.blit(level_text, level_rect)
    level_decrease_button.draw(screen)
    level_increase_button.draw(screen)

def draw_loading(screen):
    darken_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    darken_surface.fill(DARKEN_COLOR)
    
    center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    radius = 80
    width = 30
    loading_rect = pygame.Rect(center[0] - radius, center[1] - radius, radius * 2, radius * 2)
    pygame.draw.circle(darken_surface, BACKGROUND_COLOR, center, radius, width)
    pygame.draw.arc(darken_surface, BUTTON_COLOR, loading_rect, current_angle - math.pi / 3, current_angle, width)

    screen.blit(darken_surface, (0, 0))
    
def load():
    global game_state
    global initial_game_state
    global stone_weight
    global stones
    global pos_of_ares
    global all_steps
    global current_step_index
    global current_weight
    global previous_move
    global previous_states
    global current_algorithm_index
    global tile_size
    global fit_wall
    global fit_ares_back
    global fit_ares_front
    global fit_ares_left
    global fit_ares_right
    global fit_stone
    global fit_stone_on_switch
    global fit_switch

    game_state, stone_weight = get_game_state(levels[current_level_index])
    initial_game_state = np.copy(game_state)
    pos_of_stones = [tuple(x) for x in np.argwhere((game_state == 3) | (game_state == 5))]
    stones = {}
    for index, pos in enumerate(pos_of_stones):
        stones[pos] = stone_weight[index]
    pos_of_ares = np.argwhere((game_state == 2) | (game_state == 6))[0]
    all_steps = execute_search(game_state, stone_weight)

    current_step_index = 0
    current_weight = 0
    previous_move = 'd'
    previous_states = []
    current_algorithm_index = 0

    width = game_state.shape[1] * TILE_SIZE
    height = game_state.shape[0] * TILE_SIZE
    tile_size = min(int((FRAME_WIDTH - 20)/ width * TILE_SIZE), int((FRAME_HEIGHT - 20)/ height * TILE_SIZE))
    fit_wall = pygame.transform.scale(wall, (tile_size, tile_size))
    fit_ares_back = pygame.transform.scale(ares_back, (tile_size, tile_size))
    fit_ares_front = pygame.transform.scale(ares_front, (tile_size, tile_size))
    fit_ares_left = pygame.transform.scale(ares_left, (tile_size, tile_size))
    fit_ares_right = pygame.transform.scale(ares_right, (tile_size, tile_size))
    fit_stone = pygame.transform.scale(stone, (tile_size, tile_size))
    fit_stone_on_switch = pygame.transform.scale(stone_on_switch, (tile_size, tile_size))
    fit_switch = pygame.transform.scale(switch, (tile_size, tile_size))

    pygame.event.post(pygame.event.Event(LOAD_COMPLETE_EVENT))

def draw_game_map(screen):
    font = pygame.font.Font(None, int(tile_size / TILE_SIZE * 30))

    width = game_state.shape[1] * tile_size
    height = game_state.shape[0] * tile_size
    game_surface = pygame.Surface((width, height))
    game_surface.fill(GAME_COLOR)

    for i in range(game_state.shape[0]):
        for j in range(game_state.shape[1]):
            if game_state[i, j] == -1:
                pygame.draw.rect(game_surface, BACKGROUND_COLOR, (j * tile_size, i * tile_size, tile_size, tile_size))
            if game_state[i, j] == 1:
                game_surface.blit(fit_wall, (j * tile_size, i * tile_size))
            elif game_state[i, j] == 2 or game_state[i, j] == 6:
                if game_state[i, j] == 6:
                    game_surface.blit(fit_switch, (j * tile_size, i * tile_size))
                if previous_move == 'u':
                    game_surface.blit(fit_ares_back, (j * tile_size, i * tile_size))
                elif previous_move == 'd':
                    game_surface.blit(fit_ares_front, (j * tile_size, i * tile_size))
                elif previous_move == 'l':
                    game_surface.blit(fit_ares_left, (j * tile_size, i * tile_size))
                elif previous_move == 'r':
                    game_surface.blit(fit_ares_right, (j * tile_size, i * tile_size))
            elif game_state[i, j] == 3:
                game_surface.blit(fit_stone, (j * tile_size, i * tile_size))
                center = (j * tile_size + tile_size // 2, i * tile_size + tile_size // 2)
                pygame.draw.circle(game_surface, WHITE, center, tile_size // 4)
                weight_text = font.render(str(stones[(i, j)]), True, BLACK)
                weight_rect = weight_text.get_rect(center=center)
                game_surface.blit(weight_text, weight_rect)
            elif game_state[i, j] == 4:
                game_surface.blit(fit_switch, (j * tile_size, i * tile_size))
            elif game_state[i, j] == 5:
                game_surface.blit(fit_stone_on_switch, (j * tile_size, i * tile_size))
                center = (j * tile_size + tile_size // 2, i * tile_size + tile_size // 2)
                pygame.draw.circle(game_surface, WHITE, center, tile_size // 4)
                weight_text = font.render(str(stones[(i, j)]), True, BLACK)
                weight_rect = weight_text.get_rect(center=center)
                game_surface.blit(weight_text, weight_rect)

    screen.blit(game_surface, (FRAME_LEFT + (FRAME_WIDTH - width) // 2, (FRAME_TOP + (FRAME_HEIGHT - height) // 2)))

def draw_game_screen(screen):
    board_frame = pygame.Rect(FRAME_LEFT, FRAME_TOP, FRAME_WIDTH, FRAME_HEIGHT)
    font = pygame.font.Font(None, TEXT_SIZE)
    step_text = font.render("Step: " + str(current_step_index), True, BUTTON_COLOR)
    weight_text = font.render("Weight: " + str(current_weight), True, BUTTON_COLOR)
    algorithm_text = font.render("Algorithm: ", True, BUTTON_COLOR)
    algortihm_chosen_text = font.render(algorithms[current_algorithm_index], True, BUTTON_COLOR)
    algortihm_chosen_rect = algortihm_chosen_text.get_rect(center=(190, 280))

    screen.fill(BACKGROUND_COLOR)

    return_button.draw(screen)
    algorithm_left_button.draw(screen)
    algorithm_right_button.draw(screen)

    screen.blit(step_text, (50, 100))
    screen.blit(weight_text, (50, 150))
    screen.blit(algorithm_text, (50, 200))
    screen.blit(algortihm_chosen_text, algortihm_chosen_rect)

    back_button.draw(screen)
    play_pause_button.draw(screen)
    next_button.draw(screen)
    reset_button.draw(screen)

    pygame.draw.rect(screen, WHITE, (25, 25, 30, 55))
    pygame.draw.polygon(screen, BUTTON_COLOR, [(26, 26), (26, 80), (50, 90), (50, 16)])
    pygame.draw.circle(screen, WHITE, (45, 53), 2)

    pygame.draw.polygon(screen, BUTTON_COLOR, [(820, 40), (820, 80), (780, 60)])
    pygame.draw.rect(screen, BUTTON_COLOR, (825, 40, 10, 40))
    if playing:
        pygame.draw.rect(screen, BUTTON_COLOR, (860, 30, 15, 60))
        pygame.draw.rect(screen, BUTTON_COLOR, (885, 30, 15, 60))
    else:
        pygame.draw.polygon(screen, BUTTON_COLOR, [(860, 30), (860, 90), (900, 60)])
    pygame.draw.rect(screen, BUTTON_COLOR, (925, 40, 10, 40))
    pygame.draw.polygon(screen, BUTTON_COLOR, [(940, 40), (940, 80), (980, 60)])
    pygame.draw.rect(screen, BUTTON_COLOR, board_frame, BORDER_SIZE, BORDER_SIZE)
    pygame.draw.arc(screen, TEXT_COLOR, (1220, 40, 40, 40), - math.pi, math.pi / 2, 10)
    pygame.draw.polygon(screen, TEXT_COLOR, [(1240, 35), (1240, 55), (1225, 45)])

    draw_game_map(screen)

def back_game_state(previous_states):
    global game_state
    global current_step_index
    global current_weight
    global previous_move
    global pos_of_ares

    if len(previous_states) == 0:
        return
    game_state = previous_states.pop()
    current_step_index -= 1
    if steps[current_step_index].isupper(): 
        pos_of_stone = pos_of_ares
    previous_move = 'd' if current_step_index == 0 else steps[current_step_index - 1].lower()
    pos_of_ares = np.argwhere((game_state == 2) | (game_state == 6))[0]
    if steps[current_step_index].isupper():
        old_pos_of_stone = 2 * pos_of_stone - pos_of_ares
        stones[tuple(pos_of_stone)] = stones[tuple(old_pos_of_stone)]
        stones.pop(tuple(old_pos_of_stone))
        current_weight -= stones[tuple(pos_of_stone)]

def next_game_state(game_state, previous_states):
    global current_step_index
    global current_weight
    global previous_move
    global pos_of_ares
    global playing

    if current_step_index == len(steps):
        if playing:
            playing = False
        return

    previous_states.append(np.copy(game_state))

    current_step = steps[current_step_index]
    x, y = pos_of_ares

    if game_state[x, y] == 6: 
        game_state[x, y] = 4
    else: 
        game_state[x, y] = 0

    if current_step.lower() == 'u':
        new_pos_of_ares = np.array([x - 1, y])
    elif current_step.lower() == 'd':
        new_pos_of_ares = np.array([x + 1, y])
    elif current_step.lower() == 'l':
        new_pos_of_ares = np.array([x, y - 1])
    elif current_step.lower() == 'r':
        new_pos_of_ares = np.array([x, y + 1])
    
    if current_step.isupper():
        pos_of_stone = 2 * new_pos_of_ares - pos_of_ares
        stones[tuple(pos_of_stone)] = stones[tuple(new_pos_of_ares)]
        stones.pop(tuple(new_pos_of_ares))
        current_weight += stones[tuple(pos_of_stone)]
        x, y = pos_of_stone
        if game_state[x, y] == 4:
            game_state[x, y] = 5
        else: 
            game_state[x, y] = 3 

    x, y = new_pos_of_ares
    if game_state[x, y] == 4 or game_state[x, y] == 5: game_state[x, y] = 6
    else: game_state[x, y] = 2

    current_step_index += 1
    previous_move = current_step.lower()
    pos_of_ares = new_pos_of_ares


def reset():
    global playing
    global game_state
    global stones
    global pos_of_ares
    global current_step_index
    global current_weight
    global previous_move
    global previous_states

    if playing:
        playing = False
    game_state = np.copy(initial_game_state)
    pos_of_stones = [tuple(x) for x in np.argwhere((game_state == 3) | (game_state == 5))]
    stones = {}
    for index, pos in enumerate(pos_of_stones):
        stones[pos] = stone_weight[index]
    pos_of_ares = np.argwhere((game_state == 2) | (game_state == 6))[0]
    current_step_index = 0
    current_weight = 0
    previous_move = 'd'
    previous_states = []

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sokoban")

running = True

start_button = Button((SCREEN_WIDTH - BUTTON_WIDTH) // 2, 350, BUTTON_WIDTH, BUTTON_HEIGHT, "START")

current_level_index = 0
levels = os.listdir(TESTS_DIR)

level_decrease_button = PolygonButton([(500, 510), (500, 570), (450, 540)])
level_increase_button = PolygonButton([(780, 510), (780, 570), (830, 540)])

current_angle = math.pi / 2

LOAD_COMPLETE_EVENT = pygame.USEREVENT + 1

game_state = None
initial_game_state = None
stone_weight = None
stones = None
pos_of_ares = None
all_steps = None
current_algorithm_index = 0
algorithms = ['BFS', 'DFS', 'UCS', 'A*']
steps = None

loading = False

starting = True

return_button = PolygonButton([(20, 20), (20, 80), (60, 80), (60, 20)])

wall = pygame.image.load(os.path.join(IMAGES_DIR, "wall.png"))
ares_back = pygame.image.load(os.path.join(IMAGES_DIR, "ares_back.png"))
ares_front = pygame.image.load(os.path.join(IMAGES_DIR, "ares_front.png"))
ares_left = pygame.image.load(os.path.join(IMAGES_DIR, "ares_left.png"))
ares_right = pygame.image.load(os.path.join(IMAGES_DIR, "ares_right.png"))
stone = pygame.image.load(os.path.join(IMAGES_DIR, "stone.png"))
stone_on_switch = pygame.image.load(os.path.join(IMAGES_DIR, "stone_on_switch.png"))
switch = pygame.image.load(os.path.join(IMAGES_DIR, "switch.png"))

tile_size = None
fit_wall = None
fit_ares_back = None
fit_ares_front = None
fit_ares_left = None
fit_ares_right = None
fit_stone = None
fit_stone_on_switch = None
fit_switch = None

previous_move = None

back_button = PolygonButton([(780, 40), (835, 40), (835, 80), (780, 80)], BACKGROUND_COLOR)
algorithm_left_button = PolygonButton([(90, 250), (90, 310), (50, 280)])
algorithm_right_button = PolygonButton([(290, 250), (290, 310), (330, 280)])
play_pause_button = PolygonButton([(860, 30), (900, 30), (900, 90), (860, 90)], BACKGROUND_COLOR)
next_button = PolygonButton([(925, 40), (980, 40), (980, 80), (925, 80)], BACKGROUND_COLOR)
reset_button = PolygonButton([(1210, 30), (1270, 30), (1270, 90), (1210, 90)])

previous_states = None
current_step_index = None

playing = False

current_weight = None

gaming = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if starting and not loading:
                if start_button.is_selected(event.pos):
                    threading.Thread(target=load).start()
                    loading = True
                elif level_decrease_button.is_selected(event.pos):
                    current_level_index = (current_level_index - 1 + len(levels)) % len(levels)
                elif level_increase_button.is_selected(event.pos):
                    current_level_index = (current_level_index + 1) % len(levels)
            elif gaming:
                if back_button.is_selected(event.pos) and not playing:
                    back_game_state(previous_states)
                elif play_pause_button.is_selected(event.pos):
                    playing = not playing
                elif next_button.is_selected(event.pos) and not playing:
                    next_game_state(game_state, previous_states)
                elif reset_button.is_selected(event.pos):
                    reset()
                elif return_button.is_selected(event.pos):
                    if playing:
                        playing = False
                    gaming = False
                    starting = True
                elif algorithm_left_button.is_selected(event.pos):
                    current_algorithm_index = (current_algorithm_index - 1 + len(algorithms)) % len(algorithms)
                    steps = all_steps[algorithms[current_algorithm_index]]
                    reset()
                elif algorithm_right_button.is_selected(event.pos):
                    current_algorithm_index = (current_algorithm_index + 1) % len(algorithms)
                    steps = all_steps[algorithms[current_algorithm_index]]
                    reset()
        elif event.type == LOAD_COMPLETE_EVENT:
            current_angle = math.pi / 2
            steps = all_steps[algorithms[current_algorithm_index]]
            if starting and loading:
                loading = False
                starting = False
                gaming = True

    if starting:
        draw_start_screen(screen)

        if loading:
            draw_loading(screen)
            current_angle = current_angle - math.pi / 6
            if (current_angle <= 0):
                current_angle += 2 * math.pi

    elif gaming:
        if playing:
            pygame.time.delay(200)
            next_game_state(game_state, previous_states)
        draw_game_screen(screen)

    pygame.display.flip()

    pygame.time.Clock().tick(FPS)

pygame.quit()