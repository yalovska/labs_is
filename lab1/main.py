import pygame
import random
import math

# --- Константи ---
SCREEN_WIDTH = 606
SCREEN_HEIGHT = 606
PACMAN_SPEED = 20
GHOST_BASE_SPEED = 18

# --- Кольори ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Глобальна змінна для рівня складності
DIFFICULTY_LEVEL = 1

# Завантаження іконки
try:
    PacmanIcon = pygame.image.load('images/pacman.png')
    pygame.display.set_icon(PacmanIcon)
except pygame.error:
    print("Не вдалося завантажити іконку 'images/pacman.png', використовується стандартна")


# --- Класи ---
class Wall(pygame.sprite.Sprite):
    """Клас для створення стін лабіринту"""

    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x


class Block(pygame.sprite.Sprite):
    """Клас для точок, які збирає Пакмен"""

    def __init__(self, color, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        pygame.draw.ellipse(self.image, color, [0, 0, width, height])
        self.rect = self.image.get_rect()


class Player(pygame.sprite.Sprite):
    """Базовий клас для рухомих об'єктів (Пакмен та Привиди)"""

    def __init__(self, x, y, filename):
        super().__init__()
        try:
            self.image = pygame.image.load(filename).convert_alpha()
        except pygame.error:
            self.image = pygame.Surface([20, 20])
            self.image.fill(YELLOW)
            print(f"Попередження: Не знайдено файл {filename}. Використовується жовтий квадрат.")

        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x
        self.change_x = 0
        self.change_y = 0

    def set_speed(self, x, y):
        self.change_x = x
        self.change_y = y

    def update(self, walls, gate=None):
        old_x = self.rect.left
        self.rect.left += self.change_x
        if pygame.sprite.spritecollide(self, walls, False):
            self.rect.left = old_x

        old_y = self.rect.top
        self.rect.top += self.change_y
        if pygame.sprite.spritecollide(self, walls, False):
            self.rect.top = old_y

        if gate and pygame.sprite.spritecollide(self, gate, False):
            self.rect.left = old_x
            self.rect.top = old_y


class Ghost(Player):
    """Клас, що описує поведінку привидів"""

    def __init__(self, x, y, filename, ghost_type, speed):
        super().__init__(x, y, filename)
        self.ghost_type = ghost_type
        self.speed = speed
        self.last_seen_pacman_pos = None
        self.is_stuck_counter = 0
        self.last_position = (x, y)
        self.current_direction = (0, 0)
        self.patrol_points = self._get_patrol_route()
        self.patrol_index = 0

    def _get_patrol_route(self):
        """Визначає маршрут патрулювання для кожного типу привида"""
        if self.ghost_type == "blinky":
            return [(50, 50), (250, 50), (500, 50), (500, 250)]
        elif self.ghost_type == "pinky":
            return [(50, 50), (50, 250), (50, 500), (250, 500)]
        elif self.ghost_type == "inky":
            return [(550, 550), (300, 550), (50, 550), (50, 300)]
        else:
            return [(550, 550), (550, 300), (550, 50), (300, 50)]

    def _get_available_directions(self, walls):
        """Повертає список доступних напрямків з урахуванням швидкості"""
        possible_moves = [(0, -self.speed), (0, self.speed), (-self.speed, 0), (self.speed, 0)]
        available = []
        for dx, dy in possible_moves:
            test_rect = self.rect.move(dx, dy)
            if not any(wall.rect.colliderect(test_rect) for wall in walls):
                available.append((dx, dy))
        return available

    def _has_line_of_sight(self, target_pos, walls):
        start_pos = self.rect.center
        for i in range(0, 101, 5):
            t = i / 100
            check_x = int(start_pos[0] * (1 - t) + target_pos[0] * t)
            check_y = int(start_pos[1] * (1 - t) + target_pos[1] * t)
            for wall in walls:
                if wall.rect.collidepoint(check_x, check_y):
                    return False
        return True

    @staticmethod
    def _calculate_distance(pos1, pos2):
        return math.hypot(pos1[0] - pos2[0], pos1[1] - pos2[1])

    def _move_towards_target(self, target, walls):
        available = self._get_available_directions(walls)
        if not available: return (0, 0)
        if len(available) > 1 and (-self.current_direction[0], -self.current_direction[1]) in available:
            available.remove((-self.current_direction[0], -self.current_direction[1]))
        best_move = min(available, key=lambda move: self._calculate_distance(
            (self.rect.x + move[0], self.rect.y + move[1]), target))
        return best_move

    def _patrol(self, walls):
        target_point = self.patrol_points[self.patrol_index]
        if self._calculate_distance(self.rect.center, target_point) < self.speed:
            self.patrol_index = (self.patrol_index + 1) % len(self.patrol_points)
        return self._move_towards_target(target_point, walls)

    def update_behavior(self, pacman, walls, other_ghosts, mode):
        if mode == "scatter":
            # У режимі розосередження привиди просто рухаються до свого першого патрульного пункту (кута)
            self.current_direction = self._move_towards_target(self.patrol_points[0], walls)
            self.set_speed(*self.current_direction)
            self.update(walls)
            return

        pacman_pos = pacman.rect.center
        if self.rect.topleft == self.last_position:
            self.is_stuck_counter += 1
        else:
            self.is_stuck_counter = 0
        self.last_position = self.rect.topleft

        if self.is_stuck_counter > 5:
            available = self._get_available_directions(walls)
            if available: self.current_direction = random.choice(available)
            self.is_stuck_counter = 0
        else:
            if self._has_line_of_sight(pacman_pos, walls):
                self.last_seen_pacman_pos = pacman_pos

            if DIFFICULTY_LEVEL == 1:
                self.current_direction = self._level1_behavior(pacman, walls)
            elif DIFFICULTY_LEVEL == 2:
                self.current_direction = self._level2_behavior(pacman, walls, other_ghosts)
            else:
                self.current_direction = self._level3_behavior(pacman, walls, other_ghosts)

        self.set_speed(*self.current_direction)
        self.update(walls)

    def _level1_behavior(self, pacman, walls):
        if not self.last_seen_pacman_pos: return self._patrol(walls)
        if self.ghost_type == "blinky":
            return self._move_towards_target(self.last_seen_pacman_pos, walls)
        elif self.ghost_type == "pinky":
            return self._patrol(walls)
        elif self.ghost_type == "inky":
            return self._move_towards_target(self.last_seen_pacman_pos, walls) if self._has_line_of_sight(
                pacman.rect.center, walls) else self._patrol(walls)
        else:
            if random.random() < 0.6:
                available = self._get_available_directions(walls)
                return random.choice(available) if available else (0, 0)
            return self._move_towards_target(self.last_seen_pacman_pos, walls)

    def _level2_behavior(self, pacman, walls, other_ghosts):
        if not self.last_seen_pacman_pos: return self._patrol(walls)
        pacman_pos = pacman.rect.center
        if self.ghost_type == "blinky":
            predicted_pos = (pacman_pos[0] + pacman.change_x * 2, pacman_pos[1] + pacman.change_y * 2)
            return self._move_towards_target(predicted_pos, walls)
        elif self.ghost_type == "pinky":
            target_pos = (pacman_pos[0] + pacman.change_x * 4, pacman_pos[1] + pacman.change_y * 4)
            return self._move_towards_target(target_pos, walls)
        elif self.ghost_type == "inky":
            blinky_pos = next((g.rect.center for g in other_ghosts if g.ghost_type == "blinky"), pacman_pos)
            target_x = 2 * pacman_pos[0] - blinky_pos[0]
            target_y = 2 * pacman_pos[1] - blinky_pos[1]
            return self._move_towards_target((target_x, target_y), walls)
        else:
            if self._calculate_distance(self.rect.center, pacman_pos) < 150:
                return self._move_towards_target(self.patrol_points[0], walls)
            return self._move_towards_target(self.last_seen_pacman_pos, walls)

    def _level3_behavior(self, pacman, walls, other_ghosts):
        if not self.last_seen_pacman_pos: return self._patrol(walls)
        pacman_pos = pacman.rect.center
        if self.ghost_type == "blinky":
            return self._move_towards_target(self.last_seen_pacman_pos, walls)
        elif self.ghost_type == "pinky":
            target_x = pacman_pos[0] - pacman.change_y * 3
            target_y = pacman_pos[1] + pacman.change_x * 3
            return self._move_towards_target((target_x, target_y), walls)
        elif self.ghost_type == "inky":
            blinky = next((g for g in other_ghosts if g.ghost_type == "blinky"), None)
            if blinky:
                target_pos = ((pacman_pos[0] + blinky.rect.centerx) // 2, (pacman_pos[1] + blinky.rect.centery) // 2)
                return self._move_towards_target(target_pos, walls)
            return self._move_towards_target(self.last_seen_pacman_pos, walls)
        else:
            if self._calculate_distance(self.rect.center, pacman_pos) > 200:
                return self._move_towards_target((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), walls)
            return self._move_towards_target(self.last_seen_pacman_pos, walls)


# --- Функції налаштування гри ---

def setupRoomOne(all_sprites_list):
    wall_list = pygame.sprite.RenderPlain()
    walls_coords = [
        [0, 0, 6, 600], [0, 0, 600, 6], [0, 600, 606, 6], [600, 0, 6, 606], [300, 0, 6, 66],
        [60, 60, 186, 6], [360, 60, 186, 6], [60, 120, 66, 6], [60, 120, 6, 126], [180, 120, 246, 6],
        [300, 120, 6, 66], [480, 120, 66, 6], [540, 120, 6, 126], [120, 180, 126, 6],
        [120, 180, 6, 126], [360, 180, 126, 6], [480, 180, 6, 126], [180, 240, 6, 126],
        [180, 360, 246, 6], [420, 240, 6, 126], [240, 240, 42, 6], [324, 240, 42, 6],
        [240, 240, 6, 66], [240, 300, 126, 6], [360, 240, 6, 66], [0, 300, 66, 6],
        [540, 300, 66, 6], [60, 360, 66, 6], [60, 360, 6, 186], [480, 360, 66, 6],
        [540, 360, 6, 186], [120, 420, 366, 6], [120, 420, 6, 66], [480, 420, 6, 66],
        [180, 480, 246, 6], [300, 480, 6, 66], [120, 540, 126, 6], [360, 540, 126, 6]
    ]
    for item in walls_coords:
        wall = Wall(item[0], item[1], item[2], item[3], BLUE)
        wall_list.add(wall)
        all_sprites_list.add(wall)
    return wall_list


def setupGate(all_sprites_list):
    gate = pygame.sprite.RenderPlain()
    gate.add(Wall(282, 242, 42, 2, WHITE))
    all_sprites_list.add(gate)
    return gate


# --- Головні функції гри ---

def select_difficulty(screen, font, small_font, clock):
    """Екран вибору складності"""
    global DIFFICULTY_LEVEL

    level_descriptions = {
        1: ["Рівень 1: Легкий", "Привиди діють незалежно"],
        2: ["Рівень 2: Середній", "Просунуті індивідуальні тактики"],
        3: ["Рівень 3: Складний", "Емерджентна командна робота"]
    }

    selected_level = 1
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_level = max(1, selected_level - 1)
                elif event.key == pygame.K_DOWN:
                    selected_level = min(3, selected_level + 1)
                elif event.key == pygame.K_RETURN:
                    DIFFICULTY_LEVEL = selected_level
                    return True
                elif event.key == pygame.K_ESCAPE:
                    return False

        screen.fill(BLACK)
        title = font.render("ОБЕРІТЬ РІВЕНЬ СКЛАДНОСТІ", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, 50))
        for level, desc in level_descriptions.items():
            color = YELLOW if level == selected_level else WHITE
            level_text = font.render(desc[0], True, color)
            screen.blit(level_text, (100, 150 + (level - 1) * 120))
            for i, line in enumerate(desc[1:]):
                line_text = small_font.render(line, True, WHITE)
                screen.blit(line_text, (120, 180 + i * 20 + (level - 1) * 120))
        hint = small_font.render("Використовуйте стрілки, ENTER для вибору, ESC для виходу", True, GREEN)
        screen.blit(hint, (SCREEN_WIDTH / 2 - hint.get_width() / 2, 550))
        pygame.display.flip()
        clock.tick(10)


def game_loop(screen, font, small_font, clock):
    """Основний ігровий цикл"""
    all_sprites = pygame.sprite.Group()
    block_list = pygame.sprite.Group()
    monster_list = pygame.sprite.Group()

    wall_list = setupRoomOne(all_sprites)
    gate = setupGate(all_sprites)

    pacman = Player(303 - 16, (7 * 60) + 19, "images/pacman.png")
    all_sprites.add(pacman)

    ghost_speed = GHOST_BASE_SPEED - 2 if DIFFICULTY_LEVEL == 1 else GHOST_BASE_SPEED

    ghost_data = [
        {"file": "images/Blinky.png", "type": "blinky", "pos": (60, 60)},
        {"file": "images/Pinky.png", "type": "pinky", "pos": (520, 60)},
        {"file": "images/Inky.png", "type": "inky", "pos": (60, 520)},
        {"file": "images/Clyde.png", "type": "clyde", "pos": (520, 520)}
    ]
    ghosts = [Ghost(d["pos"][0], d["pos"][1], d["file"], d["type"], ghost_speed) for d in ghost_data]
    for ghost in ghosts:
        all_sprites.add(ghost)
        monster_list.add(ghost)

    for row in range(19):
        for column in range(19):
            if (row in [7, 8]) and (column in [8, 9, 10]): continue
            block = Block(YELLOW, 4, 4)
            block.rect.x = (30 * column + 6) + 26
            block.rect.y = (30 * row + 6) + 26
            if not pygame.sprite.spritecollide(block, wall_list, False):
                block_list.add(block)
                all_sprites.add(block)

    initial_block_count = len(block_list)
    score = 0

    mode_timer = 0
    current_mode = "chase"
    CHASE_TIME = 200  # 20 секунд при 10 FPS
    SCATTER_TIME = 70  # 7 секунд при 10 FPS

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit", 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    pacman.set_speed(-PACMAN_SPEED, 0)
                elif event.key == pygame.K_RIGHT:
                    pacman.set_speed(PACMAN_SPEED, 0)
                elif event.key == pygame.K_UP:
                    pacman.set_speed(0, -PACMAN_SPEED)
                elif event.key == pygame.K_DOWN:
                    pacman.set_speed(0, PACMAN_SPEED)

        mode_timer += 1
        if current_mode == "chase" and mode_timer > CHASE_TIME:
            current_mode = "scatter"
            mode_timer = 0
        elif current_mode == "scatter" and mode_timer > SCATTER_TIME:
            current_mode = "chase"
            mode_timer = 0

        pacman.update(wall_list, gate)

        for ghost in ghosts:
            other_ghosts = [g for g in ghosts if g != ghost]
            ghost.update_behavior(pacman, wall_list, other_ghosts, current_mode)

        blocks_hit = pygame.sprite.spritecollide(pacman, block_list, True)
        score += len(blocks_hit)

        screen.fill(BLACK)
        all_sprites.draw(screen)

        score_text = font.render(f"Рахунок: {score}/{initial_block_count}", True, WHITE)
        mode_text_str = "Погоня!" if current_mode == 'chase' else "Перепочинок!"
        mode_text_color = RED if current_mode == 'chase' else GREEN
        mode_text = font.render(mode_text_str, True, mode_text_color)

        screen.blit(score_text, [10, 10])
        screen.blit(mode_text, [SCREEN_WIDTH - mode_text.get_width() - 10, 10])

        if score == initial_block_count: return "win", score
        if pygame.sprite.spritecollide(pacman, monster_list, False): return "lose", score

        pygame.display.flip()
        clock.tick(10)


def end_screen(screen, font, message, score, clock):
    """Екран завершення гри (перемога/поразка)"""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: return True
                if event.key == pygame.K_ESCAPE: return False

        screen.fill(BLACK)
        msg_text = font.render(message, True, YELLOW)
        score_text = font.render(f"Ваш рахунок: {score}", True, WHITE)
        restart_text = font.render("Натисніть ENTER, щоб грати знову", True, GREEN)
        quit_text = font.render("Натисніть ESC, щоб вийти", True, GREEN)

        screen.blit(msg_text, (SCREEN_WIDTH / 2 - msg_text.get_width() / 2, 200))
        screen.blit(score_text, (SCREEN_WIDTH / 2 - score_text.get_width() / 2, 250))
        screen.blit(restart_text, (SCREEN_WIDTH / 2 - restart_text.get_width() / 2, 350))
        screen.blit(quit_text, (SCREEN_WIDTH / 2 - quit_text.get_width() / 2, 400))

        pygame.display.flip()
        clock.tick(10)


def main():
    """Головна функція, що запускає гру"""
    pygame.init()
    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    pygame.display.set_caption('Pacman: Emergent Ghost AI')

    try:
        font = pygame.font.Font("freesansbold.ttf", 24)
        small_font = pygame.font.Font("freesansbold.ttf", 18)
    except FileNotFoundError:
        font = pygame.font.SysFont('Arial', 24)
        small_font = pygame.font.SysFont('Arial', 18)

    clock = pygame.time.Clock()

    while True:
        if not select_difficulty(screen, font, small_font, clock): break
        game_status, score = game_loop(screen, font, small_font, clock)
        if game_status == "quit": break
        message = "Перемога!" if game_status == "win" else "Гру завершено!"
        if not end_screen(screen, font, message, score, clock): break

    pygame.quit()


if __name__ == "__main__":
    main()
