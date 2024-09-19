from flask import Flask
from flask_cors import CORS
from flask_restx import Api

from resources import user
from dbmodel import db


cowrywisebea_app = Flask(__name__)
cors = CORS()
api = Api(
    title="CowrywiseBEA",
    version="Beta v0.1.0",
    description="Cowrywise Backend Engineer (Infrastructure, API Engineer, Devops) Assessment frontend API for user management",
    doc="/",
)

cowrywisebea_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///CowrywiseBEAUserDataStore.db"
cowrywisebea_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(cowrywisebea_app)
api.init_app(cowrywisebea_app)
cors.init_app(cowrywisebea_app)

api.add_namespace(user)

if __name__ == "__main__":
    cowrywisebea_app.run(debug=True)
