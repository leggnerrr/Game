import pygame
import sys
import os
import random

pygame.init()

# --- Setup ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Yakumo's Quest")
clock = pygame.time.Clock()
FPS = 60

# --- Paths ---
SPRITES = "assets/sprites"
YAKUMO_SPRITES = os.path.join(SPRITES, "yakumo")
BG = "assets/backgrounds"
UI = "assets/ui"

def load_image(file, size=None):
    img = pygame.image.load(file).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    return img

# --- Load Assets ---
area_names = [
    "village.png", "forest.png", "swamp.png",
    "cave_entrance.png", "field.png", "ruins.png",
    "mountain.png", "river.png", "desert.png"
]
backgrounds = [load_image(os.path.join(BG, name)) for name in area_names]

yakumo_imgs = {
    "down": load_image(os.path.join(YAKUMO_SPRITES, "down_0.png"), (48, 48)),
    "up": load_image(os.path.join(YAKUMO_SPRITES, "up_0.png"), (48, 48)),
    "left": load_image(os.path.join(YAKUMO_SPRITES, "left_0.png"), (48, 48)),
    "right": load_image(os.path.join(YAKUMO_SPRITES, "right_0.png"), (48, 48))
}
direction = "down"

haurto_img = load_image(f"{SPRITES}/haurto.png", (48, 48))
sword_img = load_image(f"{SPRITES}/sword.png", (32, 32))
swing_img = load_image(f"{SPRITES}/sword_swing.png", (64, 64))
enemy_img = load_image(f"{SPRITES}/enemy1.png", (48, 48))
heart_full = load_image(f"{UI}/heart_full.png", (24, 24))
heart_empty = load_image(f"{UI}/heart_empty.png", (24, 24))
rock_img = load_image(f"{SPRITES}/rock.png", (64, 64))  # Load rock image

# --- Rects and State ---
def reset_positions():
    global yakumo_rect, haurto_rect, sword_rect, swing_rect
    yakumo_rect = yakumo_imgs["down"].get_rect(center=(100, 500))
    haurto_rect = haurto_img.get_rect(center=(250, 300))
    sword_rect = sword_img.get_rect(center=(600, 300))
    swing_rect = swing_img.get_rect(center=(-100, -100))

def spawn_enemies(area):
    if area == [0, 0]:  # No enemies in village
        return []
    enemies = []
    if area != boss_location:
        num = random.randint(2, 4)
        for _ in range(num):
            x = random.randint(100, 700)
            y = random.randint(100, 500)
            enemy = {
                "rect": enemy_img.get_rect(center=(x, y)),
                "health": 2,
                "max_health": 2,
                "speed": 1.0,
                "damage": 1,
                "alive": True
            }
            enemies.append(enemy)
    return enemies

# --- Map State ---
current_area = [0, 0]
boss_location = [random.randint(0, 2), random.randint(0, 2)]
visited_areas = {}

# --- Obstacles ---
# You can add more obstacles per area by extending this dictionary.
# Format: (x, y) = list of dicts with 'rect' and 'img'.
obstacles_by_area = {
    (0, 0): [  # Village
        {"name": "rock", "rect": pygame.Rect(400, 300, 64, 64), "img": rock_img},
        # Add more objects like houses or trees by copying the line above
    ],
    # Example for another area:
    # (1, 0): [
    #     {"name": "rock", "rect": pygame.Rect(300, 300, 64, 64), "img": rock_img},
    # ]
}

# --- Game State ---
font = pygame.font.SysFont("consolas", 24)

