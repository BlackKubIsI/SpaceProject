import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Post(SqlAlchemyBase):
    __tablename__ = "post"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String)
    n_like = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    date_of_post = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)