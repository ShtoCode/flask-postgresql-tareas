import os
from flask import (
 Flask, flash, g, redirect, render_template, request, url_for, session
)
import functools
from werkzeug.security import check_password_hash, generate_password_hash
import db
from db import get_db
from werkzeug.exceptions import abort

app = Flask(__name__, static_url_path='/static')

app.config.from_mapping(
    SECRET_KEY="mikey",
    DATABASE_HOST=os.environ.get("FLASK_DATABASE_HOST"),
    DATABASE_PASSWORD=os.environ.get("FLASK_DATABASE_PASSWORD"),
    DATABASE_USER=os.environ.get("FLASK_DATABASE_USER"),
    DATABASE=os.environ.get("FLASK_DATABASE"),
)


db.init_app(app)


@app.route('/registrar', methods = ['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db, c = get_db()
        error = None
        c.execute(
            "SELECT id FROM usuario WHERE username = %s", (username,)
        )
        if not username:
            error = 'Username es requerido'

        if not password:
            error = 'Password es requerido'
        elif c.fetchone() is not None:
            error = 'Usuario {} se encuentra registrado.'.format(username)

        if error is None:
            c.execute(
                'INSERT INTO usuario (username, password) VALUES (%s, %s)', (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('login'))
        flash(error)
    return render_template('auth/registrar.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] 
        db,c = get_db()
        error = None
        c.execute(
            "SELECT * FROM usuario WHERE username = %s", (username,)
        )
        user = c.fetchone()
        
        if user is None:
            error = 'Username y/o contraseña incorrecta'
        elif not check_password_hash(user['password'], password):
            error = 'Username y/o contraseña incorrecta'

        if error is None:
                session.clear()
                session['user_id'] = user['id']
                return redirect(url_for('index'))
        flash(error)
    
    return render_template("auth/login.html")

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db,c = get_db()
        c.execute(
            "SELECT * FROM usuario WHERE id= %s", (user_id,)
        )
        g.user = c.fetchone()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))  
        return view(**kwargs)
    return wrapped_view 

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



@app.route('/', methods=['POST', 'GET'])
@login_required
def index():
    db,c = get_db()
    c.execute(
        "SELECT t.id, t.description, u.username, t.completed, t.created_at FROM todo t JOIN usuario u ON created_by= u.id WHERE t.created_by=%s ORDER BY created_at DESC", (g.user['id'],)
    )
    tareas = c.fetchall()
    return render_template('todo/index.html', tareas=tareas)

@app.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    if request.method == 'POST':
        description = request.form['description']
        error = None

        if not description:
            error = 'Description is required.'
        
        if error is not None:
            flash(error)
        else:
            db,c = get_db()
            c.execute(
                "INSERT INTO todo (description, completed, created_by) VALUES (%s, %s, %s)", (description, False, g.user['id'])
            )
            db.commit()
            return redirect(url_for("index"))

    return render_template('todo/crear.html')


def get_todo(id):
    db,c = get_db()
    c.execute(
        'SELECT t.id, t.description, t.completed, t.created_by, t.created_at, u.username '
        'FROM todo t JOIN usuario u ON t.created_by=u.id WHERE t.id=%s', (id,)
    )

    todo = c.fetchone()
    if todo is None:
        abort(404, "The todo with id {0} not exist".format(id))

    return todo

@app.route('/<int:id>/actualizar', methods=['GET', 'POST'])
@login_required
def actualizar(id):
    todo = get_todo(id)
    if request.method == 'POST':
        description = request.form['description']
        completed = True if request.form.get('completed') == 'on' else False
        error = None
        if not description:
            error = "Description is required"
        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute(
                "UPDATE todo SET description= %s, completed =%s"
                " WHERE id=%s AND created_by=%s", (description, completed, id, g.user['id'])
            )
            db.commit()
            return redirect(url_for('index'))

    return render_template('todo/actualizar.html', todo=todo)

@app.route('/<int:id>/eliminar', methods=['GET', 'POST'])
@login_required
def eliminar(id):
        db, c = get_db()
        c.execute(
            "DELETE FROM todo WHERE id=%s AND created_by=%s", (id, g.user['id'])
        )
        db.commit()
        return redirect(url_for('index'))





