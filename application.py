# APPlICATION FILE FOR 3155 PROJECT

import os  # os is used to get environment variables IP & PORT
from flask import Flask, redirect, url_for  # Flask is the web app that we will customize
from flask import render_template
from flask import request
from database import db


app = Flask(__name__)  # create an app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_project_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

db.init_app(app) # initializes database


with app.app_context():
    db.create_all()

@app.route('/')
@app.route('/index')
def index():
    # to be implemented
    # check if a user is saved in session
    if session.get('user'):
        return render_template("index.html", user=session['user'])
    return render_template("index.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    # to be implemented
    login_form = LoginForm()
    # validate_on_submit only validates using POST
    if login_form.validate_on_submit():
        # we know user exists. We can use one()
        the_user = db.session.query(User).filter_by(email=request.form['email']).one()
        # user exists check password entered matches stored password
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), the_user.password):
            # password match add user info to session
            session['user'] = the_user.first_name
            session['user_id'] = the_user.id
            # render view
            return redirect(url_for('get_events'))

        # password check failed
        # set error message to alert user
        login_form.password.errors = ["Incorrect username or password."]
        return render_template("login.html", form=login_form)
    else:
        # form did not validate or GET request
        return render_template("login.html", form=login_form)

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if request.method == 'POST' and form.validate_on_submit():
        # salt and hash password
        h_password = bcrypt.hashpw(
            request.form['password'].encode('utf-8'), bcrypt.gensalt())
        # get entered user data
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        # create user model
        new_user = User(first_name, last_name, request.form['email'], h_password)
        # add user to database and commit
        db.session.add(new_user)
        db.session.commit()
        # save the user's name to the session
        session['user'] = first_name
        session['user_id'] = new_user.id  # access id value from user model of this newly added user
        # show user dashboard view
        return redirect(url_for('get_events'))

    # something went wrong - display register view
    return render_template('register.html', form=form)

@app.route('/events')
def get_events():
    # check if a user is saved in session
    if session.get('user'):
        # retrieve events from database
        my_events = db.session.query(Event).filter_by(user_id=session['user_id']).all()

        return render_template('events.html', events=my_events, user=session['user'])
    else:
        return redirect(url_for('login'))

@app.route('/events/<event_id>')
def get_event(event_id):
    # check if a user is saved in session
    if session.get('user'):
        # retrieve event from database
        my_event = db.session.query(Event).filter_by(id=event_id, user_id=session['user_id']).one()

        # create a comment form object
        form = CommentForm()

        return render_template('event.html', event=my_event, user=session['user'], form=form)
    else:
        return redirect(url_for('login'))

@app.route('/events/new', methods=['GET', 'POST'])
def new_event():
    # check if a user is saved in session
    if session.get('user'):
        # check method used for request
        if request.method == 'POST':
            # get title data
            title = request.form['title']
            # get note data
            text = request.form['noteText']
            # create date stamp
            from datetime import date
            today = date.today()
            # format date mm/dd/yyyy
            today = today.strftime("%m-%d-%Y")
            new_record = Event(title, text, today, session['user_id'])
            db.session.add(new_record)
            db.session.commit()

            return redirect(url_for('get_events'))
        else:
            # GET request - show new note form
            return render_template('new.html', user=session['user'])
    else:
        # user is not in session redirect to login
        return redirect(url_for('login'))

@app.route('/events/edit/<event_id>', methods=['GET', 'POST'])
def update_event(event_id):
    # check if a user is saved in session
    if session.get('user'):
        # check method used for request
        if request.method == 'POST':
            # get title data
            title = request.form['title']
            # get event data
            text = request.form['eventText']
            event = db.session.query(Event).filter_by(id=event_id).one()
            # update note data
            event.title = title
            event.text = text
            # update event in DB
            db.session.add(event)
            db.session.commit()
            return redirect(url_for('get_events'))
        else:
            # GET request - show new event form to edit event

            # retrieve event from database
            my_event = db.session.query(Note).filter_by(id=note_id).one()

            return render_template('new.html', event=my_event, user=session['user'])
    else:
        # user is not in session redirect to login
        return redirect(url_for('login'))

@app.route('/events/delete/<event_id>', methods=['POST'])
def delete_event(event_id):
    # check if a user is saved in session
    if session.get('user'):
        # retrieve event from database
        my_event = db.session.query(Event).filter_by(id=event_id).one()

        db.session.delete(my_event)
        db.session.commit()

        return redirect(url_for('get_events'))
    else:
        # user is not in session redirect to login
        return redirect(url_for('login'))

app.run(host=os.getenv('IP', '127.0.0.1'), port=int(os.getenv('PORT', 5000)), debug=True)