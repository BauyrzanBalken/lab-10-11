import pygame
import psycopg2
import time
import random

def initialize_database():
    """Подключается к базе данных и создает соединение."""
    try:
        return psycopg2.connect(
            dbname="snake",
            user="postgres",
            password="Erkin2006",
            host="localhost",
            port="5432"
        )
    except psycopg2.Error as error:
        print(f"Ошибка соединения с БД: {error}")
        return None

def setup_database(conn):
    """Создает необходимые таблицы в базе данных."""
    try:
        with conn.cursor() as cursor:
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
                    level INTEGER DEFAULT 1,
                    score INTEGER DEFAULT 0
                );
            """)
            conn.commit()
    except psycopg2.Error as error:
        print(f"Ошибка при создании таблиц: {error}")

def get_or_add_user(conn, username):
    """Возвращает ID пользователя, добавляя его, если он не существует."""
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s;", (username,))
            user = cursor.fetchone()
            if user:
                return user[0]

            cursor.execute("INSERT INTO users (username) VALUES (%s) RETURNING id;", (username,))
            conn.commit()
            return cursor.fetchone()[0]
    except psycopg2.Error as error:
        print(f"Ошибка при обработке пользователя: {error}")


def get_progress(conn, user_id):
    """Получает уровень и очки пользователя."""
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT level, score FROM user_scores WHERE user_id = %s ORDER BY id DESC LIMIT 1;", (user_id,))
            progress = cursor.fetchone()
            return progress if progress else (1, 0)
    except psycopg2.Error as error:
        print(f"Ошибка получения прогресса: {error}")


def record_progress(conn, user_id, level, score):
    """Сохраняет прогресс пользователя."""
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO user_scores (user_id, level, score) VALUES (%s, %s, %s);", (user_id, level, score))
            conn.commit()
    except psycopg2.Error as error:
        print(f"Ошибка записи прогресса: {error}")


def main_game(conn, user_id, initial_level, initial_score):
    """Главный игровой цикл."""
    pygame.init()

    # Константы
    speed = 5
    SCREEN_HEIGHT, SCREEN_WIDTH = 700, 500
    SQUARE_SIZE = 20

    # Цвета
    COLORS = {
        1: pygame.Color(255, 215, 0),
        2: pygame.Color(255, 140, 0),
        3: pygame.Color(255, 0, 0),
        4: pygame.Color(138, 43, 226),
        5: pygame.Color(75, 0, 130)
    }

    # Окно игры
    screen = pygame.display.set_mode((SCREEN_HEIGHT, SCREEN_WIDTH))
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()

    # Параметры игры
    level = initial_level
    score = initial_score
    snake = [[100, 50], [80, 50], [60, 50]]
    direction = 'RIGHT'

    def generate_food():
        position = [
            random.randint(1, (SCREEN_HEIGHT // SQUARE_SIZE) - 1) * SQUARE_SIZE,
            random.randint(1, (SCREEN_WIDTH // SQUARE_SIZE) - 1) * SQUARE_SIZE
        ]
        weight = random.randint(1, 5)
        return position, weight, COLORS[weight]

    food_position, food_weight, food_color = generate_food()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                record_progress(conn, user_id, level, score)
                pygame.quit()
                return

        # Логика движения
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and direction != 'DOWN':
            direction = 'UP'
        elif keys[pygame.K_DOWN] and direction != 'UP':
            direction = 'DOWN'
        elif keys[pygame.K_LEFT] and direction != 'RIGHT':
            direction = 'LEFT'
        elif keys[pygame.K_RIGHT] and direction != 'LEFT':
            direction = 'RIGHT'

        # Обновление позиции
        if direction == 'UP':
            snake[0][1] -= SQUARE_SIZE
        elif direction == 'DOWN':
            snake[0][1] += SQUARE_SIZE
        elif direction == 'LEFT':
            snake[0][0] -= SQUARE_SIZE
        elif direction == 'RIGHT':
            snake[0][0] += SQUARE_SIZE

        # Добавление сегмента
        snake.insert(0, list(snake[0]))
        if snake[0] == food_position:
            score += food_weight
            food_position, food_weight, food_color = generate_food()
        else:
            snake.pop()

        # Проверка на столкновение
        if any(block == snake[0] for block in snake[1:]) or \
           snake[0][0] < 0 or snake[0][1] < 0 or \
           snake[0][0] >= SCREEN_HEIGHT or snake[0][1] >= SCREEN_WIDTH:
            record_progress(conn, user_id, level, score)
            pygame.quit()
            return

        # Отрисовка
        screen.fill(pygame.Color(0, 0, 0))
        for block in snake:
            pygame.draw.rect(screen, pygame.Color(0, 255, 0), (*block, SQUARE_SIZE, SQUARE_SIZE))
        pygame.draw.rect(screen, food_color, (*food_position, SQUARE_SIZE, SQUARE_SIZE))

        # Показ уровня и очков
        font = pygame.font.SysFont('Arial', 20)
        score_text = font.render(f"Score: {score} Level: {level}", True, pygame.Color(255, 255, 255))
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(speed)

if __name__ == "__main__":
    connection = initialize_database()
    if connection:
        setup_database(connection)
        user = input("Введите имя пользователя: ")
        user_id = get_or_add_user(connection, user)
        level, score = get_progress(connection, user_id)
        main_game(connection, user_id, level, score)
