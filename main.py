# Import flask stuff
from flask import Flask, render_template, redirect, request, redirect, session
# import mysql module
from flaskext.mysql import MySQL
import bcrypt

# set up mysql later

mysql = MySQL()
app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'x'
app.config['MYSQL_DATABASE_PASSWORD'] = 'x'
#the name of the database we want to connect to at the DB server
app.config['MYSQL_DATABASE_DB'] = 'bawk'
#where the mysql server is at
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
#use the mysql objects method init_app and pass it the flask object
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
app.secret_key = 'hpiuadfnadf938498h087y3ry087yafhgbhfb8y08y08yqwer342134'

#create route
@app.route('/')
def index():
	return render_template('index.html')

@app.route('/register')
def register():
	if request.args.get('username'):
		return render_template('register.html',
			message = "That username is already taken.")
	else:
		return render_template('register.html')

@app.route('/register_submit', methods=['POST'])
def register_submit():
	# check to see if username is already take.  This means select statement.
	check_username_query = "select * from user where username = '%s'" % request.form['user_name']
	print check_username_query
	cursor.execute(check_username_query)
	check_username_result = cursor.fetchone()
	if check_username_result is None:
		# no match. insert
		real_name = request.form['name']
		username = request.form['user_name']
		email = request.form['email']
		password = request.form['password'].encode('utf-8')
		hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
		username_insert = "insert into user values (default, '"+real_name+"', '"+username+"', '"+hashed_password+"', '"+email+"')"
		cursor.execute(username_insert)
		conn.commit()
		return render_template('index.html')
	else:
		return redirect('/register?username=taken')
	print check_username_result
	return "done"
	# Second if it is take send them back to register page with a message
	# If it is take then insert user into MySQL


@app.route('/sign_in')
def sign_in():
	return render_template('sign_in.html')

@app.route('/sign_in_submit', methods = ['POST'])
def sign_in_submit():
	password = request.form['password'].encode('utf-8')
	hashed_password_from_mysql = "select password from user where username = '%s'" % request.form['username']
	cursor.execute(hashed_password_from_mysql)
	hashed_password = cursor.fetchone()
	# To check a hash against english:
	if hashed_password == None:
		return render_template("sign_in.html", message = "Wrong Username.")
	if bcrypt.checkpw(password, hashed_password[0].encode('utf-8')):
		session['username'] = request.form['username']
		return redirect('/')
	else:
		return render_template("sign_in.html", message = "Wrong Password.")

@app.route('/logout')
def logout():
	#nuke their session vars.  This will end the session which is what we use to let them into the portal
	session.clear()
	return redirect('/sign_in?message=LoggedOut')

		

if __name__ == "__main__":
	app.run(debug=True)