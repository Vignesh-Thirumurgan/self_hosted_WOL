from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from wakeonlan import send_magic_packet
from functools import wraps

app = Flask(__name__, template_folder='templates', static_url_path='/')
  
app.secret_key = 'your_secret_key'  # Set your secret key for session management

# MySQL configurations  
app.config['MYSQL_HOST'] = '10.18.10.45'
app.config['MYSQL_USER'] = 'WAKE'
app.config['MYSQL_PASSWORD'] = 'WAKE'
app.config['MYSQL_DB'] = 'WAKE'
app.config['MYSQL_CURSORCLASS']= 'DictCursor'   

mysql = MySQL(app)


def create_tables():
    cur = mysql.connection.cursor()
    # Create mac table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS mac (
            id INT NOT NULL AUTO_INCREMENT,
            tag VARCHAR(45) NOT NULL,
            sys_name VARCHAR(45) NOT NULL,
            mac VARCHAR(45) NOT NULL,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    ''')
    
    # Create users table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT NOT NULL AUTO_INCREMENT,
            username VARCHAR(45) NOT NULL,
            password VARCHAR(45) NOT NULL,
            PRIMARY KEY (id),
            UNIQUE KEY (username)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    ''')
    
    mysql.connection.commit()
    cur.close()



def user_exists():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) as count FROM users")
    count = cur.fetchone()['count']
    cur.close()
    return count > 0

def login_required(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args,**kwargs)
    return inner

@app.route("/logout")
def logout():
    session.pop('user',None)
    return redirect(url_for('login'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        # user1= cur.fetchall()
        cur.close()

        if user:
            session['user'] = username
            return redirect(url_for('tab'))
        else:
            return 'Error: Invalid email or password'
    
    return render_template('index.html')



@app.route('/', methods=['GET', 'POST'])
def index():
    if user_exists():
        return redirect(url_for('login'))
    

    else:
      if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login'))

    return render_template('register.html')



@app.route('/mac',methods=['GET','POST'])
@login_required
def mac():
    if request.method=='POST':
          mac = request.form['mac']
          mac_match= re.compile("^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")
          test = bool(re.match(mac_match,mac))
          if test:
             send_magic_packet(mac)
             return render_template('mac.html',response="sucess")
          else:
              return render_template('mac.html',response="error")
          
    return render_template('mac.html')

@app.route('/users')
def users():
    con=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    con.execute("SELECT * FROM users")
    users=con.fetchall()
    return render_template('users.html',users=users)

@app.route('/up_us/<int:id>', methods=['GET', 'POST'])
def up_us(id):
    con = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        con.execute("UPDATE users SET username = %s, password = %s WHERE id = %s", (username, password, id))
        mysql.connection.commit()
        con.close()
        return redirect(url_for('users'))
    
    elif request.method == 'GET':
        con.execute("SELECT * FROM users WHERE id = %s", (id,))
        users = con.fetchone()
        con.close()
        
        if users:
            return render_template('in_us.html', users=users)
        else:
            return "Record not found", 404


@app.route('/add_users',methods=['GET','POST'])
@login_required
def add_users():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']

        con=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        con.execute("INSERT users (username,password) VALUES (%s,%s)",(username,password))
        mysql.connection.commit()
        con.close()
        return redirect('/users')

    return render_template('add_user.html') 

@app.route('/del_user/<string:id>')
@login_required
def del_user(id):
    con = mysql.connection.cursor()
    con.execute("DELETE FROM users WHERE id = %s", (id,))
    mysql.connection.commit()
    con.close()
    return redirect(url_for('users')) 


@app.route('/insert',methods=['GET','POST'])
@login_required
def insert():
    if request.method=='POST':
        tag= request.form['tag']
        mac = request.form['mac']
        sysname = request.form['system']

        
        con=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        con.execute("INSERT mac (tag,sys_name,mac) VALUES (%s,%s,%s)",(tag,mac,sysname))
        mysql.connection.commit()
        con.close()
        return redirect('/tab')

    return render_template('insert.html')


@app.route('/tab')
@login_required
def tab():
      con=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      con.execute("SELECT * FROM mac")
      mac_dis = con.fetchall() 
      con.close()
      render_template('table.html', mac_dis=mac_dis)
      return render_template('table.html',mac_dis=mac_dis)


@app.route('/tes/<string:mac>')
@login_required
def tes(mac):
    if mac: 
          send_magic_packet(mac)
    return redirect('/tab')

@app.route('/update/<string:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    con = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        sys_name = request.form.get('system')
        mac_address = request.form.get('mac')
        tag = request.form.get('tag')
        con.execute("UPDATE mac SET sys_name = %s, mac = %s, Tag = %s WHERE id = %s", (sys_name, mac_address, tag, id))
        mysql.connection.commit()
        con.close()
        return redirect(url_for('tab'))
    
    elif request.method == 'GET':
        con.execute("SELECT * FROM mac WHERE id = %s", (id,))
        mac_record = con.fetchone()
        con.close()
        
        if mac_record:
            return render_template('update_form.html', mac=mac_record)
        else:
            return "Record not found", 404

@app.route('/delete/<string:id>')
@login_required
def delete(id):
    con = mysql.connection.cursor()
    con.execute("DELETE FROM mac WHERE id = %s", (id,))
    mysql.connection.commit()
    con.close()
    return redirect(url_for('tab'))




if __name__ == '__main__': 
    with app.app_context():  # Ensure we are in the Flask app context
        create_tables()
    app.run(host='0.0.0.0') 
