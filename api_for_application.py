from flask_restful import reqparse, abort, Api, Resource
from flask import jsonify
from _data import db_session
import datetime

from _data.user import User
from _data.post import Post
from _data.comment import Comment
from _data.message import Message


# parsers

parser_users = reqparse.RequestParser()
parser_users.add_argument('nick', required=True)
parser_users.add_argument('about', required=True)
parser_users.add_argument('address', required=True)
parser_users.add_argument('registration_date', required=True)
parser_users.add_argument('password', required=True)
parser_users.add_argument('birthday', required=True)

parser_posts = reqparse.RequestParser()
parser_posts.add_argument('user_id', required=True)
parser_posts.add_argument('text', required=True)
parser_posts.add_argument('image', required=True)
parser_posts.add_argument('n_like', required=True)
parser_posts.add_argument('date_of_post', required=True)

parser_comments = reqparse.RequestParser()
parser_comments.add_argument('id_of_user', required=True)
parser_comments.add_argument('id_of_post', required=True)
parser_comments.add_argument('text', required=True)
parser_comments.add_argument('n_like', required=True)

parser_messages = reqparse.RequestParser()
parser_messages.add_argument('id_of_chat', required=True)
parser_messages.add_argument('id_of_user', required=True)
parser_messages.add_argument('n_of_message', required=True)
parser_messages.add_argument('text', required=True)

# end of parsers


# classes

class GetUsers(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('id', 'nick', 'about', 'address', 'registration_date', 'birthday')) for item in users]})

    def post(self):
        DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
        args = parser_users.parse_args()
        session = db_session.create_session()
        user = User(
            nick=args["nick"],
            about=args["nick"],
            address=args["address"],
            registration_date=datetime.datetime.strptime(
                args["registration_date"], DATE_FORMAT),
            birthday=datetime.datetime.strptime(
                args["birthday"], DATE_FORMAT.split()[0])
        )
        user.set_password(args["password"])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})


class GetUser(Resource):
    def get(self, user_id):
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=('id', 'nick', 'about', 'address', 'registration_date', 'birthday'))})

    def delete(self, user_id):
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class GetPosts(Resource):
    def get(self):
        session = db_session.create_session()
        posts = session.query(Post).all()
        return jsonify({'posts': [item.to_dict(
            only=('id', 'user_id', 'text', 'image', 'n_like', 'date_of_post')) for item in posts]})

    def post(self):
        DATE_FORMAT = "%Y-%m-%d"
        args = parser_posts.parse_args()
        session = db_session.create_session()
        post = Post(
            user_id=args["user_id"],
            text=args["text"],
            image=args["image"],
            n_like=args["n_like"],
            date_of_post=datetime.datetime.strptime(
                args["date_of_post"], DATE_FORMAT)
        )
        session.add(post)
        session.commit()
        return jsonify({'success': 'OK'})


class GetPost(Resource):
    def get(self, post_id):
        session = db_session.create_session()
        post = session.query(Post).get(post_id)
        return jsonify({'post': post.to_dict(
            only=('id', 'user_id', 'text', 'image', 'n_like', 'date_of_post'))})

    def delete(self, post_id):
        session = db_session.create_session()
        post = session.query(Post).get(post_id)
        session.delete(post)
        session.commit()
        return jsonify({'success': 'OK'})


class GetComments(Resource):
    def get(self):
        session = db_session.create_session()
        comments = session.query(Comment).all()
        return jsonify({'comments': [item.to_dict(
            only=('id', 'id_of_user', 'id_of_post', 'text', 'n_like')) for item in comments]})

    def post(self):
        args = parser_comments.parse_args()
        session = db_session.create_session()
        comment = Comment(
            id_of_user=args["id_of_user"],
            id_of_post=args["id_of_post"],
            text=args["text"],
            n_like=args["n_like"],
        )
        session.add(comment)
        session.commit()
        return jsonify({'success': 'OK'})


class GetComment(Resource):
    def get(self, comment_id):
        session = db_session.create_session()
        comment = session.query(Comment).get(comment_id)
        return jsonify({'comment': comment.to_dict(
            only=('id', 'id_of_user', 'id_of_post', 'text', 'n_like'))})

    def delete(self, comment_id):
        session = db_session.create_session()
        comment = session.query(Comment).get(comment_id)
        session.delete(comment)
        session.commit()
        return jsonify({'success': 'OK'})


class GetMessages(Resource):
    def get(self):
        session = db_session.create_session()
        messages = session.query(Message).all()
        return jsonify({'messages': [item.to_dict(
            only=('id', 'id_of_chat', 'id_of_user', 'n_of_message', 'text')) for item in messages]})

    def post(self):
        args = parser_messages.parse_args()
        session = db_session.create_session()
        message = Message(
            id_of_chat=args["id_of_chat"],
            id_of_user=args["id_of_user"],
            n_of_message=args["n_of_message"],
            text=args["text"],
        )
        session.add(message)
        session.commit()
        return jsonify({'success': 'OK'})


class GetMessage(Resource):
    def get(self, message_id):
        session = db_session.create_session()
        message = session.query(Message).get(message_id)
        return jsonify({'message': message.to_dict(
            only=('id', 'id_of_chat', 'id_of_user', 'n_of_message', 'text'))})

    def delete(self, message_id):
        session = db_session.create_session()
        message = session.query(Message).get(message_id)
        session.delete(message)
        session.commit()
        return jsonify({'success': 'OK'})

# end of classes
