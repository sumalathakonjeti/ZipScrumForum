from flask import *
from flask_login import LoginManager, current_user, login_user, logout_user  # UPDATED
from flask_login.utils import login_required  # UPDATED
from flask_login.login_manager import LoginManager  # UPDATED
import datetime

from sqlalchemy.orm.session import sessionmaker

from messaging import *
import config
import os
from setup import *
import setup
from flask_wtf.form import FlaskForm
from wtforms.fields.core import StringField
from wtforms.fields.simple import SubmitField
from sqlalchemy import or_, join, create_engine, engine
from forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm
from flask_mail import Message as fm
from werkzeug.security import generate_password_hash, check_password_hash
from database import *
from app import app, mail

# SETUP
app.config.from_object(config)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.init_app(app)


# DATABASE STUFF
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# VIEWS
def load_user(userid):
    return User.query.get(userid)


@app.route('/')
def index():
    subforums = Subforum.query.filter(Subforum.parent_id == None).order_by(Subforum.id)
    return render_template("subforums.html", subforums=subforums)


@app.route('/subforum')
def subforum():

    subforum_id = int(request.args.get("sub"))
    subforum = Subforum.query.filter(Subforum.id == subforum_id).first()
    if not subforum:
        return error("That subforum does not exist!")
    posts = Post.query.filter(Post.subforum_id == subforum_id).order_by(Post.id.desc()).limit(50)
    if not subforum.path:
        subforum.path = generateLinkPath(subforum.id)
    subforums = Subforum.query.filter(Subforum.parent_id == subforum_id).all()
    if subforum.id == 7:
        return render_template("links.html",subforum=subforum, posts=posts, subforums=subforums, path=subforum.path)
    return render_template("subforum.html", subforum=subforum, posts=posts, subforums=subforums, path=subforum.path)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data) and user.login_attempts < 3:
            user.login_attempts = 0
            db.session.commit()
            login_user(user, remember=form.remember.data)
            return redirect(url_for('index'))
        else:
            if user:
                user.login_attempts = user.login_attempts + 1
                db.session.commit()
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)


@app.route('/addpost')
@login_required
def addpost():
    subforum_id = int(request.args.get("sub"))
    subforum = Subforum.query.filter(Subforum.id == subforum_id).first()
    if not subforum:
        return error("That subforum does not exist!")

    return render_template("createpost.html", subforum=subforum)


@app.route('/viewpost')
def viewpost():
    postid = int(request.args.get("post"))
    post = Post.query.filter(Post.id == postid).first()
    if not post:
        return error("That post does not exist!")
    if not post.subforum.path:
        subforum.path = generateLinkPath(post.subforum.id)
    comments = Comment.query.filter(Comment.post_id == postid).order_by(
        Comment.id.desc())  # no need for scalability now
    return render_template("viewpost.html", post=post, path=subforum.path, comments=comments)


@app.route('/tags')
def tag_display():
    fav_post = []
    tags = Tags.query.filter(Tags.user_id == current_user.id).order_by(Tags.tag_id.desc()).limit(10)
    for tag in tags:
        if tag.type == 'favorite':
            fav_post.append(tag.post_info)
    posts_fav = Post.query.filter(Post.id.in_(fav_post))
    return render_template("favourites.html", user=current_user, posts_f=posts_fav)


@login_required
@app.route('/action_comment', methods=['POST', 'GET'])
def comment():
    post_id = int(request.args.get("post"))
    post = Post.query.filter(Post.id == post_id).first()
    if not post:
        return error("That post does not exist!")
    content = request.form['content']
    postdate = datetime.datetime.now()
    comment = Comment(content, postdate)
    current_user.comments.append(comment)
    post.comments.append(comment)
    db.session.commit()
    return redirect("/viewpost?post=" + str(post_id))


