import sqlite3

conn = sqlite3.connect("testdb.db")
cursor = conn.cursor()

cursor.execute("""Insert into test VALUES ('Vova', 'Kakakshka') """)
conn.commit()