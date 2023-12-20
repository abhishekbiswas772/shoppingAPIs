from schema import StoreSchema
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from models import StoreModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_jwt_extended import jwt_required
from db import db


blp = Blueprint("Stores", __name__, "Operations on stores")


@blp.route('/store/<string:store_id>')
class Store(MethodView):
    @jwt_required(fresh=True)
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store_data = StoreModel.query.get_or_404(store_id)
        return store_data

    @jwt_required(fresh=True)
    def delete(self, store_id):
        item = StoreModel.query.get(store_id)
        db.session.delete(item)
        db.session.commit()
        return {
            "status" : "deleted",
            "message" : "Item deleted"
        }, 200


@blp.route('/store')
class StoreList(MethodView):
    @jwt_required(fresh=True)
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @jwt_required(fresh=True)
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        store_data = StoreModel(**store_data)
        try:
            db.session.add(store_data)
            db.session.commit()
        except IntegrityError as iErr:
            print(iErr)
            abort(400, message = "Store Already Exists in Database")
        except SQLAlchemyError as err:
            print(err)
            abort(500, message = "Error in inserting store in Database")
        return store_data
