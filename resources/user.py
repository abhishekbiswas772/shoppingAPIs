from flask_smorest import Blueprint, abort
from flask.views import MethodView
from passlib.hash import pbkdf2_sha256
from models import UserModel, BlockListModel
from schema import UserSchema
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt, create_refresh_token, get_jwt_identity
)
from db import db

blp = Blueprint("user", __name__, "Login, Logout And Register Flow")

@blp.route('/register')
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        if (
            UserModel.query.filter(UserModel.username == user_data["username"]).first()
        ):
            abort(409, "A user with this username already exist")

        user_data_model = UserModel(
            username = user_data["username"],
            password = pbkdf2_sha256.hash(user_data["password"])
        )
        try:
            db.session.add(user_data_model)
            db.session.commit()
            return {
                "status" : "user created",
                "message" : "Sucssfully Saved The User in DB"
            }, 201
        except SQLAlchemyError as sqlError:
            print(sqlError)
            abort (500, "Fail to Register The User in Portal, Please Try Again")
        except IntegrityError as ierr:
            print(ierr)
            abort(500, "Fail to Register The User in Portal, Please Try Again")


@blp.route('/user/<int:user_id>')
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user_data = UserModel.query.get_or_404(user_id)
        return user_data

    def delete(self, user_id):
        user_data = UserModel.query.get_or_404(user_id)
        try:
            db.session.delete(user_data)
            db.session.commit()
            return {
                "status" : "User Found",
                "message" : "User Deleted"
            }, 200
        except Exception as e:
            print(e)
            abort(500, "Failed To Delete User From DB")

@blp.route('/login')
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user_data_db = UserModel.query.filter(UserModel.username == user_data["username"]).first()
        if user_data_db and pbkdf2_sha256.verify(user_data_db["password"], user_data_db.password):
            #use user id (primary key) for genrating jwt token
            jwt_token_gen = create_access_token(identity=user_data_db.id, fresh=True)
            jwt_refresh_token = create_refresh_token(identity=user_data_db.id)
            return {
                "access_token" : jwt_token_gen,
                "refresh_token" : jwt_refresh_token
            }, 200
        else:
            abort (
                401,
                message = {
                    "Invalid Credentials. Try Login with Valid Login Credentials"
                }
            )

@blp.route('/logout')
class UserLogout(MethodView):
    @jwt_required
    def post(self):
        jwt_local_token = get_jwt()["jti"]
        jwt_obj_temp_revoke = BlockListModel(
            jwt_tokens = jwt_local_token
        )
        try:
            db.session.add(jwt_obj_temp_revoke)
            db.session.commit()
            return {
                "message" : "Successfully logged out"
            }, 200
        except Exception as e:
            print(e)
            abort(
                500,
                message = {
                    "message" : "Failed to logout",
                    "status" : "Error in Process Logout"
                }
            )



@blp.route('/refresh')
class TokenManager(MethodView):
    @jwt_required(refresh= True)
    def post(self):
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user, fresh=False)
        old_jwt_token = BlockListModel(
            jwt_tokens = get_jwt()["jti"]
        )   
        try:
            db.session.add(old_jwt_token)
            db.session.commit()
            return {
                "access_token" : new_access_token
            }, 201
        except Exception as e:
            print(e)
            abort(
                500, 
                message = {
                    "message" : "Failed to get Refresh Token",
                    "status" : "Token Error"
                }
            )   

        