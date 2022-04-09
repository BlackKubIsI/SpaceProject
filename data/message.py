import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Message(SqlAlchemyBase):
    __tablename__ = "message"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    id_of_chat = sqlalchemy.Column(sqlalchemy.Integer)
    id_of_user = sqlalchemy.Column(sqlalchemy.Integer)
    n_of_message = sqlalchemy.Column(sqlalchemy.Integer)
    text = sqlalchemy.Column(sqlalchemy.String)