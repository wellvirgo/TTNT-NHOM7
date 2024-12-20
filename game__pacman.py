import pygame
import heapq
import random

def show_popup(screen, message):
    font = pygame.font.Font(None, 50)
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    screen.blit(text, text_rect)
    pygame.display.flip()

    pygame.time.wait(3000)  # Chờ 3 giây trước khi đóng game


pygame.init()

# Cài đặt màn hình hiển thị
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 20, 20
CELL_SIZE = WIDTH // COLS

# Màu cho các thành phần trong game
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Hướng di chuyển
directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

# Hàm heuristic cho A*
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Hàm tạo thức ăn
def generate_food(grid, num_food=30):
    food = []
    empty_cells = [(row, col) for row in range(ROWS) for col in range(COLS) if grid[row][col] == 0]
    random.shuffle(empty_cells)

    for candidate in empty_cells:
        if len(food) >= num_food:
            break
        if all(heuristic(candidate, existing) > 3 for existing in food):
            food.append(candidate)

    return food

# Thuật toán A*
def a_star(grid, start, goal):
    queue = []
    heapq.heappush(queue, (0, start))
    came_from = {}
    cost = {start: 0}

    while queue:
        _, current = heapq.heappop(queue)

        if current == goal:
            path = []
            while current != start:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < ROWS and 0 <= neighbor[1] < COLS and not grid[neighbor[0]][neighbor[1]]:
                new_cost = cost[current] + 1
                if neighbor not in cost or new_cost < cost[neighbor]:
                    cost[neighbor] = new_cost
                    priority = new_cost + heuristic(goal, neighbor)
                    heapq.heappush(queue, (priority, neighbor))
                    came_from[neighbor] = current

    return []

# Hàm tìm vị trí an toàn cho Pacman
def find_safe_position(grid, pacman, ghosts, safety_threshold=3):
    safe_positions = []

    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if grid[row][col] == 0:
                min_ghost_distance = min(
                    heuristic((row, col), (ghost.x, ghost.y)) 
                    for ghost in ghosts
                )

                if min_ghost_distance > safety_threshold:
                    safe_positions.append((row, col))

    if safe_positions:
        safe_positions.sort(key=lambda pos: heuristic(pos, (pacman.x, pacman.y)))
        return safe_positions[0]

    return (pacman.x, pacman.y)

# Lớp pacman
class Pacman:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.score = 0

    def move(self, path):
        if path:
            self.x, self.y = path[0]

    def add_score(self, points):
        self.score += points

    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (self.y * CELL_SIZE + CELL_SIZE // 2, self.x * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)

# Lớp ghost
class Ghost:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.steps = 0

    def move(self, grid, pacman, other_ghosts):
        if self.steps % 2 == 0:
            path = a_star(grid, (self.x, self.y), (pacman.x, pacman.y))
            if path:
                next_x, next_y = path[0]

                # Kiểm tra sự va chạm với các ghost khác
                if not any(ghost.x == next_x and ghost.y == next_y for ghost in other_ghosts):
                    self.x, self.y = next_x, next_y
        self.steps += 1

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (self.y * CELL_SIZE + CELL_SIZE // 2, self.x * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pacman AI")
    clock = pygame.time.Clock()

    # Tạo bản đồ cố định
    grid = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
        [1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
        [1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]

    # Tạo thức ăn
    food = generate_food(grid, num_food=30)

    # Khởi tạo pacman và ghost
    pacman = Pacman(2, 2)
    ghosts = [Ghost(ROWS // 2, COLS // 2)]

    running = True
    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Vẽ bản đồ
        for row in range(ROWS):
            for col in range(COLS):
                if grid[row][col] == 1:
                    pygame.draw.rect(screen, BLUE, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Vẽ thức ăn
        for fx, fy in food:
            pygame.draw.circle(screen, GREEN, (fy * CELL_SIZE + CELL_SIZE // 2, fx * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 5)

        # Cập nhật lại pacman
        if food:
            closest_food = min(food, key=lambda f: heuristic((pacman.x, pacman.y), f))

            dangerous_ghosts = [
                ghost for ghost in ghosts 
                if heuristic((pacman.x, pacman.y), (ghost.x, ghost.y)) <= 3
            ]

            if dangerous_ghosts:
                safe_position = find_safe_position(grid, pacman, dangerous_ghosts)
                path = a_star(grid, (pacman.x, pacman.y), safe_position)
            else:
                path = a_star(grid, (pacman.x, pacman.y), closest_food)

            pacman.move(path[:1])

        pacman.draw(screen)

        # Cập nhật các ghost
        for i, ghost in enumerate(ghosts):
            ghost.move(grid, pacman, ghosts[:i] + ghosts[i+1:])
            ghost.draw(screen)

            if (pacman.x, pacman.y) == (ghost.x, ghost.y):
                show_popup(screen, f"Game Over! Your score: {pacman.score}")
                running = False
                return

        # Pacman thực hiện ăn thức ăn
        if (pacman.x, pacman.y) in food:
            food.remove((pacman.x, pacman.y))
            pacman.add_score(10)

        if not food:
            show_popup(screen, f"You Win! Your score: {pacman.score}")
            running = False

        pygame.display.flip()
        clock.tick(8)

    pygame.quit()

if __name__ == "__main__":
    main()
