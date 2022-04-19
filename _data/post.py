from datetime import datetime
from email.policy import default
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin

class Post(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "post"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String)
    n_like = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    date_of_post = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.now)