import sqlite3

conn=sqlite3.connect('product.db')
c=conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS buy_product(
            added_time text,
            buyed_time text,
            buyer_email text,
            buyer_name text
            )""")
conn.commit()
conn.close()