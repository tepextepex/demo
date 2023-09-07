import os
from dotenv import load_dotenv

load_dotenv()

db_user = "postgres"
db_pass = os.environ.get("DB_PASS")
# print(f"DB pass: {db_pass}")

db_port = os.environ.get("DB_PORT")
# print(f"Port: {db_port}")

hostname = "127.0.0.1"

conn_string = f"postgresql+psycopg2://{db_user}:{db_pass}@{hostname}:{db_port}/postgres"
