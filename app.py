from flask import Flask, request, redirect, url_for, render_template, session,send_file
from flask_mysqldb import MySQL
import MySQLdb.cursors
import secrets

import io

app = Flask(__name__)

# Use a strong secret key
app.secret_key = secrets.token_hex(16)

# Database connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Harshal@2003'
app.config['MYSQL_DB'] = 'laptop_recomendation'
mysql = MySQL(app)



@app.route('/')
def main():
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM  data  where   MyUnKnownColumn<=20")
        rows = cur.fetchall()
        print(rows,len(rows))
        return render_template('index.html', rows=rows )
    except Exception as e:
        print(f"Error in main route: {e}")
        return "An error occurred while processing your request."


@app.route('/nextPage/<int:id>')
def nextPage(id):

     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     cur.execute(f"SELECT * FROM data  where MyUnKnownColumn={id}")
     rows=cur.fetchone()
     return render_template('nextPage.html', rows=rows )

@app.route('/user_nextPage/<int:id>')
def user_nextPage(id):
    if 'loggedin' in session:
     msg=""
     name=session['name']
     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     cur.execute(f"SELECT * FROM data  where MyUnKnownColumn={id}")
     rows=cur.fetchone()

     return render_template('user_nextPage.html', rows=rows ,name=name ,msg=msg)
    return redirect(url_for('login'))

@app.route('/image/<file_name>')
def display_image(file_name):
            print(file_name)
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute(f"SELECT image from combine_data where file_name= '{file_name}' ")
            result = cur.fetchone()

            if result:
                image_data = result['image']
                image_stream = io.BytesIO(image_data)
                return send_file(image_stream, mimetype='image/jpg')
            else:

               return "Image not found"


@app.route('/login' , methods=['GET' ,'POST'])
def login():
    msg = ''
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(f"SELECT * FROM register WHERE email = '{email}' AND password = '{password}';")
        user = cur.fetchone()
        if user:
            session['loggedin'] = True
            session['id'] = user['id']
            session['email'] = user['email']
            session['name'] = user['name']
            var = session['name']
            msg = f'Welcome { var}!!'
            cur.execute("SELECT * FROM  data  where   MyUnKnownColumn<=20")
            rows = cur.fetchall()

            return render_template('user.html', msg=msg, user=user , rows=rows)

        else:
            # unsuccessful login
            msg = 'Incorrect Username and password'
            return render_template('login.html', msg=msg)
    else:
        # display login form
        return render_template('login.html', msg=msg)



@app.route('/user'  )
def user():


     if 'loggedin' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM register WHERE id= %b AND name = %s ', (session['id'], session['name'],))
        user = cur.fetchone()
        msg=""
        cur.execute("SELECT * FROM  data  where   MyUnKnownColumn<=20")
        rows = cur.fetchall()
        print(rows, len(rows))
        return render_template('user.html', rows=rows,user=user,msg=msg)

     return redirect(url_for('login'))


@app.route('/logout')
def logout():
        msg=""
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('name', None)

        return redirect(url_for('login',msg=msg))


@app.route('/register' , methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        name = request.form['name']
        print(name)
        email = request.form['email']
        print(email)

        password = request.form['password']
        print(password)
        if ( name.isalpha()):
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute('INSERT INTO register VALUES (NULL, %s, %s, %s)', ( name, email, password, ) )
            #CREATE TABLE `laptop_recomendation`.`new_table` (`id` INT NOT NULL,`image` LONGBLOB NOT NULL,`name` VARCHAR(45) NOT NULL,`price` VARCHAR(45) NOT NULL,`file_name` VARCHAR(45) NOT NULL,PRIMARY KEY (`id`));
            cur.execute(
                f'CREATE TABLE {name} (`name` VARCHAR(100) NOT NULL,`price` INT NOT NULL,`file_name` VARCHAR(45) NOT NULL )')
            mysql.connection.commit()
            msg = 'Registered !! Sucessfully !!'
            return redirect(url_for('login',msg=msg))
        else:
            msg = 'Username Contain Only Alphabate'
            return render_template('register.html', msg=msg)

    else:
        return render_template('register.html', msg=msg)


@app.route('/search', methods=['POST'])
def search():
    try:
        brand = request.form['search']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(f"SELECT * FROM data WHERE  brand = '{brand}' ")
        rows = cur.fetchall()
        return render_template('index.html', rows=rows )
    except Exception as e:
        print(f"Error in search route: {e}")
        return "An error occurred while processing your request."

@app.route('/UserSearch', methods=['POST'])
def UserSearch():

    if 'loggedin' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM register WHERE id= %b AND name = %s ', (session['id'], session['name'],))
        user = cur.fetchone()
        msg = ""
        brand = request.form['search']
        cur.execute(f"SELECT * FROM data WHERE  brand = '{brand}' ")
        rows = cur.fetchall()
        return render_template('user.html', rows=rows,user=user,msg=msg )
    return redirect(url_for('login'))


@app.route("/cart")
def cart():
    if 'loggedin' in session:
        var=session['name']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM {var}")
        rows = cursor.fetchall()
        return render_template('cart.html', rows=rows ,var=var,msg=' ')
    return "error"

@app.route('/remove/<file_name>')
def remove(file_name):
    if 'loggedin' in session:
        var = session['name']
        print(var)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f" DELETE FROM {var}  WHERE file_name='{file_name}' ")
        mysql.connection.commit()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM {var}")
        rows = cursor.fetchall()
        return render_template('cart.html', rows=rows, var=var, msg=' ')


    return "error"



@app.route('/addToCart/<file2_name> ')
def addToCart(file2_name):
    if'loggedin' in session:

        var=session['name']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(f"SELECT * from combine_data where file_name= '{file2_name}' " )
        product = cur.fetchone()
        print(product)
        #INSERT INTO `laptop_recomendation`.`ram` (`name`, `price`, `file_name`) VALUES ('x', '45', 'jk')
        cur.execute(f"INSERT INTO {var} (`name`, `price`, `file_name`) VALUES ( %s, %s, %s)", (product['name'], product['price'],product['file_name'],))
        mysql.connection.commit()
        return redirect(url_for('cart',msg="Successfully .. Added into Cart .."))
    return redirect(url_for('user'))


# @app.route("/")
# def hello_world():
#     return render_template('index.html')