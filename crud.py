from sqlalchemy import create_engine, ForeignKey, exc
from sqlalchemy import Table, Column, Integer, Float, String, Date, Boolean, LargeBinary
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
import bcrypt
from db_config import conn_string


# engine = create_engine("sqlite:///database.db", echo=False)
engine = create_engine(conn_string, echo=False)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    # name = Column(String, unique=True)
    name = Column(String)
    # password = Column(String)  # работает для sqlite, но не работает для postgres
    password = Column(LargeBinary)  # формат String вызовет ошибку при сравнении паролей с bcrypt
    # salt = Column(String)  # bcrypt хранит соль вместе с паролем
    admin = Column(Boolean)

    def __repr__(self):
        return f"User {self.name}"


def add_user(session, name, password, admin=False):
    try:
        if user_exists(session, name):
            raise ValueError(f"User {name} already exists!")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        u = User(name=name, password=hashed, admin=admin)
        session.add(u)
    except Exception as e:
        print(e)
        session.rollback()
        return False
    else:
        session.commit()
        return True


def user_exists(session, name):
    try:
        result = session.query(User.name).filter(User.name == name).one()
        # print(result)
        return True
    except NoResultFound:
        session.rollback()
        return False
    except exc.OperationalError as err:
        if err.orig.args[0] == 1045:
            print("Access Denied")
        elif err.orig.args[0] == 2003:
            print("Connection Refused")
        return False


def update_password(session, name, new_password):
    try:
        if not user_exists(session, name):
            raise ValueError(f"User {name} does not exist!")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), salt)
        session.query(User).filter(User.name == name).update({"password": hashed})
    except Exception as e:
        print(e)
        session.rollback()
        return False
    else:
        session.commit()
        return True


def delete_user(session, name):
    try:
        if not user_exists(session, name):
            raise ValueError(f"User {name} does not exist!")
        u = session.query(User).filter(User.name == name).one()
        session.delete(u)
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
        return False
    else:
        session.commit()
        return True


def init_db(admin_name, admin_pass):
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # creating the first user with the admin rights:
    if user_exists(session, admin_name):
        update_password(session, admin_name, admin_pass)
    else:
        add_user(session, admin_name, admin_pass, admin=True)