@login_required
@app.route('/action_post', methods=['POST'])
def action_post():
    subforum_id = int(request.args.get("sub"))
    subforum = Subforum.query.filter(Subforum.id == subforum_id).first()
    if not subforum:
        return redirect(url_for("subforums"))

    user = current_user
    title = request.form['title']
    content = request.form['content']
    # check for valid posting
    errors = []
    retry = False
    if not valid_title(title):
        errors.append("Title must be between 4 and 140 characters long!")
        retry = True
    if not valid_content(content):
        errors.append("Post must be between 10 and 5000 characters long!")
        retry = True
    if retry:
        return render_template("createpost.html", subforum=subforum, errors=errors)
    post = Post(title, content, datetime.datetime.now())
    subforum.posts.append(post)
    user.posts.append(post)
    db.session.commit()
    return redirect("/viewpost?post=" + str(post.id))


@login_required
@app.route('/action_logout')
def action_logout():
    # todo
    logout_user()
    return redirect("/")


@login_required
@app.route('/action_tag', methods=['GET', 'POST'])
def action_tag():
    post_id = int(request.args.get("post"))
    user_now = current_user
    post = Post.query.filter(Post.id == post_id).first()
    if not post:
        return error("That post does not exist!")
    type = 'favorite'
    fav = Tags.query.filter(Tags.user_id == user_now.id, Tags.post_info == post_id).first()
    if not fav:
        tag = Tags(type, post_id)
        user_now.tags.append(tag)
        db.session.commit()
    return redirect("/tags")

