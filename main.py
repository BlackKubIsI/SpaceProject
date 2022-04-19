from flask import Flask, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from flask_login import current_user, LoginManager, login_required, logout_user, login_user
from wtforms.validators import DataRequired
from wtforms import StringField, BooleanField, SubmitField, IntegerField
from wtforms import DateField, PasswordField, EmailField, TextAreaField, FileField
from flask_restful import reqparse, abort, Api, Resource
from werkzeug.utils import secure_filename
from urllib.parse import urlparse, urljoin
from urllib.request import urlopen

import nasapy
from nasapy import julian_date as jd
import base64
import sys
import datetime
from _data.user import User
from _data.post import Post
from _data.like_of_post import LikeOfPost
from _data.like_of_comment import LikeOfComment
from _data.comment import Comment
from _data.chat import Chat
from _data.message import Message
from _data import db_session
import api_for_application
from bs4 import BeautifulSoup
# from urllib3 import urlopen

app = Flask(__name__)
api = Api(app)
app.config["SECRET_KEY"] = "random_key"

login_manager = LoginManager()
login_manager.init_app(app)


def redirect_back(default='hello', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


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

    def get_julian_date(self, year, month, day):
        return jd(year=year, month=month, day=day)

    def get_asteroids_data(self):
        return self.nasa.get_asteroids()["near_earth_objects"]


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

# профиль пользователя


@app.route("/user/<int:user_id>", methods=["GET", "POST"])
@login_required
def user_profile(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    posts_ = db_sess.query(Post).filter(Post.user_id == user_id).all()
    local_posts = list()
    for post in posts_[::-1]:
        elem = dict()
        elem['post_id'] = post.id
        elem['post_description'] = post.text
        elem['post_photo'] = post.image
        elem['post_likes'] = post.n_like
        elem['post_date'] = post.date_of_post
        elem['isliked'] = True if db_sess.query(LikeOfPost).filter(
            (LikeOfPost.id_of_user == user_id) & (LikeOfPost.id_of_post == post.id)).first() else False

        local_posts.append(elem)
    if 'post_id' in request.args:
        like_of_post(user_id, int(request.args['post_id']))
        post_id = int(request.args['post_id'])
    posts = dict()
    posts['posts'] = local_posts
    return render_template("user_profile.html", title=f"{user.nick}", name=user.nick, about=user.about,
                           address=user.address, birthday=user.birthday, reg_date=user.registration_date, posts=posts,
                           user_id=user_id)

# комментарии к посту


@app.route("/user/<int:user_id>/post/<int:post_id>/all_comments", methods=["GET", "POST"])
@login_required
def all_comments(user_id, post_id):
    db_sess = db_session.create_session()
    post_ = db_sess.query(Post).filter(Post.id == post_id).first()
    post = dict()
    post['post_id'] = post_.id
    post['post_description'] = post_.text
    post['post_photo'] = post_.image
    post['post_likes'] = post_.n_like
    post['post_date'] = post_.date_of_post
    post['isliked'] = True if db_sess.query(LikeOfPost).filter(
        (LikeOfPost.id_of_user == user_id) & (LikeOfPost.id_of_post == post_.id)).first() else False
    all_comments = db_sess.query(Comment).filter(
        Comment.id_of_post == post_id).all()
    comms_ = list()
    for c in all_comments:
        elem = dict()
        elem['user_id'] = c.id_of_user
        elem['user_name'] = db_sess.query(User).filter(
            User.id == c.id_of_user).first().nick
        elem['text'] = c.text
        comms_.append(elem)
    comms = dict()
    comms['comms'] = comms_
    return render_template('comments_view.html', comms=comms, post=post, user_id=user_id)


@app.route('/upload/<int:user_id>', methods=["POST"])
def upload_file(user_id):
    f = request.files['file']
    with open("t.txt", mode="w", encoding="utf-8") as a:
        a.write(str(base64.b64encode(f.read())))
    print(base64.b64encode(f.read()))
    f.save(secure_filename(f.filename))
    return redirect("/")


# астероиды

@app.route("/asteroids", methods=["GET"])
def asteroids():
    data_asteroids = NasaInterfese().get_asteroids_data()
    img_links = []
    for g, elem in enumerate(data_asteroids):
        img_links.append([])
        html_doc = urlopen(f'https://yandex.ru/images/search?text=asteroid+{elem["name_limited"]}')
        soup = BeautifulSoup(html_doc)
        for img in soup.find_all('img')[:15]:
            if img.get('src') != "":
                img_links[g] += [img.get('src')]
    return render_template("asteroids.html", asteroids=data_asteroids, images_of_asteroids=img_links, title="Asteroids")


# главная


@app.route("/", methods=["GET", "POST"])
def main():
    db_sess = db_session.create_session()
    posts_ = db_sess.query(Post).all()
    local_posts = list()
    for post in posts_[::-1]:
        elem = dict()
        elem['user_name'] = db_sess.query(User).filter(User.id == post.user_id).first().nick
        elem['user_id'] = db_sess.query(User).filter(User.id == post.user_id).first().id
        elem['post_id'] = post.id
        elem['post_description'] = post.text
        elem['post_photo'] = post.image
        elem['post_likes'] = post.n_like
        elem['post_date'] = post.date_of_post
        # elem['isliked'] = True if db_sess.query(LikeOfPost).filter(
        #     (LikeOfPost.id_of_user == user_id) & (LikeOfPost.id_of_post == post.id)).first() else False
        local_posts.append(elem)
    # if 'post_id' in request.args:
    #     like_of_post(user_id, int(request.args['post_id']))
    #     post_id = int(request.args['post_id'])
    posts = dict()
    posts['posts'] = local_posts
    return render_template("main.html", title="News", posts=posts)


# добавление комментария

@app.route("/user/<int:user_id>/post/<int:post_id>/comment", methods=["GET", "POST"])
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
        return redirect(f'/user/{user_id}/post/{post_id}/all_comments')
    return render_template("add_comment.html", title="AddComment",
                           inf={"user_id": user_id, "post_id": post_id})


# редактирование комментария


@app.route("/user/<int:user_id>/post/<int:post_id>/comment/red/<int:comment_id>",
           methods=["GET", "POST"])
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


@app.route("/user/<int:user_id>/post/<int:post_id>/comment/del/<int:comment_id>",
           methods=["GET", "POST"])
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
        return redirect(f"/user/{current_user.id}")
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
    return render_template("img_of_mars.html", str_date=str_date, form=form, cam=list(d.keys()),
                           title="ImagesOfMars",
                           d=d, len=len)


# перевод дат в юлианский календарь
@app.route("/julian_translator", methods=["GET", "POST"])
def julian_translator():
    nasa_interfese = NasaInterfese()
    form = DateForm()
    date_today = str(datetime.date.today()).split('-')
    if form.validate_on_submit():
        str_date = str(form.date.data).split('-')
    else:
        str_date = date_today
    d_serched = nasa_interfese.get_julian_date(year=int(str_date[0]), month=int(str_date[1]), day=int(str_date[2]))
    d_today = nasa_interfese.get_julian_date(year=int(date_today[0]), month=int(date_today[1]), day=int(date_today[2]))
    return render_template('julian_translator.html', str_date=str_date, form=form, jd_date_searched=d_serched, jd_date_today=d_today, len=len)


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

# все чаты
@app.route("/messages/<int:user_id>", methods=["GET", "POST"])
@login_required
def messenger(user_id):
    db_sess = db_session.create_session()
    messages = db_sess.query(Chat).filter(Chat.id_of_user_1 == user_id).all()
    local_messages = list()
    for chat in messages:
        elem = dict()
        elem['user1_id'] = chat.id_of_user_1
        elem['user2_id'] = chat.id_of_user_2
        elem['user2_nick'] = db_sess.query(User).filter((User.id == chat.id_of_user_2 ) | (User.id == chat.id_of_user_1)).first().nick
        r = db_sess.query(Message).filter(
            Message.id_of_chat == chat.id).all()
        if not r:
            elem['user2_nick'] = ''
            elem['last_message'] = ""
            elem['last_message_writer'] = 'Nobody here..'
        else:
            r = r[-1]
            elem['last_message'] = r.text
            elem['last_message_writer'] = 'You' if r.id_of_user == user_id else elem['user2_nick']
        local_messages.append(elem)
    messages = dict()
    messages['messages'] = local_messages
    return render_template('messages_view.html', messages=messages)


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
    chats = db_sess.query(Chat).filter(
        ((Chat.id_of_user_1 == user_1_id) | (Chat.id_of_user_1 == user_2_id)),
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


@app.route("/user/<int:id_of_user>/post/add_like/<int:id_of_post>")
@login_required
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
    return redirect_back()


@app.route("/user/<int:id_of_user>/post/<int:id_of_post>/comment/add_like/<int:id_of_comment>")
@login_required
def like_of_comment(id_of_user, id_of_post, id_of_comment):
    db_sess = db_session.create_session()
    if len(list(db_sess.query(LikeOfComment).filter(
            LikeOfComment.id_of_user == id_of_user,
            LikeOfComment.id_of_comment == id_of_comment))) == 0:
        like = LikeOfComment(
            id_of_user=id_of_user,
            id_of_comment=id_of_comment
        )
        comment = db_sess.query(Comment).get(id_of_comment)
        comment.n_like += 1
        db_sess.add(like)
        db_sess.commit()
    return redirect_back()


if __name__ == "__main__":
    db_session.global_init("db/blogs.db")
    session = db_session.create_session()
    api.add_resource(api_for_application.GetUsers, '/api/users')
    api.add_resource(api_for_application.GetUser, '/api/user/<int:user_id>')
    api.add_resource(api_for_application.GetPosts, '/api/posts')
    api.add_resource(api_for_application.GetPost, '/api/post/<int:post_id>')
    api.add_resource(api_for_application.GetComments, '/api/comments')
    api.add_resource(api_for_application.GetComment,
                     '/api/comment/<int:comment_id>')
    api.add_resource(api_for_application.GetMessages, '/api/messages')
    api.add_resource(api_for_application.GetMessage,
                     '/api/message/<int:message_id>')
    app.run(port=8080, host="127.0.0.1", debug=True)
