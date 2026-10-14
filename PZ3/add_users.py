import sqlite3
import urllib3

db_file_name='users.db'

conn = sqlite3.connect(db_file_name)
cursor = conn.cursor()

user=[
    ["Галя", "Galya@gmail.com"],
    ["Толя", "Tolya@gmail.com"],
    ["Николай", "Nokolai@gmail.com"],
    ["Нина", "Nina@gmail.com"]
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
    [3,1], [3,2], [3,4], [3,6], [1,9],
    [4,4], [4,6], [4,8], [4,9]
]

for i in range(len(usersCategories)):
    cursor.execute(
        "INSERT INTO user_categories (user_id, category_id) VALUES (?, ?)",
        (usersCategories[i][0], usersCategories[i][1])
    )
    conn.commit()

conn.close()