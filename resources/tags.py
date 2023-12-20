from flask_smorest import abort, Blueprint
from flask.views import MethodView
from db import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models import TagModel, StoreModel, ItemTagsModel
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
        

@blp.route('/store/<string:store_id>/tag/<string:tag_id>')
class LinkTagsToItem(MethodView):
    @blp.response(201, TagSchema)
    def post(self, store_id, tag_id):
        pass