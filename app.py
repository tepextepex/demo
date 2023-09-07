import os
# from dotenv import load_dotenv

from flask import Flask, jsonify
from flask import request, Response
from healthcheck import HealthCheck, EnvironmentDump
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from functools import wraps
import bcrypt
from db_config import conn_string
from crud import *


app = Flask(__name__)

health = HealthCheck()
envdump = EnvironmentDump()

# engine = create_engine("sqlite:///database.db", echo=False, connect_args={"check_same_thread": False})
engine = create_engine(conn_string, echo=False)
Base = declarative_base()

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def check_auth(username, password):
    session = Session()
    if not user_exists(session, username):
        return False
    else:
        true_hash = session.query(User.password).filter(User.name == username).one()[0]
        return True if bcrypt.checkpw(password.encode('utf-8'), true_hash) else False


def login_required(f):
    @wraps(f)
    def wrapped_view(**kwargs):
        auth = request.authorization
        if not (auth and check_auth(auth.username, auth.password)):
            return ('Forbidden', 403, {
                'WWW-Authenticate': 'Basic realm="Login Required"'
            })

        return f(**kwargs)

    return wrapped_view


@app.route("/", methods=['POST'])
@login_required
def health_check():
    try:
        conn = engine.connect()
        conn.close()
        db_status = "OK"
    except Exception as e:
        db_status = repr(e)
    data = {"health": health.run(),
            "envdump": envdump.run(),
            "db_status": db_status}
    return jsonify(data)


@app.route("/version", methods=['POST'])
@login_required
def version():
    try:
        with engine.connect() as con:
            result = con.execute('SELECT version();')
            for row in result:
                db_version = row[0]
    except:
        db_version = "DB not accessible"
    data = {"app_version": os.environ.get("APP_VERSION"),
            "db_version": db_version}
    return jsonify(data)


@app.route("/auth", methods=['POST'])
@login_required
def auth_test():
    return f"Logged as {request.authorization.username}."


@app.route("/user_add", methods=['POST'])
@login_required
def user_add():
    """
    Любой авторизованный юзер может создавать новых юзеров. Статус админа никак не проверяется.
    """
    result = add_user(session, request.json["name"], request.json["password"])
    if result:
        return Response(f"Success: user {request.json['name']} created.", status=200)
    else:
        return Response(f"Error, user {request.json['name']} wasn't created.", status=400)


@app.route("/user_del", methods=['POST'])
@login_required
def user_del():
    """
    Любой авторизованный юзер может удалять любых юзеров, в том числе сам себя.
    """
    result = delete_user(session, request.json["name"])
    if result:
        return Response(f"Success: user {request.json['name']} deleted.", status=200)
    else:
        return Response(f"Error, user {request.json['name']} wasn't deleted.", status=400)


@app.route("/password_update", methods=['POST'])
@login_required
def pass_update():
    """
    Любой авторизованный юзер может изменять пароли любых существующих юзеров.
    """
    result = update_password(session, request.json["name"], request.json["password"])
    if result:
        return f"Success: password for {request.json['name']} updated."
    else:
        return f"Error, password {request.json['name']} wasn't updated."


if __name__ == "__main__":
    admin_name = os.environ.get("ADMIN_NAME")
    admin_pass = os.environ.get("ADMIN_PASS")
    init_db(admin_name, admin_pass)
    app.run(host="0.0.0.0")
