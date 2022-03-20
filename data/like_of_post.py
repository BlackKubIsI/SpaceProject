import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class LikeOfPost(SqlAlchemyBase):
    __tablename__ = "like_of_post"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    id_of_user = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    id_of_post = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)