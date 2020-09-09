import sqlite3

conn=sqlite3.connect('answer.db')
c=conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS answer (
                asked_on text,
                answered_on text,
                answer text,
                photo text,
                answerd_by text,
                answer_by_email text
                )""")
conn.commit()
conn.close()