def reset_game():
    global dialogue_index, show_dialogue, has_sword, is_attacking, attack_cooldown
    global yakumo_health, max_health, damage_cooldown, enemies, enemy_kill_count, heart_drops
    global direction, visited_areas, current_area, boss_location, talked_to_haurto

    reset_positions()
    show_dialogue = False
    dialogue_index = 0
    has_sword = False
    is_attacking = False
    attack_cooldown = 0
    yakumo_health = 3
    max_health = 3
    damage_cooldown = 0
    enemies = []
    enemy_kill_count = 0
    heart_drops = []
    direction = "down"
    current_area = [0, 0]
    boss_location = [random.randint(0, 2), random.randint(0, 2)]
    visited_areas.clear()
    visited_areas[tuple(current_area)] = spawn_enemies(current_area)
    talked_to_haurto = False

reset_game()

# --- Dialogue ---
dialogue_lines = [
    "Haurto: Yakumo... your father has been taken.",
    "Haurto: Take the sword from the chest. You'll need it.",
    "Haurto: Go now. The Mountain Walker awaits..."
]

def draw_dialogue_box():
    pygame.draw.rect(screen, (0, 0, 0), (50, 450, 700, 120))
    pygame.draw.rect(screen, (255, 255, 255), (50, 450, 700, 120), 3)
    line = dialogue_lines[dialogue_index]
    text = font.render(line, True, (255, 255, 255))
    screen.blit(text, (60, 470))

def draw_heart_bar():
    for i in range(max_health):
        x = 20 + i * 30
        screen.blit(heart_full if i < yakumo_health else heart_empty, (x, 20))

def draw_enemy_health(enemy):
    ratio = enemy["health"] / enemy["max_health"]
    bar_w = enemy["rect"].width
    pygame.draw.rect(screen, (255, 0, 0), (enemy["rect"].x, enemy["rect"].y - 10, bar_w, 5))
    pygame.draw.rect(screen, (0, 255, 0), (enemy["rect"].x, enemy["rect"].y - 10, int(bar_w * ratio), 5))

