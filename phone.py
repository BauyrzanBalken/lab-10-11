import psycopg2
import csv
import string

conn = psycopg2.connect(
  host = 'localhost',
  database = 'postgres',
  user = 'postgres',
  password = 'Dias2009*'
)

cur = conn.cursor()

import csv

filename = 'phone_book.csv'


with open(filename, 'w', newline='',encoding="utf8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Name', ' Phone'])
    writer.writerow(['Anna',870712345])
    writer.writerow(['Ivan',874701010])
    writer.writerow(['Tomirsis',870100035])
    writer.writerow(['Ayan',877755555])
    print("CSV файл успешно создан.")

def create_table():
    create_query = """
    CREATE TABLE IF NOT EXISTS phone_book (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        phone VARCHAR(15) NOT NULL UNIQUE
    );
    """
    cur.execute(create_query)
    conn.commit()
    print("Table 'phone_book' created successfully.")

create_table()


def find_user_by_number(number):
  select_query = f"select * from phone_book where phone = {number};"
  cur.execute(select_query)
  return cur.fetchone()

def find_user_by_name(name):
  select_query = f"select * from phone_book where name = '{name}';"
  cur.execute(select_query)
  return cur.fetchone()

def add_new_user():
  name = input("User name: ")
  phone = int(input("User phone: "))
  insert_query = f"INSERT INTO phone_book (name, phone) VALUES ('{name}', '{phone}');"
  cur.execute(insert_query)
  conn.commit()
  print("User phone added sucsessfully!")

def update_userInfo():
  answer = input("Write 'N' if you wanna change the user name or write 'P' if you wanna change the phone: ")
  if answer == 'P':
    number = int(input("Write the number which you wanna change: " ))
    checked = find_user_by_number(number)
    if (checked is not None):
      new_number = int(input("Write new number: "))
      update_number = f"update phone_book set phone = {new_number} where phone = '{number}';"
      cur.execute(update_number)
      conn.commit()
      print("User phone changed sucsessfully!")
    else:
      print("User not found")
  elif answer == 'N':
    name = input("Write the name which you wanna change: " )
    checked = find_user_by_name(name)
    if (checked is not None):
      new_name = input("Write new name: ")
      update_name = f"update phone_book set name = '{new_name}' where name = '{name}';"
      cur.execute(update_name)
      conn.commit()
      print("User name changed sucsessfully!")
    else:
      print("User not found")


def show_data():
  q = """
Choose the query:
1 - find user by name
2 - find user by phone number
3 - Show all users with their phone numbers
"""
  query = int(input(q))
  if query == 1:
    name = input("Write user name: ")
    checked = find_user_by_name(name)
    if (checked is not None):
      select_query = f"select phone from phone_book where name = '{name}';"
      cur.execute(select_query)
      print(f"Users phone is: {cur.fetchone()[0]}")
    else:
      print("User not found")
  elif query == 2:
    phone = int(input("Write user phone: "))
    checked = find_user_by_number(phone)
    if (checked is not None):
      select_query = f"select name from phone_book where phone = {phone};"
      cur.execute(select_query)
      print(f"Users name is: {cur.fetchone()[0]}")
    else:
      print("User not found")
  elif query == 3:
    cur.execute(f"select name from phone_book;")
    names = cur.fetchall()
    cur.execute(f"select phone from phone_book;")
    phones = cur.fetchall()
    print("Names      Phone numbers")
    for x in range(len(names)):
      print(f"{names[x][0]}:       {phones[x][0]}")

def delete_users():
  answer = input("Write 'N' if you wanna delete user by name or write 'P' if you wanna delete user by phone: ")
  if answer == 'P':
    number = int(input("Write the number which you wanna delete: " ))
    checked = find_user_by_number(number)
    if (checked is not None):
      delete_number = f"delete from phone_book where phone = '{number}';"
      cur.execute(delete_number)
      conn.commit()
      print("User phone deleted sucsessfully!")
    else:
      print("User not found")
  elif answer == 'N':
    name = input("Write the name which you wanna delete: " )
    checked = find_user_by_name(name)
    if (checked is not None):
      delete_name = f"delete from phone_book where name = '{name}';"
      cur.execute(delete_name)
      conn.commit()
      print("User name deleted sucsessfully!")
    else:
      print("User not found")

if __name__ == '__main__':
    create_table()  

def main():
  menu = """
Choose the number:
1 - add new phone user
2 - change user phone or name
3 - query
4 - delete users
"""

  start = int(input(menu))
  if start == 1:
    add_new_user()
  elif start == 2:
    update_userInfo()
  elif start == 3:
    show_data()
  elif start == 4:
    delete_users()
    
if __name__ == '__main__':
  main()

conn.close()