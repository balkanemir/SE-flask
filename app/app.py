
import json
from flask import request
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from http import HTTPStatus
from initialise import Initialise
from flask import Flask
# Creates the Flask app
app = Flask(__name__)
init = Initialise()
app = init.db(app)
# Creates the db connection
db = SQLAlchemy(app)