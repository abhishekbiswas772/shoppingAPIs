from flask_smorest import abort, Blueprint
from flask.views import MethodView
from db import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models import TagModel, ItemModel, StoreModel
from schema import TagSchema, TagItemSchema

blp = Blueprint("Tags", __name__,  "Operations on Tags")


@blp.route('/store/<string:store_id>/tag')
class Tags(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store_items = StoreModel.query.get_or_404(store_id)
        return store_items

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_body, store_id):
        if TagModel.query.filter(TagModel.id == store_id, TagModel.name == tag_body["name"]).first():
            abort(400, message = {
                "status" : "Store already Present",
                "message" : "A tag with that name already exists in that store."
            })

        tag_item = TagModel(**tag_body, store_id = store_id)
        try:
            db.session.add(tag_item)
            db.session.commit()
        except SQLAlchemyError as sqlError:
            print(sqlError)
            abort(
                500, 
                messsage = "Error in Inserting Tags to Store In DB"
            )
        except IntegrityError as iErr:
            print(iErr)
            abort(
                500,
                messgae = "Error in Inserting Tags to Store In DB"
            )
        return tag_item


@blp.route('/tag/<string:tag_id>')
class TagListModel(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag_item = TagModel.query.get_or_404(tag_id)
        return tag_item

    @blp.response(202, 
        description = "Delete the tag with item is assocaited with it", 
        example= {
            "message" : "Tag Deleted"
        }
    )
    @blp.alt_response(404, description = "Tag Not Found")
    @blp.alt_response(
        400,
        description = "bad request for tag for items"
    )
    def delete(self, tag_id):
        tag_item = TagModel.query.get_or_404(tag_id)
        try:
            db.session.delete(tag_item)
            ab.session.commit()
            return {
                "message" : "Tag Deleted",
            }, 202
        except Exception as err:
            print(err)
            abort(
                400,
                message = {
                    "status" : "Not Found",
                    "message" : "Item with this tag not found"
                }
            )
           
@blp.route('/store/<string:item_id>/tag/<string:tag_id>')
class LinkTagsToItem(MethodView):
    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item_object = ItemModel.query.get_or_404(item_id)
        tag_object = TagModel.query.get_or_404(tag_id)
        try:
            item_object.tags.append(tag_object)
            db.session.add(item_object)
            db.session.commit() 
        except Exception as err:
            print(err)
            abort(
                500,
                message = {
                    "status" : "Tag Inseration Failed",
                    "message" : "Tag Insertion Failed for this Item"
                }
            )
    @blp.response(200, TagItemSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        try:
            item.tags.remove(tag)
            db.session.add(item)
            db.session.commit()
            return {
                "status" : "Tag Delete Failed",
                "message" : "error occurced while removing Tag"
            }, 200
        except Exception as err:
            print(err)
            abort(
                500,
                message = {
                    "message" : "An occured while inserting the Tag For this item"
                }
            )
