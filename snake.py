import pygame
import psycopg2
import time
import random

# Подключение к базе данных
def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname="snake",
            user="postgres",
            password="Erkin2006",
            host="localhost",
            port="5432"
        )
        print("Соединение с базой данных установлено.")
        return conn
    except psycopg2.Error as e:
        print("Ошибка подключения к базе данных:", e)
        return None

# Создание таблиц
def create_tables(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_scores (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            level INTEGER NOT NULL DEFAULT 1,
            score INTEGER NOT NULL DEFAULT 0
        );
        """)
        conn.commit()
        print("Таблицы успешно созданы.")
    except psycopg2.Error as e:
        print("Ошибка создания таблиц:", e)

# Получение или создание пользователя
def get_or_create_user(conn, username):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s;", (username,))
        user = cursor.fetchone()
        if user:
            return user[0]  # Возвращаем ID пользователя
        cursor.execute("INSERT INTO users (username) VALUES (%s) RETURNING id;", (username,))
        conn.commit()
        return cursor.fetchone()[0]
    except psycopg2.Error as e:
        print("Ошибка при получении или создании пользователя:", e)

# Получение уровня и очков пользователя
def get_user_progress(conn, user_id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT level, score FROM user_scores WHERE user_id = %s ORDER BY id DESC LIMIT 1;", (user_id,))
        progress = cursor.fetchone()
        if progress:
            return progress
        return 1, 0  # Уровень 1, очки 0 по умолчанию
    except psycopg2.Error as e:
        print("Ошибка получения прогресса пользователя:", e)

# Сохранение прогресса пользователя
def save_user_progress(conn, user_id, level, score):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_scores (user_id, level, score) VALUES (%s, %s, %s);", (user_id, level, score))
        conn.commit()
    except psycopg2.Error as e:
        print("Ошибка сохранения прогресса пользователя:", e)

# Инициализация Pygame
pygame.init()

# Константы игры
snake_speed = 5
HEIGHT = 700
WIDTH = 500
segment_size = 20
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
green = pygame.Color(0, 255, 0)
red = pygame.Color(255, 0, 0)
colors = {1: pygame.Color(255, 215, 0),  # Gold for weight 1
          2: pygame.Color(255, 140, 0),  # Dark orange for weight 2
          3: red,    # Red for weight 3
          4: pygame.Color(138, 43, 226), # Purple for weight 4
          5: pygame.Color(75, 0, 130)} 

# Окно игры
game_window = pygame.display.set_mode((HEIGHT, WIDTH))
pygame.display.set_caption('Snake')
fps = pygame.time.Clock()

# Логика игры
def game_loop(conn, user_id, start_level, start_score):
    global snake_speed
    level = start_level
    score = start_score
    snake_position = [100, 50]
    snake_body = [[100, 50], [80, 50], [60, 50]]
    food_lifetime = 6000  # 6 seconds

    def generate_food():
        """Generates a new food item with random weight and timer."""
        pos = [random.randrange(1, (HEIGHT // segment_size)) * segment_size,
               random.randrange(1, (WIDTH // segment_size)) * segment_size]
        weight = random.randint(1, 5)  # Random weight between 1 and 5
        color = colors[weight]         # Get color based on weight
        spawn_time = pygame.time.get_ticks()  # Record spawn time
        return pos, weight, color, spawn_time
# Generate initial food
    fruit_position, fruit_weight, fruit_color, spawn_time = generate_food()
    fruit_spawn = True

    direction = 'RIGHT'
    change_to = direction
    paused = False  # Flag to track pause state

    def show_score_level():
        font = pygame.font.SysFont('times new roman', 20)
        score_surface = font.render(f'Score: {score}  Level: {level}', True, white)
        score_rect = score_surface.get_rect()
        score_rect.midtop = (HEIGHT / 6, 15)
        game_window.blit(score_surface, score_rect)

    def game_over():
        font = pygame.font.SysFont('times new roman', 50)
        game_over_surface = font.render('Your Score: ' + str(score), True, red)
        game_over_rect = game_over_surface.get_rect()
        game_over_rect.midtop = (HEIGHT / 2, WIDTH / 4)
        game_window.blit(game_over_surface, game_over_rect)
        pygame.display.flip()
        time.sleep(2)
        save_user_progress(conn, user_id, level, score)
        pygame.quit()
        quit()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_user_progress(conn, user_id, level, score)
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    change_to = 'UP'
                elif event.key == pygame.K_DOWN:
                    change_to = 'DOWN'
                elif event.key == pygame.K_LEFT:
                    change_to = 'LEFT'
                elif event.key == pygame.K_RIGHT:
                    change_to = 'RIGHT'
                elif event.key == pygame.K_p:  # Pause and save shortcut
                    if paused:
                        paused = False  # Resume game
                    else:
                        paused = True
                        save_user_progress(conn, user_id, level, score)
                        print("Game paused. Progress saved!")

        if paused:
            font = pygame.font.SysFont('times new roman', 30)
            pause_surface = font.render('Game Paused.', True, white)
            pause_rect = pause_surface.get_rect()
            pause_rect.center = (HEIGHT / 2, WIDTH / 2)
            game_window.blit(pause_surface, pause_rect)
            pygame.display.flip()
            continue

        # Movement logic
        if change_to == 'UP' and direction != 'DOWN':
            direction = 'UP'
        if change_to == 'DOWN' and direction != 'UP':
            direction = 'DOWN'
        if change_to == 'LEFT' and direction != 'RIGHT':
            direction = 'LEFT'
        if change_to == 'RIGHT' and direction != 'LEFT':
            direction = 'RIGHT'

        if direction == 'UP':
            snake_position[1] -= segment_size
        elif direction == 'DOWN':
            snake_position[1] += segment_size
        elif direction == 'LEFT':
            snake_position[0] -= segment_size
        elif direction == 'RIGHT':
            snake_position[0] += segment_size

        snake_body.insert(0, list(snake_position))

        snake_head_rect = pygame.Rect(snake_position[0], snake_position[1], segment_size, segment_size)
        fruit_rect = pygame.Rect(fruit_position[0], fruit_position[1], segment_size, segment_size)
        if snake_head_rect.colliderect(fruit_rect):
            score += fruit_weight  # Increase score based on food weight
            fruit_spawn = False
        else:
            snake_body.pop()

        if pygame.time.get_ticks() - spawn_time > food_lifetime:
            fruit_spawn = False

        if not fruit_spawn:
            fruit_position, fruit_weight, fruit_color, spawn_time = generate_food()
            fruit_spawn = True

        # Level logic
        if score // 10 + 1 > level:
            level += 1
            snake_speed += 5
# Render game objects
        game_window.fill(black)
        for pos in snake_body:
            pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], segment_size, segment_size))
        pygame.draw.rect(game_window, fruit_color, pygame.Rect(fruit_position[0], fruit_position[1], segment_size, segment_size))

        # Collision logic
        if snake_position[0] < 0 or snake_position[0] >= HEIGHT or snake_position[1] < 0 or snake_position[1] >= WIDTH:
            game_over()
        for block in snake_body[1:]:
            if snake_position == block:
                game_over()

        show_score_level()

        pygame.display.update()
        fps.tick(snake_speed)


# Основной блок программы
if __name__ == "__main__":
    connection = connect_to_db()
    if connection:
        create_tables(connection)
        username = input("Введите имя пользователя: ")
        user_id = get_or_create_user(connection, username)
        start_level, start_score = get_user_progress(connection, user_id)
        game_loop(connection, user_id, start_level, start_score)