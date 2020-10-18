#!/usr/bin/python3
""" Starts a Flask CrossMe app """

from flask import Flask, render_template, request, json, url_for, redirect,flash, session
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user
import uuid
from models import storage
from models.user import User
from models.post import Post

app = Flask(__name__)

@app.errorhandler(404)
def resource_not_found(e):
    return  render_template('404.html'), 404




@app.route('/')
def home():
    if "email" in session:
        email = session['email']
        return render_template('home.html', cache_id=uuid.uuid4(), user=email)
    return render_template('index.html', cache_id=uuid.uuid4())


@app.route('/profile/<user_id>', strict_slashes=False)
def render_profile(user_id):
    """
    Render The profile page
    if user doesn't exist or invalid id redirect to home

    """
    try:
        uuid_obj = uuid.UUID(user_id, version=4)
    except ValueError:
        return redirect('/')
    user = storage.get(User, user_id)
    user_info = user.to_dict()
    all_user_post = storage.getlist_by_attr(Post, user_id)
    return render_template('profile.html',
                           cache_id=str(uuid.uuid4()),
                           user_info=user_info,
                           all_user_post=all_user_post)


@app.route('/me', strict_slashes=False)
def render_me():
    """
    Render The profile page
    User will be redirected by it id to his profile
    """
    if "email" in session:
        user_email = session['email']
        me_user = storage.getbyemail(User, user_email)
        user_id = me_user.id
        NEWURL = '/profile/' + user_id
        return redirect(NEWURL)
    else:
        redirect('/')



@app.route('/login',methods=['GET', 'POST'])
def logg():
    if request.method == 'POST':
        if request.form['email'] and request.form['password']:
            req_data = request.form.to_dict()
            users = storage.getbyemail(User, request.form['email'])
            if users is None:
                return render_template('index.html', cache_id=uuid.uuid4(), error="Invalid Details")
            a = users.as_dict()
            print(a)
            print(a.__class__.__name__)
            b = User().verify_password(req_data['password'], a["password"])
            if b:
                session['email'] = request.form['email']
                if a["fb_access_token"] or a["ig_access_token"]:
                    return render_template('home.html', cache_id=uuid.uuid4(), user=session['email'])
                else:
                    return render_template('steptwo.html', cache_id=uuid.uuid4(), user_info=session['email'])
            else:
                return render_template('index.html', cache_id=uuid.uuid4(), error="Invalid Details")
        else:
            return render_template('index.html', cache_id=uuid.uuid4(), error="Missing information")
    else:
        if session:
            storage.reload()
            user_info = storage.getbyemail(User, session['email']).as_dict_nopwd()
            if user_info["fb_access_token"] or user_info["ig_access_token"]:
                return render_template('home.html', cache_id=uuid.uuid4(), user=session['email'])
            else:
                return render_template('steptwo.html', cache_id=uuid.uuid4(), user_info=user_info)
        else:
            return render_template('index.html', cache_id=uuid.uuid4())

@app.route('/logout',methods=['GET', 'POST'])
def loggoo():
        session.pop('email', None)
        return render_template('index.html', cache_id=uuid.uuid4())

@app.route('/register',methods=['GET', 'POST'])
def signUp():
    """create  users"""
    if request.method == 'POST':
        f = request.form['full_name']
        e = request.form['email']
        p = request.form['password']
        if not e and not f and not p:
            return render_template('index.html', cache_id=uuid.uuid4(), error="Missing information")
        all_cls = storage.all(User)
        for value in all_cls.values():
            if (value.email == e):
                return render_template('index.html', cache_id=uuid.uuid4(), error="Already Registred")
        req_data = request.form.to_dict()
        new= User()
        for k , v in req_data.items():
            if k == "password":
                v = new.hashpwd(v)
            setattr(new, k, v)
        setattr(new, "user_avatar", '/web_front/static/images/default-user-image.png')
        new.auth= True
        session['email'] = request.form['email']
        new.save()
        my_user = storage.getbyemail(User, request.form['email'])
        return render_template('steptwo.html', cache_id=uuid.uuid4(), user_info= my_user)
    else:
        if session:
            storage.reload()
            user_info = storage.getbyemail(User, session['email']).as_dict_nopwd()
            if user_info["fb_access_token"] or user_info["ig_access_token"]:
                return render_template('home.html', cache_id=uuid.uuid4(), user=session['email'])
            else:
                return render_template('steptwo.html', cache_id=uuid.uuid4(), user_info=user_info)
        else:
            return render_template('index.html', cache_id=uuid.uuid4())


if __name__ == "__main__":
    app.secret_key = 'mycrossme'
    """ Main Function """
    app.run(host='0.0.0.0', port=5000, ssl_context=('./ssl/server.crt', './ssl/server.key'))
