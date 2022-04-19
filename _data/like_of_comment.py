import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class LikeOfComment(SqlAlchemyBase):
    __tablename__ = "like_of_comment"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    id_of_user = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    id_of_comment = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)