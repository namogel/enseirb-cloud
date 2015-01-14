import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash


# configuration
app = Flask(__name__)
app.config.update(dict(
    DATABASE='database.db',
    DEBUG=True,
    SECRET_KEY='1234',
    USERNAME='admin',
    PASSWORD='admin'
))


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.cli.command('initdb')
def initdb_command():
    init_db()
    print 'Initialized the database'

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

#####################################################################################


PROTOCOL = {
    'login': ['connect', 'create', 'update', 'delete'],
    'data': ['read', 'upload', 'download', 'update', 'delete'],
    }


def add_db_user(username, password, mail):
    db = get_db()
    db.execute('insert into users (username, password, mail) values (?, ?, ?)',
               [username, password, mail])
    db.commit()
    flash('New entry was successfully posted')

@app.route('/add_user', methods=['POST'])
def add_user():
    add_db_user(request.form['username'], request.form['password'], request.form['mail'])
    return redirect(url_for('home'))

@app.route('/delete_user', methods=['POST'])
def delete_user():
    db = get_db()
    db.execute('delete from users where id = ?', [request.form['id']])
    db.commit()
    return redirect(url_for('home'))

@app.route('/search_user', methods=['POST'])
def search_user():
    users = get_db_users(request.form['username'], request.form['mail'])
    return render_template('index.html', users=users)

def get_db_users(username, mail):
    db = get_db()
    if username != '' or mail != '':
        cur = db.execute('select * from users where username = ? or mail = ?',
            [username, mail])
    else:
        cur = db.execute('select * from users')
    users = cur.fetchall()
    return users

@app.route('/', methods=['GET'])
def home():
    db = get_db()
    cur = db.execute('select * from users')
    users = cur.fetchall()
    return render_template('index.html', users=users)

def is_request_valid(type, form):
    try:
        request_option = form['option']
        options = PROTOCOL['login']
        if not request_option in options:
            raise KeyError
    except KeyError:
        return False
    return True

@app.route('/login', methods=['POST'])
def login():
    if not is_request_valid('login', request.form):
        return "invalid protocol"

    username = request.form['username']
    password = request.form['password']

    if request.form['option'] == 'connect':
        user = get_db_users(username, '')
        if user == []:
            return 'invalid_username'
        if password != user[0][2]:
            return 'invalid_password'
        return "ok"

    if request.form['option'] == 'create':
        user = get_db_users(username, '')
        if user != []:
            return 'username_busy'
        mail = request.form['mail']
        user = get_db_users('', mail)
        if user != []:
            return 'mail_busy'
        add_db_user(username, password, mail)
        return 'ok'

@app.route('/login/data', methods=['GET'])
def login_data():
    try:
        mode = request.args['mode']
        if mode == 'single':
            data = request.args['data']
        elif mode == 'all':
            data = '*'
        else:
            raise KeyError
        field = request.args['field']
        value = request.args['value']
    except KeyError:
        abort(404)

    db = get_db()
    cur = db.execute('select {} from users where {} = ?'.format(data, field), [value])
    user = cur.fetchall()
    if user == []:
        return "err"
    if mode == 'single':
        return "{}".format(user[0][0])
    return "id={}&username={}&mail={}".format(user[0][0], user[0][1], user[0][3])

@app.route('/tree', methods=['GET'])
def update_tree():
    try:
        mode = request.args['mode']
        dragged_id = request.args.get('field[dragged_file_id]')
        dropped_id = request.args.get('field[dropped_file_id]')
        # print field
        if mode == 'in':
            # DEBUG 
            print 'Putting '+dragged_id+' inside folder ' +dropped_id  
            print "tree updated"
            return "ok"
        elif mode == 'swap':
            # DEBUG 
            print 'Swapping '+dragged_id+' and ' +dropped_id  
            print "tree updated"
            return "ok"
        else:
            raise KeyError
    except KeyError:
        abort(404)
    return "err"

if __name__ == '__main__':
    app.run('0.0.0.0', 8080)
