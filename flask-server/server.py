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

################################################################################


PROTOCOL = {
    'login': ['connect', 'create', 'update', 'delete'],
    'data': ['read', 'upload', 'download', 'update', 'delete'],
    }


#------------------------------------------------------------------------------#
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
    files = get_db_files(users[0][0])
    return render_template('index.html', users=users, files=files)

def get_db_users(username='', mail=''):
    db = get_db()
    if username or mail:
        cur = db.execute('select * from users where username = ? or mail = ?',
            [username, mail])
    else:
        cur = db.execute('select * from users')
    users = cur.fetchall()
    return users
#------------------------------------------------------------------------------#

#------------------------------------------------------------------------------#
def add_db_file(id_usr, name, type, folder):
    db = get_db()
    db.execute('insert into files (id_usr, name, type, folder) \
        values (?, ?, ?, ?)', [id_usr, name, type, folder])
    db.commit()

def del_db_file(id_usr, id):
    db = get_db()
    db.execute('delete from files where id_usr = ? and id = ?', \
        [id_usr, id])
    db.commit()

@app.route('/search_file', methods=['POST'])
def search_file():
    users = get_db_users()
    files = get_db_files(request.form['id_usr'], name=request.form['name'])
    return render_template('index.html', users=users, files=files)

def get_db_files(id_usr, id=None, folder=-1, name=''):
    db = get_db()
    if id:
        cur = db.execute('select * from files where id_usr = ? and id = ?', \
            [id_usr, id])
    else:
        if name and folder != -1:
            cur = db.execute('select * from files where id_usr = ? and folder = ? \
                and name like ?', [id_usr, folder, '%{}%'.format(name)])
        elif folder != -1:
            cur = db.execute('select * from files where id_usr = ? and folder = ?',\
                [id_usr, folder])
        elif name:
            cur = db.execute('select * from files where id_usr = ? \
                and name like ?', [id_usr, '%{}%'.format(name)])
        else:
            cur = db.execute('select * from files where id_usr = ?', [id_usr])
    files = cur.fetchall()
    return files
#------------------------------------------------------------------------------#

@app.route('/', methods=['GET'])
def home():
    users = get_db_users()
    files = []
    for user in users:
        files += get_db_files(user[0])
    return render_template('index.html', users=users, files=files)

@app.route('/login/connect', methods=['POST'])
def login_connect():
    username = request.form['username']
    password = request.form['password']
    user = get_db_users(username, '')
    if not user:
        return 'invalid_username'
    if password != user[0][2]:
        return 'invalid_password'
    return "ok"

@app.route('/login/create', methods=['POST'])
def login_create():
    username = request.form['username']
    password = request.form['password']
    user = get_db_users(username, '')
    if user:
        return 'username_busy'
    mail = request.form['mail']
    user = get_db_users('', mail)
    if user:
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
    cur = db.execute('select {} from users where {} = ?'.format(data, field), \
        [value])
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

@app.route('/tree/update/new', methods=['POST'])
def new_folder():
    try:
        id_usr = request.form['id_usr']
        name = request.form['name']
        location = request.form['location']
        folder = get_db_files(id_usr, name=name, folder=location)
        if folder:
            raise KeyError
        add_db_file(id_usr, name, "folder", location)
        return "ok"
    except KeyError:
        return "err"
    
@app.route('/file/upload', methods=['POST'])
def upload_file():
    try:
        id_usr = request.form['id_usr']
        name = request.form['name']
        type_ = request.form['type']
        location = request.form['location']
        file_ = get_db_files(id_usr, name=name)
        if file_:
            raise KeyError
    except KeyError:
        return "err"
    add_db_file(id_usr, name, type_, location)
    return "ok"

@app.route('/file/delete', methods=['POST'])
def remove_file():
    try:
        id_usr = request.form['id_usr']
        id_file = request.form['id_file']
        file_ = get_db_files(id_usr, id=id_file)
        if not file_:
            raise KeyError
        del_db_file(id_usr, id_file)
    except KeyError:
        return "err"
    return "ok"

@app.route('/tree/show', methods=['GET'])
def show_tree():
    try:
        id_usr = request.args['id_usr']
        location = request.args['location']
        parent = get_db_files(id_usr, id=location)[0][4] if location != '0' else -1
        files = get_db_files(id_usr, folder=location)
        ids, names, types = "", "", ""
        for file in files:
            ids += str(file[0]) + ","
            names += file[2] + ","
            types += file[3] + ","
        return "names=" + names + "&types=" + types + "&ids=" + ids + \
            "&parent=" + str(parent)
    except KeyError:
        return "err"



if __name__ == '__main__':
    app.run('0.0.0.0', 8080)
