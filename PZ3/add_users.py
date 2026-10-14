import sqlite3
import urllib3

db_file_name='users.db'

conn = sqlite3.connect(db_file_name)
cursor = conn.cursor()

user=[
    ["Галя", "Galya@gmail.com"],
    ["Толя", "Tolya@gmail.com"],
    ["Николай", "Nokolay@gmail.com"],
    ["Генадий", "Genadiy@gmail.com"]
    ["Петр", "Petr@gmail.com"]
    ["Олег", "Oleg@gmail.com"]
    ["Валера", "Valera@gmail.com"]

]
for i in range(len(user)):
    cursor.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        (user[i][0], user[i][1])
    )
    conn.commit()

usersCategories=[
    [1,1], [1,4], [1,5], [1,8],
    [2,2], [2,3], [2,7],
    [3,1], [3,8],
    [4,4], [4,6], [4,8], [4,9],
    [5,2], [4,5],
    [6,4], [4,6], [4,7],
    [7,1], [4,2], [4,3], [4,4]
]

for i in range(len(usersCategories)):
    cursor.execute(
        "INSERT INTO user_categories (user_id, category_id) VALUES (?, ?)",
        (usersCategories[i][0], usersCategories[i][1])
    )
    conn.commit()

conn.close()