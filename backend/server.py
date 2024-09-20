from flask import Flask
from flask_cors import CORS
from flask_restx import Api

from resources import admin
from dbmodel import db


cowrywisebea_app = Flask(__name__)
cors = CORS()
api = Api(
    title="CowrywiseBEA",
    version="Beta v0.1.0",
    description="Cowrywise Backend Engineer (Infrastructure, API Engineer, Devops) Assessment backend API for admin management",
    doc="/",
)

cowrywisebea_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///CowrywiseBEAAdminDataStore.db"
cowrywisebea_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(cowrywisebea_app)
api.init_app(cowrywisebea_app)
cors.init_app(cowrywisebea_app)

api.add_namespace(admin)

if __name__ == "__main__":
    cowrywisebea_app.run(
        host="0.0.0.0",
        port=5001,
        debug=True,
    )
