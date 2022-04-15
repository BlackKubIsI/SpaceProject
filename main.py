from flask import Flask, redirect, render_template, request
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from flask_login import current_user, LoginManager, login_required, logout_user, login_user
from wtforms.validators import DataRequired
from wtforms import StringField, BooleanField, SubmitField, IntegerField
from wtforms import DateField, PasswordField, EmailField, TextAreaField, FileField
from flask_restful import reqparse, abort, Api, Resource
from werkzeug.utils import secure_filename

import nasapy
import base64
import sys
import datetime
from data.user import User
from data.post import Post
from data.like_of_post import LikeOfPost
from data.like_of_comment import LikeOfComment
from data.comment import Comment
from data.chat import Chat
from data.message import Message
from data import db_session
import api_for_application

app = Flask(__name__)
api = Api(app)
app.config["SECRET_KEY"] = "random_key"

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


class NasaInterfese:
    nasa = nasapy.Nasa(key="29bQr5rknKaUFZrD3TVmhOB2nNHrhgRpBHal0mIB")

    def get_mars_img(self, earth_date):
        data = self.nasa.mars_rover(earth_date=earth_date)
        d = {}
        for i in data:
            if i["camera"]["id"] not in list(d.keys()):
                d[i["camera"]["id"]] = {
                    "name": i["camera"]["full_name"], "img": [i["img_src"]]}
            else:
                d[i["camera"]["id"]]["img"].append(i["img_src"])
        return d


class DateForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    submit = SubmitField("Search")


class RegistrationForm(FlaskForm):
    nick = StringField("Nick", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField(
        'PasswordAgain', validators=[DataRequired()])
    about = TextAreaField("About", validators=[DataRequired()])
    birthday = DateField("Birthday", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    submit = SubmitField("Registration")


class LoginForm(FlaskForm):
    nick = StringField("Nick", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField("Log in")


@app.route("/user/<int:user_id>", methods=["GET", "POST"])
@login_required
def user_profile(user_id):
    return render_template("user_profile.html", title="TEST", name='BlackKub', posts={'posts': [
        {'post_description': '123',
         'post_photo': 'https://sun9-42.userapi.com/impf/Mp93Y8AkP7w1tgvn5W8yz8LbfJB5u-knSwmn4Q/5GOrvebr898.jpg?size'
                       '=460x320&quality=95&sign=38e32a4abfb798f53eb5d962f656400f&type=album'},
        {'post_description': '123',
         'post_photo': 'https://sun9-42.userapi.com/impf/Mp93Y8AkP7w1tgvn5W8yz8LbfJB5u-knSwmn4Q/5GOrvebr898.jpg?size'
                       '=460x320&quality=95&sign=38e32a4abfb798f53eb5d962f656400f&type=album'}
    ]})


@app.route('/upload/<int:user_id>', methods=["POST"])
def upload_file(user_id):
    f = request.files['file']
    with open("t.txt", mode="w", encoding="utf-8") as a:
        a.write(str(base64.b64encode(f.read())))
    print(base64.b64encode(f.read()))
    f.save(secure_filename(f.filename))
    return redirect("/")


# главная


@app.route("/", methods=["GET", "POST"])
def main():
    return render_template("base.html", title="TEST")


# добавление комментария


@app.route("/user/<int:user_id>/post/<int:post_id>/comment/add", methods=["GET", "POST"])
@login_required
def add_comment(user_id, post_id):
    if request.method == "POST":
        db_sess = db_session.create_session()
        comment = Comment(
            id_of_user=user_id,
            id_of_post=post_id,
            text=request.form["text"],
            n_like=0
        )
        db_sess.add(comment)
        db_sess.commit()
        return render_template('base.html')
    return render_template("add_comment.html", title="AddComment", inf={"user_id": user_id, "post_id": post_id})


# редактирование комментария


@app.route("/user/<int:user_id>/post/<int:post_id>/comment/red/<int:comment_id>", methods=["GET", "POST"])
@login_required
def red_comment(user_id, post_id, comment_id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).filter(Comment.id == comment_id).first()
    if request.method == "POST":
        comment.text = request.form["text"]
        db_sess.commit()
        return render_template('base.html')
    return render_template("red_comment.html", title="RedComment",
                           inf={"user_id": user_id, "post_id": post_id, "text": comment.text})


# удаление комментария


@app.route("/user/<int:user_id>/post/<int:post_id>/comment/del/<int:comment_id>", methods=["GET", "POST"])
@login_required
def del_comment(user_id, post_id, comment_id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).get(comment_id)
    db_sess.delete(comment)
    db_sess.commit()
    return render_template("base.html", title="RedPost")


# добавление поста


@app.route("/user/<int:user_id>/post/add", methods=["GET", "POST"])
@login_required
def add_post(user_id):
    if request.method == "POST":
        db_sess = db_session.create_session()
        img_file = request.files['file']
        post = Post(
            user_id=user_id,
            text=request.form["text"],
            image=str(base64.b64encode(img_file.read()))[2:-1],
            n_like=0
        )
        db_sess.add(post)
        db_sess.commit()
        return render_template('profile.html', title=current_user.nick, img=post.image)
    return render_template("add_post.html", title="AddPost", inf={"user_id": user_id})


# редактирование поста


@app.route("/user/<int:user_id>/post/red/<int:post_id>", methods=["GET", "POST"])
@login_required
def red_post(user_id, post_id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).get(post_id)
    if request.method == "POST":
        img_file = request.files['file']
        img = str(base64.b64encode(img_file.read()))[2:-1]
        if len(img) >= 10:
            post.image = img
        post.text = request.form["text"]
        db_sess.commit()
        return render_template('profile.html', title=current_user.nick, img=post.image)
    d = {"text": post.text, "image": post.image, "post_id": post_id}
    return render_template("red_post.html", title="RedPost", values=d)


# удаление поста


@app.route("/user/<int:user_id>/post/del/<int:post_id>", methods=["GET", "POST"])
@login_required
def del_post(user_id, post_id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).get(post_id)
    db_sess.delete(post)
    db_sess.commit()
    return render_template("base.html", title="RedPost")


@app.route("/pictures_of_the_day")
def pictures_of_the_day():
    return "pictures_of_the_day"


# фотки с Марса


@app.route("/img_of_mars", methods=["GET", "POST"])
def images_of_mars():
    nasa_interfese = NasaInterfese()
    form = DateForm()
    print(form.data)
    if form.validate_on_submit():
        str_date = str(form.date.data).split()[0]
    else:
        day_min_3 = datetime.date.today() - datetime.timedelta(days=3)
        str_date = str(day_min_3).split()[0]
    d = nasa_interfese.get_mars_img(earth_date=str_date)
    return render_template("img_of_mars.html", str_date=str_date, form=form, cam=list(d.keys()), title="ImagesOfMars",
                           d=d, len=len)


@app.route("/missions")
def missions():
    return "missions"


@app.route("/exoplanets")
def exoplanets():
    return "exoplanets"


# вход


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.nick == form.nick.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Incorrect login or password",
                               form=form)
    return render_template('login.html', title='Log in', form=form)


# регистрация


@app.route("/registration", methods=["GET", "POST"])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registration.html', title='Registration',
                                   form=form,
                                   message="Passwords don't match")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.nick == form.nick.data).first():
            return render_template('registration.html', title='Registration',
                                   form=form,
                                   message="There is already such a user")
        user = User(
            nick=form.nick.data,
            about=form.about.data,
            address=form.address.data,
            birthday=form.birthday.data
        )
        user.set_password(form.password.data)
        login_user(user, remember=False)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('registration.html', title='Registration', form=form)


