import sqlite3

news=(
    (1,"бизнес","business"),
    (2,"развлечения","entertainment"),
    (3,"общее","general"),
    (4,"здоровье","health"),
    (5,"наука","science"),
    (6,"спорт","sports"),
    (7,"технологии","technology")
)

def checkBase():
    try:
        con=sqlite3.connect('database.db')
        cursor=con.cursor()
        cursor.execute(
            """ CREATE TABLE IF NOT EXISTS "users" (
            "id"	INTEGER,
            "login"	TEXT,
            "username" TEXT,
            PRIMARY KEY("id")
        );
        """ )
        cursor.execute(
            """   CREATE TABLE IF NOT EXISTS "categories" (
	        "id"	INTEGER NOT NULL,
            "local_name"  TEXT,
	        "name"	TEXT,
	        PRIMARY KEY("id" AUTOINCREMENT)
        );""")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS "subscribes" (
	        "id_user"	INTEGER,
	        "id_categories"	INTEGER,
	        FOREIGN KEY("id_user") REFERENCES "users"("id"),
	        FOREIGN KEY("id_categories") REFERENCES "categories"("id")
        );"""
        )
        cursor.executemany(
            """INSERT INTO "categories" (id,local_name,name) VALUES (?,?,?)""", news
        )
        con.commit()
    except sqlite3.Error:
        print ("not create")
    finally:
        con.close()