# --- Main Loop ---
game_state = "start"
running = True
while running:
    dt = clock.tick(FPS)
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if game_state == "start" and event.key == pygame.K_RETURN:
                reset_game()
                game_state = "playing"

            elif game_state == "playing":
                if show_dialogue and event.key == pygame.K_SPACE:
                    dialogue_index += 1
                    if dialogue_index >= len(dialogue_lines):
                        show_dialogue = False

                elif not show_dialogue and has_sword and event.key == pygame.K_SPACE:
                    if attack_cooldown <= 0:
                        is_attacking = True
                        attack_cooldown = 12

                elif not show_dialogue and not has_sword and yakumo_rect.colliderect(sword_rect):
                    if event.key == pygame.K_e:
                        has_sword = True

                elif not show_dialogue and current_area == [0, 0] and yakumo_rect.colliderect(haurto_rect) and not talked_to_haurto:
                    if event.key == pygame.K_e:
                        show_dialogue = True
                        dialogue_index = 0
                        talked_to_haurto = True

    keys = pygame.key.get_pressed()

    if game_state == "start":
        screen.blit(font.render("Yakumo's Quest", True, (255, 255, 0)), (SCREEN_WIDTH//2 - 100, 200))
        screen.blit(font.render("Press ENTER to start", True, (255, 255, 255)), (SCREEN_WIDTH//2 - 140, 300))

    elif game_state == "playing":
        area_index = current_area[1] * 3 + current_area[0]
        screen.blit(backgrounds[area_index], (0, 0))

        # Draw obstacles for the current area
        for obstacle in obstacles_by_area.get(tuple(current_area), []):
            screen.blit(obstacle["img"], obstacle["rect"])

        dx = dy = 0
        speed = 4
        if keys[pygame.K_LEFT]: dx -= speed; direction = "left"
        if keys[pygame.K_RIGHT]: dx += speed; direction = "right"
        if keys[pygame.K_UP]: dy -= speed; direction = "up"
        if keys[pygame.K_DOWN]: dy += speed; direction = "down"
        yakumo_rect.x += dx
        yakumo_rect.y += dy

        # Obstacle collision check
        for obstacle in obstacles_by_area.get(tuple(current_area), []):
            if yakumo_rect.colliderect(obstacle["rect"]):
                yakumo_rect.x -= dx
                yakumo_rect.y -= dy
                break

        # Area transitions
        transitioned = False
        if yakumo_rect.left < 0 and current_area[0] > 0:
            current_area[0] -= 1
            transitioned = True
            yakumo_rect.right = SCREEN_WIDTH
        elif yakumo_rect.right > SCREEN_WIDTH and current_area[0] < 2:
            current_area[0] += 1
            transitioned = True
            yakumo_rect.left = 0
        elif yakumo_rect.top < 0 and current_area[1] > 0:
            current_area[1] -= 1
            transitioned = True
            yakumo_rect.bottom = SCREEN_HEIGHT
        elif yakumo_rect.bottom > SCREEN_HEIGHT and current_area[1] < 2:
            current_area[1] += 1
            transitioned = True
            yakumo_rect.top = 0

        if transitioned:
            pos = tuple(current_area)
            if pos not in visited_areas:
                visited_areas[pos] = spawn_enemies(current_area)
            heart_drops.clear()

        enemies = visited_areas.get(tuple(current_area), [])

        if current_area == [0, 0]:
            screen.blit(haurto_img, haurto_rect)
        screen.blit(yakumo_imgs[direction], yakumo_rect)

        if not has_sword:
            screen.blit(sword_img, sword_rect)

        draw_heart_bar()

        if is_attacking:
            offset = {
                "left": (-48, 0), "right": (48, 0),
                "up": (0, -48), "down": (0, 48)
            }[direction]
            swing_rect.center = (yakumo_rect.centerx + offset[0], yakumo_rect.centery + offset[1])
            is_attacking = False
        else:
            swing_rect.center = (-100, -100)
        screen.blit(swing_img, swing_rect)

        if attack_cooldown > 0:
            attack_cooldown -= 1

        if show_dialogue:
            draw_dialogue_box()
        elif not has_sword and yakumo_rect.colliderect(sword_rect):
            screen.blit(font.render("Press E to take the sword", True, (255, 255, 0)),
                        (sword_rect.x - 30, sword_rect.y - 40))
        elif not talked_to_haurto and yakumo_rect.colliderect(haurto_rect):
            screen.blit(font.render("Press E to talk to Haurto", True, (255, 255, 0)),
                        (haurto_rect.x - 30, haurto_rect.y - 40))

        for enemy in enemies[:]:
            if enemy["alive"]:
                dx = yakumo_rect.centerx - enemy["rect"].centerx
                dy = yakumo_rect.centery - enemy["rect"].centery
                dist = max(1, (dx**2 + dy**2)**0.5)
                if dist < 300:
                    enemy["rect"].x += int(enemy["speed"] * dx / dist)
                    enemy["rect"].y += int(enemy["speed"] * dy / dist)
                screen.blit(enemy_img, enemy["rect"])
                draw_enemy_health(enemy)

                if yakumo_rect.colliderect(enemy["rect"]) and damage_cooldown <= 0:
                    yakumo_health -= enemy["damage"]
                    damage_cooldown = 60
                    if yakumo_health <= 0:
                        game_state = "gameover"

                if swing_rect.colliderect(enemy["rect"]):
                    enemy["health"] -= 1
                    if enemy["health"] <= 0:
                        enemy["alive"] = False
                        enemy_kill_count += 1
                        if enemy_kill_count % 2 == 0:
                            heart_drops.append(enemy_img.get_rect(center=enemy["rect"].center))

        if damage_cooldown > 0:
            damage_cooldown -= 1

        for heart in heart_drops[:]:
            screen.blit(heart_full, heart)
            if yakumo_rect.colliderect(heart):
                max_health += 1
                yakumo_health += 1
                heart_drops.remove(heart)

    pygame.display.update()

pygame.quit()
sys.exit()
