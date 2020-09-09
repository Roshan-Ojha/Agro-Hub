import sqlite3
import datetime
conn=sqlite3.connect("question_product.db")
c=conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS question(
                date_time text,
                email text,
                title text,
                question text,
                photo text,
                type text,
                asked_by text
                )""")

c.execute("""CREATE TABLE IF NOT EXISTS product(
            date_time text,
            email text,
            title text,
            description text,
            photo text,
            type text,
            added_by text
            )""")
conn.commit()
conn.close()

now=datetime.datetime.now()
print(now)