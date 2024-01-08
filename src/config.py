import os
import requests


from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

postgres_migrations_repo = os.path.join(BASE_DIR,'migrations','postgresql')

POSTGRES_DATABASE = f'postgresql://{os.getenv("DB_Username")}:{os.getenv("DB_Password")}@{os.getenv("DB_Host")}/{os.getenv("DB_name")}'

POSTGRES_DATABASE_Test = f'postgresql://{os.getenv("DB_Username")}:{os.getenv("DB_Password")}@{os.getenv("DB_Host")}/{os.getenv("test_DB_name")}'


app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_DATABASE

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Define metadata, instantiate db
metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

migrate = Migrate(app, db, directory=postgres_migrations_repo)

db.init_app(app)