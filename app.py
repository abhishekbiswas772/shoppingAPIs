from flask import Flask, jsonify
from flask_smorest import Api
from db import db
from resources.item import blp as ItemBluePrint
from resources.store import blp as StoreBluePrint
from resources.tags import blp as TagBluePrint
from flask_jwt_extended import JWTManager
import secrets
from resources.user import blp as UserBluePrint
import os
from dotenv import load_dotenv
from flask_migrate import Migrate


def create_app(db_url=None):
    app = Flask(__name__)
    # Comment this when Deployment
    # Take From OS Env
    load_dotenv()
    app.config["API_VERSION"] = os.getenv("API_VERSION","v1")
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = os.getenv("API_TITLE", "stores REST API")
    app.config["OPENAPI_VERSION"] = os.getenv("OPENAPI_VERSION", "3.0.3")
    app.config["OPENAPI_URL_PREFIX"] = os.getenv("OPENAPI_URL_PREFIX", "/")
    app.config["OPENAPI_SWAGGER_UI_PATH"] = os.getenv("OPENAPI_SWAGGER_UI_PATH", "/swagger-ui")
    app.config["OPENAPI_SWAGGER_UI_URL"] = os.getenv("OPENAPI_SWAGGER_UI_URL", "https://cdn.jsdelivr.net/npm/swagger-ui-dist/")
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or  os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)

    app.config["JWT_SECRET_KEY"] = secrets.SystemRandom().getrandbits(128) 
    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def expire_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({
                "message" : "The Token Expire, create New Token",
                "error": "token_expired"
            }), 401
        )
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        # print(error)
        return (
            jsonify({
                "message" : "Signature / Token is Invalid, Send Valid Token", "error" : "invalid_token" 
            }), 401
        )

    @jwt.unauthorized_loader
    def unauthorized_token_callback():
        return (
            jsonify(
                {
                    "message" : "Request does't contain access token",
                    "error" : "missing token"
                }
            ), 401
        )

    @jwt.additional_claims_loader
    def additional_claims_callback(identifier):
        if identifier == int(os.getenv("ADMIN_USER_ID", 22100018)):
            return {
                "is_admin" : True
            }
        else:
            return {
                "is_admin" : False
            }
            
    @jwt.needs_fresh_token_loader
    def refresh_tokne_need_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "message" : "Token Expire, Need Fresh Token",
                    "error" : "Fresh token Required"
                }
            ), 401
        )


    api.register_blueprint(ItemBluePrint)
    api.register_blueprint(StoreBluePrint)
    api.register_blueprint(TagBluePrint)
    api.register_blueprint(UserBluePrint)
    return app
