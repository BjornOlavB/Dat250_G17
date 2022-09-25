import re
from flask import render_template, flash, redirect, url_for, request,make_response
from app import app, query_db
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm
from datetime import datetime
import os
from werkzeug.security import generate_password_hash,check_password_hash
import time



# function that wraps the validate_on_submit() method of the form
# this function removes the validation of cs_token, which is fu
def my_validation(form_type):
    form_type.validate_on_submit() # whos validation errors
    errs = form_type.errors
    print(errs)
    if len(errs) == 0 or ("csrf_token" in errs and len(errs) == 1):
        return True
    else:
        return False


# this file contains all the different routes, and the logic for communicating with the database

# home page/login/registration
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = IndexForm()
    

    if form.login.is_submitted() and form.login.submit.data and my_validation(form.login):
        user = query_db('SELECT * FROM Users WHERE username=?;',form.login.username.data, one=True)
        # Could not find user
        if user == None:
            flash('Wrong username or password!')
            return render_template('index.html', title='Welcome', form=form)


        # Calculate the time left until the user can login again
        if user["login_timeout"] == None:
            time_left = 0
        else:
            lockout_date = user["login_timeout"]
            time_left = lockout_date - round(time.time())
            minutes = round(time_left//60)
            seconds = round(time_left%60)


        # Restore the login_attemps and login_timeout when the time is over
        if time_left <= 0 and user["login_timeout"] != None:
            query_db("""UPDATE Users 
                    SET login_attempts = 0, login_timeout = NULL
                    WHERE id = ?;""",user["id"], one=True)
            user = query_db('SELECT * FROM Users WHERE username=?;',user["username"], one=True)
        
        # redirect and flash that the user is locked out 
        elif time_left > 0:
            flash(f'{minutes} min {seconds} sec until you can login again!')
            #return redirect(url_for('index'))
            return render_template('index.html', title='Welcome', form=form)

        # User successfully logged in
        if check_password_hash(user['password'],  form.login.password.data):
            # Reset the login_attemps and login_timeout
            query_db("""UPDATE Users 
                    SET login_attempts = 0, login_timeout = NULL
                    WHERE id = ?;""",user["id"], one=True)

            res = make_response(redirect(url_for('stream', username=form.login.username.data)))
            res.set_cookie("username",form.login.username.data)
            return res


        # Logic for setting login_attempts and login_timeout
        elif not check_password_hash(user["Password"], form.login.password.data):
            
            if user["Login_attempts"] < 2:
                query_db('UPDATE Users SET login_attempts = login_attempts + 1 WHERE id = ?;',user["id"], one=True)
                flash('Wrong username or password!')

            elif user["Login_attempts"] == 2:
                lockout_time = 5 # minutes
                lockout_stamp = time.time() + lockout_time*60 # minutes
                flash(f'You have been locked out of your account for {lockout_time} minutes due to too many failed login attempts')
                query_db('UPDATE Users SET login_timeout = ? WHERE id = ?;',lockout_stamp,user["id"], one=True)
        #_________________________________

        else:
            flash('Unknown error')

    elif form.register.is_submitted() and form.register.submit.data and my_validation(form.register):
            user = query_db('SELECT * FROM Users WHERE username=?;',form.register.username.data,one=True)
            if user != None:
                flash('Username is already taken!')
            else:
                query_db(
                    """INSERT INTO Users (
                        username, 
                        first_name, 
                        last_name, 
                        password
                        ) 
                        VALUES(?,?,?,?);""",
                        form.register.username.data, 
                        form.register.first_name.data,
                        form.register.last_name.data, 
                        generate_password_hash(form.register.password.data,"sha256"))

                flash(f'account {form.register.username.data} was successfully created')
                return redirect(url_for('index'))
    return render_template('index.html', title='Welcome', form=form)

# content stream page
@app.route('/stream/<username>', methods=['GET', 'POST'])
def stream(username):
    form = PostForm()

    user = query_db('SELECT * FROM Users WHERE username=?;',username, one=True)

    # if the user is not logged in or doesn't exist, redirect to the login page
    coockieUsername = request.cookies.get("username")
    if coockieUsername != username:
        return redirect(url_for('index'))
    elif user == None:
        flash("User does not exist")
        return redirect(url_for('index'))


    if form.is_submitted() and form.submit.data and my_validation(form):

        # remove "\r" and "\n" and <"> from the content of the post escape the content
        content = form.content.data.replace("\n", "").replace("\r", "")

        if form.image.data:
            path = os.path.join(app.config['UPLOAD_PATH'], form.image.data.filename)
            form.image.data.save(path)
            query_db(
                """INSERT INTO Posts (
                    u_id, 
                    content, 
                    image,
                    creation_time
                    ) 
                    VALUES(?, ?, ?, ?);""",
                    user['id'], form.content.data, form.image.data.filename, datetime.now())
        
        elif form.content.data:
            query_db(
                """INSERT INTO Posts (
                    u_id, 
                    content, 
                    creation_time
                    ) 
                    VALUES(?,?,?);""",
                    user['id'], content, datetime.now())
        else:
            flash('You must enter some content or upload an image')

       
        return redirect(url_for('stream', username=username))
    
    posts = query_db("""SELECT p.*, u.*, (SELECT COUNT(*) 
                        FROM Comments 
                        WHERE p_id=p.id) AS cc 
                        FROM Posts AS p 
                        JOIN Users AS u ON u.id=p.u_id 
                        WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id=?) 
                        OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id=?) OR p.u_id=?
                        ORDER BY p.creation_time DESC;""",user['id'], user['id'], user['id'])
                        
    return render_template('stream.html', title='Stream', username=username, form=form, posts=posts)



# comment page for a given post and user.
@app.route('/comments/<username>/<int:p_id>', methods=['GET', 'POST'])
def comments(username, p_id):
    coockieUsername = request.cookies.get("username")
    if coockieUsername != username:
        return redirect(url_for("index"))
    form = CommentsForm()
    if form.is_submitted():
        user = query_db('SELECT * FROM Users WHERE username=?;', username,one=True)
        query_db('INSERT INTO Comments (p_id, u_id, comment, creation_time) VALUES(?,?,?,?);',p_id, user['id'], form.comment.data, datetime.now())

    post = query_db('SELECT * FROM Posts WHERE id=?;',p_id, one=True)
    all_comments = query_db("""SELECT DISTINCT * FROM Comments 
                            AS c JOIN Users AS u ON c.u_id=u.id 
                            WHERE c.p_id=? ORDER BY c.creation_time DESC;""",p_id)

    return render_template('comments.html', title='Comments', username=username, form=form, post=post, comments=all_comments)

# page for seeing and adding friends
@app.route('/friends/<username>', methods=['GET', 'POST'])
def friends(username):
    coockieUsername = request.cookies.get("username")
    if coockieUsername != username:
        return redirect(url_for("index"))
    form = FriendsForm()
    user = query_db('SELECT * FROM Users WHERE username=?;',username, one=True)
    if form.is_submitted():
        friend = query_db('SELECT * FROM Users WHERE username=?;',form.username.data, one=True)
        if friend is None:
            flash('User does not exist')
        else:
            query_db('INSERT INTO Friends (u_id, f_id) VALUES(?,?);',user['id'], friend['id'])
    
    all_friends = query_db("""SELECT * FROM Friends 
                            AS f JOIN Users as u ON f.f_id=u.id 
                            WHERE f.u_id=? AND f.f_id!=? ;""",user['id'], user['id'])
    return render_template('friends.html', title='Friends', username=username, friends=all_friends, form=form)

# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    coockieUsername = request.cookies.get("username")
    if coockieUsername != username:
        return redirect(url_for("index"))
    form = ProfileForm()
    if form.is_submitted():

        query_db("""UPDATE Users SET education=?, employment="?, music=?, 
                    movie=?, nationality=?, birthday=? WHERE username=? ;""",
                    form.education.data, form.employment.data, form.music.data, 
                    form.movie.data, form.nationality.data, form.birthday.data, username
                    )
        
        return redirect(url_for('profile', username=username))
    
    user = query_db('SELECT * FROM Users WHERE username=?;',username, one=True)
    return render_template('profile.html', title='profile', username=username, user=user, form=form)

@app.route('/logout')
def logout():
    res = make_response(redirect(url_for("index")))
    res.set_cookie("username","",expires=0)
    return res