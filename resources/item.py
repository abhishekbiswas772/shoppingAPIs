from schema import ItemSchema, ItemUpdateSchema
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask import request
from db import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from models import ItemModel
from flask_jwt_extended import jwt_required, get_jwt

blp = Blueprint("Items", __name__, "Operations on Items")

@blp.route('/item/<string:item_id>')
class Item(MethodView):
    @jwt_required(fresh=True)
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        items = ItemModel.query.get_or_404(item_id)
        return items

    @jwt_required(fresh=True)
    def delete(self, item_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            return abort(
                401,
                message = {
                    "message" : "Need Admin Access For Deleting Item",
                    "status" : "missing admin privilege"
                }
            )

        item = ItemModel.query.get(item_id)
        db.session.delete(item)
        db.session.commit()
        return {
            "status" : "deleted",
            "message" : "Store deleted"
        }, 200

    @jwt_required(fresh=True)
    @blp.arguments(ItemUpdateSchema) #for validations
    @blp.response(201, ItemSchema)
    def put(self, item_data, item_id):
        item = ItemModel.query.get(item_id)
        if item:
            item.name = item_data["name"]
            item.price = item_data["price"]
        else:
            item = ItemModel(**item_data, id = item_id)
        db.session.add(item)
        db.session.commit()
        return item



@blp.route('/item')
class ItemList(MethodView):
    @jwt_required(fresh=True)
    @blp.response(201, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @jwt_required(fresh=True)
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        item_data = ItemModel(**item_data)
        try:
            db.session.add(item_data)
            db.session.commit()
        except IntegrityError as iErr:
            print(iErr)
            abort(
                400, 
                message = "Item is already present in database"
            )
        except SQLAlchemyError as sqlError:
            print(sqlError)
            abort(500, message = "Error Occer while inserting item in database")

        return item_data
