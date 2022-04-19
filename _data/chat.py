import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Chat(SqlAlchemyBase):
    __tablename__ = "chat"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    id_of_user_1 = sqlalchemy.Column(sqlalchemy.Integer)
    id_of_user_2 = sqlalchemy.Column(sqlalchemy.Integer)