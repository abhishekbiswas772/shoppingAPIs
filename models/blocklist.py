from db import db


class BlockListModel(db.Model):
    __tablename__ = "blocklist"
    id = db.Column(db.Integer, primary_key = True)
    jwt_tokens = db.Column(db.String(1024), unique = True, nullable = False)