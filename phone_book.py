import psycopg2
import csv

# Настройка соединения с базой данных
connection = psycopg2.connect(
    host='localhost',
    database='postgres',
    user='postgres',
    password='Erkin2006'
)
cursor = connection.cursor()


# Функция для создания таблицы в базе данных
def initialize_table():
    query = """
    CREATE TABLE IF NOT EXISTS phone_book (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        phone VARCHAR(15) NOT NULL UNIQUE
    );
    """
    cursor.execute(query)
    connection.commit()
    print("Table 'phone_book' is ready.")

initialize_table()

# Поиск пользователя по номеру телефона
def get_user_by_phone(phone):
    cursor.execute("SELECT * FROM phone_book WHERE phone = %s;", (phone,))
    return cursor.fetchone()

# Поиск пользователя по имени
def get_user_by_name(name):
    cursor.execute("SELECT * FROM phone_book WHERE name = %s;", (name,))
    return cursor.fetchone()

# Добавление нового пользователя
def insert_user():
    user_name = input("Enter user name: ")
    user_phone = input("Enter user phone: ")
    try:
        cursor.execute("INSERT INTO phone_book (name, phone) VALUES (%s, %s);", (user_name, user_phone))
        connection.commit()
        print("New user added successfully.")
    except psycopg2.Error as e:
        print(f"Error: {e}")

# Обновление информации о пользователе
def modify_user():
    choice = input("Change name (N) or phone (P): ").strip().upper()
    if choice == 'P':
        old_phone = input("Enter current phone number: ")
        if get_user_by_phone(old_phone):
            new_phone = input("Enter new phone number: ")
            cursor.execute("UPDATE phone_book SET phone = %s WHERE phone = %s;", (new_phone, old_phone))
            connection.commit()
            print("Phone updated successfully.")
        else:
            print("Phone not found.")
    elif choice == 'N':
        old_name = input("Enter current name: ")
        if get_user_by_name(old_name):
            new_name = input("Enter new name: ")
            cursor.execute("UPDATE phone_book SET name = %s WHERE name = %s;", (new_name, old_name))
            connection.commit()
            print("Name updated successfully.")
        else:
            print("Name not found.")

# Отображение данных
def display_data():
    print("1. Search by name")
    print("2. Search by phone")
    print("3. Show all users")
    option = input("Choose an option: ")
    if option == '1':
        name = input("Enter name: ")
        user = get_user_by_name(name)
        print(f"Phone: {user[2]}" if user else "User not found.")
    elif option == '2':
        phone = input("Enter phone: ")
        user = get_user_by_phone(phone)
        print(f"Name: {user[1]}" if user else "User not found.")
    elif option == '3':
        cursor.execute("SELECT name, phone FROM phone_book;")
        for row in cursor.fetchall():
            print(f"{row[0]} - {row[1]}")

# Удаление пользователя
def remove_user():
    option = input("Delete by name (N) or phone (P): ").strip().upper()
    if option == 'P':
        phone = input("Enter phone to delete: ")
        if get_user_by_phone(phone):
            cursor.execute("DELETE FROM phone_book WHERE phone = %s;", (phone,))
            connection.commit()
            print("User deleted successfully.")
        else:
            print("Phone not found.")
    elif option == 'N':
        name = input("Enter name to delete: ")
        if get_user_by_name(name):
            cursor.execute("DELETE FROM phone_book WHERE name = %s;", (name,))
            connection.commit()
            print("User deleted successfully.")
        else:
            print("Name not found.")

# Основное меню программы
def main():
    while True:
        print("\nMenu:")
        print("1. Add new user")
        print("2. Update user")
        print("3. Display data")
        print("4. Delete user")
        print("5. Exit")
        choice = input("Select an option: ").strip()
        if choice == '1':
            insert_user()
        elif choice == '2':
            modify_user()
        elif choice == '3':
            display_data()
        elif choice == '4':
            remove_user()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
    connection.close()
