import heapq
import random
import numpy as np
import pygame
import sys
import time

# الألوان المستخدمة في اللعبة
WOOD_BACKGROUND = (139, 69, 19)  # لون الخشب للخلفية
WOOD_WALL = (101, 67, 33)  # لون الجدران الخشبية
WHITE = (255, 255, 255)  # المسارات
PLAYER_COLOR = (0, 255, 0)  # لون اللاعب
AI_COLOR = (0, 0, 255)  # لون الذكاء الاصطناعي
START_COLOR = (255, 0, 0)  # لون البداية
END_COLOR = (0, 0, 255)  # لون النهاية
AI_PATH_COLOR = (255, 215, 0)  # مسار الذكاء الاصطناعي باللون الذهبي
BUTTON_COLOR = (200, 200, 200)  # لون الأزرار
BUTTON_HOVER = (180, 180, 180)  # لون عند التحويم على الزر
TEXT_COLOR = (0, 0, 0)  # لون النصوص


# توليد المتاهة مع ضمان وجود مسار
def generate_maze(width, height):
    maze = np.ones((height, width), dtype=int)

    def carve_path(x, y):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2
            if 0 < nx < width - 1 and 0 < ny < height - 1 and maze[ny][nx] == 1:
                maze[ny][nx] = 0
                maze[y + dy][x + dx] = 0
                carve_path(nx, ny)

    maze[1][1] = 0
    carve_path(1, 1)

    return maze


# عرض المتاهة
def display_maze(maze, player_pos, ai_pos, screen, block_size, start, end, ai_path=None):
    for y in range(len(maze)):
        for x in range(len(maze[0])):
            if maze[y][x] == 1:
                color = WOOD_WALL
            else:
                color = WHITE

            pygame.draw.rect(screen, color, (x * block_size, y * block_size, block_size, block_size))

    # لون اللاعب والذكاء الاصطناعي
    pygame.draw.rect(screen, PLAYER_COLOR,
                     (player_pos[1] * block_size, player_pos[0] * block_size, block_size, block_size))
    pygame.draw.rect(screen, AI_COLOR, (ai_pos[1] * block_size, ai_pos[0] * block_size, block_size, block_size))

    # عرض المسار الخاص بالذكاء الاصطناعي إن وجد
    if ai_path:
        for p in ai_path:
            pygame.draw.rect(screen, AI_PATH_COLOR, (p[1] * block_size, p[0] * block_size, block_size, block_size))

    # تمييز البداية والنهاية
    pygame.draw.rect(screen, START_COLOR, (start[1] * block_size, start[0] * block_size, block_size, block_size))
    pygame.draw.rect(screen, END_COLOR, (end[1] * block_size, end[0] * block_size, block_size, block_size))


# حركة اللاعب
def move_player(maze, player_pos, direction):
    new_pos = {
        'up': (player_pos[0] - 1, player_pos[1]),
        'down': (player_pos[0] + 1, player_pos[1]),
        'left': (player_pos[0], player_pos[1] - 1),
        'right': (player_pos[0], player_pos[1] + 1)
    }.get(direction, player_pos)

    if 0 <= new_pos[0] < len(maze) and 0 <= new_pos[1] < len(maze[0]) and maze[new_pos[0]][new_pos[1]] == 0:
        return new_pos
    return player_pos


# عرض الأزرار للتحكم
def display_controls(screen):
    font = pygame.font.SysFont(None, 36)

    x_offset = 700  # تغيير موقع الأزرار لليمين أكثر

    up_button = pygame.Rect(x_offset, 50, 50, 50)
    down_button = pygame.Rect(x_offset, 150, 50, 50)
    left_button = pygame.Rect(x_offset - 50, 100, 50, 50)
    right_button = pygame.Rect(x_offset + 50, 100, 50, 50)
    ai_button = pygame.Rect(x_offset, 250, 150, 50)  # زر الذكاء الاصطناعي

    # تغيير ألوان الأزرار
    pygame.draw.rect(screen, (100, 100, 255), up_button)
    pygame.draw.rect(screen, (100, 100, 255), down_button)
    pygame.draw.rect(screen, (100, 100, 255), left_button)
    pygame.draw.rect(screen, (100, 100, 255), right_button)
    pygame.draw.rect(screen, (0, 255, 0), ai_button)

    # عرض الرموز على الأزرار
    up_text = font.render("W", True, (0, 0, 0))
    down_text = font.render("S", True, (0, 0, 0))
    left_text = font.render("A", True, (0, 0, 0))
    right_text = font.render("D", True, (0, 0, 0))
    ai_text = font.render("AI Solve", True, (0, 0, 0))

    screen.blit(up_text, (x_offset + 10, 55))
    screen.blit(down_text, (x_offset + 10, 155))
    screen.blit(left_text, (x_offset - 40, 105))
    screen.blit(right_text, (x_offset + 60, 105))
    screen.blit(ai_text, (x_offset + 30, 255))

    return up_button, down_button, left_button, right_button, ai_button


