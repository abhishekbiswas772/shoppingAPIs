from db import db


class BlockList(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    jwt_tokens = db.Column(db.String(1024), unique = True, nullable = False)