# выход


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# чат между двумя пользователями
@app.route("/chat/<int:user_1_id>,<int:user_2_id>", methods=["GET", "POST"])
def chat(user_1_id, user_2_id):
    chat = get_chat(user_1_id, user_2_id)
    db_sess = db_session.create_session()
    if request.method == "POST":
        message = Message(
            id_of_chat=chat[1].id,
            id_of_user=current_user.id,
            n_of_message=len(chat[0]) + 1,
            text=request.form["text"]
        )
        db_sess.add(message)
        db_sess.commit()
        return redirect(f"/chat/{chat[1].id_of_user_1},{chat[1].id_of_user_2}")
    inf = {"user_1": db_sess.query(User).get(chat[1].id_of_user_1),
           "user_2": db_sess.query(User).get(chat[1].id_of_user_2)}
    return render_template("chat.html", messages=chat[0], inf=inf, title="Chat")


# функция для получения чата
def get_chat(user_1_id, user_2_id):
    db_sess = db_session.create_session()
    chats = db_sess.query(Chat).filter(((Chat.id_of_user_1 == user_1_id) | (Chat.id_of_user_1 == user_2_id)),
                                       ((Chat.id_of_user_2 == user_1_id) | (Chat.id_of_user_2 == user_2_id)))
    if len(list(chats)) > 0:
        chat = chats.first()
        messages_of_chat = db_sess.query(Message).filter(
            Message.id_of_chat == chat.id)
        list_of_messages = [(i.n_of_message, i.id_of_user, i.text)
                            for i in messages_of_chat]
        return list_of_messages, chat
    else:
        chat = Chat(
            id_of_user_1=user_1_id,
            id_of_user_2=user_2_id
        )
        db_sess.add(chat)
        db_sess.commit()
        return get_chat(user_1_id, user_2_id)


def like_of_post(id_of_user, id_of_post):
    db_sess = db_session.create_session()
    if len(list(db_sess.query(LikeOfPost).filter(
            LikeOfPost.id_of_user == id_of_user, LikeOfPost.id_of_post == id_of_post))) == 0:
        like = LikeOfPost(
            id_of_user=id_of_user,
            id_of_post=id_of_post
        )
        post = db_sess.query(Post).get(id_of_post)
        post.n_like += 1
        db_sess.add(like)
        db_sess.commit()


def like_of_comment(id_of_user, id_of_comment):
    db_sess = db_session.create_session()
    if len(list(db_sess.query(LikeOfComment).filter(
            LikeOfComment.id_of_user == id_of_user, LikeOfComment.id_of_comment == id_of_comment))) == 0:
        like = LikeOfComment(
            id_of_user=id_of_user,
            id_of_comment=id_of_comment
        )
        comment = db_sess.query(Comment).get(id_of_comment)
        comment.n_like += 1
        db_sess.add(like)
        db_sess.commit()


if __name__ == "__main__":
    db_session.global_init("db/blogs.db")
    session = db_session.create_session()
    api.add_resource(api_for_application.GetUsers, '/api/users')
    api.add_resource(api_for_application.GetUser, '/api/user/<int:user_id>')
    api.add_resource(api_for_application.GetPosts, '/api/posts')
    api.add_resource(api_for_application.GetPost, '/api/post/<int:post_id>')
    api.add_resource(api_for_application.GetComments, '/api/comments')
    api.add_resource(api_for_application.GetComment, '/api/comment/<int:comment_id>')
    api.add_resource(api_for_application.GetMessages, '/api/messages')
    api.add_resource(api_for_application.GetMessage, '/api/message/<int:message_id>')
    app.run(port=8080, host="127.0.0.1", debug=True)