# زر إعادة التشغيل
def display_restart_button(screen, width, height, block_size):
    font = pygame.font.SysFont(None, 48)  # زيادة حجم الخط

    # تحديد موقع زر إعادة التشغيل أسفل زر AI Solve

    restart_button = pygame.Rect(10, height * block_size + 10, 200, 50)  # تعديل الموقع ليكون أسفل بشكل واضح

    # تغيير اللون عندما يكون الماوس فوق الزر
    mouse_pos = pygame.mouse.get_pos()
    if restart_button.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER, restart_button)  # تغيير اللون عند التحويم
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, restart_button)

    # عرض النص داخل الزر

    text = font.render("Restart", True, TEXT_COLOR)
    screen.blit(text, (20, height * block_size + 15))  # توسيط النص بشكل أفضل


# خوارزمية A* لحل المتاهة
def a_star(maze, start, end):
    start_time = time.time()  # وقت البداية
    def heuristic(a, b):
        # Manhattan distance
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Priority queue using heapq
    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == end:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                end_time = time.time()  # وقت النهاية
                print(f"زمن تنفيذ الذكاء الاصطناعي: {end_time - start_time:.4f} ثانية")  # طباعة الزمن
                current = came_from[current]

            return path[::-1]
            open_set.remove(current)

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            neighbor = (current[0] + dx, current[1] + dy)

            if 0 <= neighbor[0] < len(maze) and 0 <= neighbor[1] < len(maze[0]) and maze[neighbor[0]][neighbor[1]] == 0:
                tentative_g = g_score[current] + 1

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None  # No path found


# تنفيذ اللعبة
def main():
    width, height = 45, 45
    block_size = 13
    maze = generate_maze(width, height)

    start = (1, 1)
    end = (height - 2, width - 2)
    player_pos = start
    ai_pos = start



    pygame.init()
    screen = pygame.display.set_mode((width * block_size + 300, height * block_size + 100))  # زيادة العرض قليلاً
    pygame.display.set_caption("Maze Game")
    clock = pygame.time.Clock()

    ai_path = None

    while True:
        screen.fill((255, 255, 255))

        display_maze(maze, player_pos, ai_pos, screen, block_size, start, end, ai_path)

        up_button, down_button, left_button, right_button, ai_button = display_controls(screen)
        display_restart_button(screen, width, height, block_size)  # إضافة زر إعادة التشغيل أسفل زر AI Solve

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if up_button.collidepoint(mouse_pos):
                    player_pos = move_player(maze, player_pos, 'up')
                elif down_button.collidepoint(mouse_pos):
                    player_pos = move_player(maze, player_pos, 'down')
                elif left_button.collidepoint(mouse_pos):
                    player_pos = move_player(maze, player_pos, 'left')
                elif right_button.collidepoint(mouse_pos):
                    player_pos = move_player(maze, player_pos, 'right')
                elif ai_button.collidepoint(mouse_pos):
                    ai_path = a_star(maze, ai_pos, end)



                # إعادة تشغيل اللعبة عند الضغط على الزر
                restart_button = pygame.Rect(10, height * block_size + 10, 200, 50)  # تعديل المكان هنا
                if restart_button.collidepoint(mouse_pos):
                    maze = generate_maze(width, height)
                    player_pos = start
                    ai_pos = start
                    ai_path = None  # مسح مسار الذكاء الاصطناعي


        pygame.display.flip()
        clock.tick(10)


if __name__ == "__main__":
    main()