@login_required
@app.route('/action_tag_del', methods=['GET', 'POST'])
def action_tag_del():
    post_id = int(request.args.get("post2"))
    user_now = current_user
    fav = Tags.query.filter(Tags.user_id == user_now.id, Tags.post_info == post_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
    return redirect("/tags")

def error(errormessage):
    return "<b style=\"color: red;\">" + errormessage + "</b>"


def generateLinkPath(subforumid):
    links = []
    subforum = Subforum.query.filter(Subforum.id == subforumid).first()
    parent = Subforum.query.filter(Subforum.id == subforum.parent_id).first()
    links.append("<a href=\"/subforum?sub=" + str(subforum.id) + "\">" + subforum.title + "</a>")
    while parent is not None:
        links.append("<a href=\"/subforum?sub=" + str(parent.id) + "\">" + parent.title + "</a>")
        parent = Subforum.query.filter(Subforum.id == parent.parent_id).first()
    links.append("<a href=\"/\">Forum Index</a>")
    link = ""
    for l in reversed(links):
        link = link + " / " + l
    return link


# messqging

@login_required
@app.route('/send', methods=['GET', 'POST'])
def send_message():
    """allow to send a message"""
    global messages
    if request.method == 'POST':
        m = request.form['text'].strip()
        sender = request.form['sender'].strip()
        _msg = add_message(sender, m)
        print(type(_msg))
        db.session.commit()
        return redirect(url_for('show_messages'))
    else:
        return render_template('layout.html')


@login_required
@app.route('/show')
def show_messages():
    """show all messages"""
    messages = Message.query.filter(Message.sender == current_user.username).order_by(
        Message.id.desc())
    # print(messages)
    return render_template('messages.html', messages=messages)


@app.route('/action_link', methods=['POST','GET'])
def action_link():
    # user_id = int(request.args.get("user"))
    if request.method == 'GET':
        languages_input = request.args.get('Language')
        lang = Languages.query.filter(Languages.type == languages_input)
        if lang.first():
            return render_template('show_links.html', languages=lang, language_input=languages_input)
        else:
            errors = []
            errors.append("No links found")
            return render_template("show_links.html", errors=errors)

            # return redirect("/", lang)


    # return redirect("/",lang)


@app.route('/action_addlink',methods=['POST','GET'])
def action_addlink():
    # user_id = User.get_id()
    user = current_user
    type = request.form['language']
    link = request.form['link']
    errors = []
    retry = False
    if link_taken(link):
        errors.append("link is already taken!")
        retry = True
    if retry:
        return render_template("links.html", errors=errors)
    languages = Languages(type, link)
    # db.session.add(languages)
    # db.session.commit()
    # return redirect("/")

    # language = Languages(type,links)
    user.languages.append(languages)
    db.session.commit()
    # message =
    # return redirect("/")
    return render_template('links.html',message='Link created successfully')

def generateLinkPath(subforumid):
    links = []
    subforum = Subforum.query.filter(Subforum.id == subforumid).first()
    parent = Subforum.query.filter(Subforum.id == subforum.parent_id).first()
    links.append("<a href=\"/subforum?sub=" + str(subforum.id) + "\">" + subforum.title + "</a>")
    while parent is not None:
        links.append("<a href=\"/subforum?sub=" + str(parent.id) + "\">" + parent.title + "</a>")
        parent = Subforum.query.filter(Subforum.id == parent.parent_id).first()
    links.append("<a href=\"/\">Forum Index</a>")
    link = ""
    for l in reversed(links):
        link = link + " / " + l
    return link


messages = []  # list of Message(s)


@login_required
@app.route('/add_message', methods=['POST', 'GET'])
def add_message(sender, m):
    global messages
    if m:
        msg = Message(sender, m, datetime.datetime.now())
        print(msg)
        messages.append(msg)
        if len(messages) > MAX_MESSAGES:
            messages = messages[-MAX_MESSAGES:]
        current_user.message.append(msg)
        db.session.commit()
        return redirect("/")
        # return msg


def send_reset_email(user):
    token = user.get_reset_token()
    msg = fm('Password Reset Request', sender="Zipscrum@zipcode.com", recipients=[user.email])
    msg.body = f'''To reset your password please click the following link:
{url_for('reset_token', token=token, _external=True)}	

If you did not make this request please ignore this email.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password 1', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_token(token)
    print(user)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password_hash = generate_password_hash(form.password.data)
        user.login_attempts = 0
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password 2', form=form)

@app.route('/admin')
@login_required
def admin():
	form = UpdateAccount()
	# username = request.form['username']
	# email = request.form['email']
	# current_user.username = username
	return render_template('admin.html')

@app.route('/action_update', methods=['POST'])
def action_update():
	username = request.form['username']
	email = request.form['email']
	current_user.username = username
	current_user.email = email
	db.session.commit()
	flash('Your account has been updated', 'success')
	return redirect("/")

@app.route('/update_post', methods=['POST'])
def update_post():
	post_id = int(request.args.get("post"))
	post = Post.query.filter(Post.id == post_id).first()
	return render_template("update_post.html", post=post)

@app.route('/action_posted', methods=['POST', 'GET'])
def action_posted():
	post_id = request.form['post_id']
	title = request.form['title']
	content = request.form['content']
	post = Post.query.filter(Post.id == post_id).first()
	post.title = title
	post.content = content
	db.session.commit()
	return redirect("/")

@app.route('/action_delete', methods=['POST', 'GET'])
def action_delete():
	post_id = int(request.args.get("post"))
	Post.query.filter(Post.id == post_id).delete()
	db.session.commit()
	return redirect("/")


db.create_all()
if not Subforum.query.all():
    init_site()


@app.route('/search', methods=['POST', 'GET'])
def search():
    search = SearchForm(request.form)
    if request.method == "POST":
        return search_results(search)

    return render_template('search.html', form=search)


@app.route('/results')
def search_results(search):
    post = search.data['search']
    post = Post.query.outerjoin(Post.comments).filter(or_(Post.title.ilike(f'%{post}%'),
                                                          Post.content.ilike(f'%{post}%'),
                                                          Comment.content.ilike(f'%{post}%')))
    return render_template("results.html", form=post)


class SearchForm(FlaskForm):
    search = StringField('Search')
    submit = SubmitField('Submit')


if __name__ == "__main__":
    # setup.setup()
    # port = int(os.environ["PORT"])
    app.run(debug=True)
