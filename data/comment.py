import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Comment(SqlAlchemyBase):
    __tablename__ = "comment"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    id_of_user = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    id_of_post = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    n_like = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)