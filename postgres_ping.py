from sqlalchemy import create_engine

db_user = "postgres"
db_pass = "pass123"
hostname = "127.0.0.1:5432"

conn_string = f"postgresql+psycopg2://{db_user}:{db_pass}@{hostname}/postgres"
# print(conn_string)
engine = create_engine(conn_string)

# Доступна ли БД?
with engine.connect() as con:
    result = con.execute('SELECT version();')
    for row in result:
        version = row
    print(version)

# Действительно ли при запуске приложения была создана админская учетная запись?
with engine.connect() as con:
    result = con.execute('SELECT * FROM users;')
    for row in result:
        print(row)
