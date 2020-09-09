import sqlite3

conn=sqlite3.connect('signup.db')
c=conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS signup(
            name text,
            email text,
            password text,
            photo text
            )""")
conn.commit()
conn.close()