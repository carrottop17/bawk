# Import flask stuff
from flask import Flask, render_template, redirect, request, session, jsonify
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
	current_posts_query = "SELECT buzzes.id, pid, post_content, date, username, SUM(vote_type) as total from buzzes left join user on buzzes.uid = user.id left join votes on votes.pid = buzzes.id group by buzzes.id, votes.pid, post_content, date, username order by date DESC"
	# vote_count_query = "SELECT pid, SUM(vote_type) from votes group by pid"
	cursor.execute(current_posts_query)
	current_posts_result = cursor.fetchall()
	return render_template('index.html',
		posts = current_posts_result
		)

@app.route('/process_vote', methods=['POST'])
def process_vote():
	# check to see has the user voted on this particular item
	pid = request.form['vid'] #the post they voted on.  THis came from jquery ajax
	vote_type = request.form['voteType']
	check_user_votes_query = "SELECT * FROM votes inner join user on user.id = votes.uid where user.username = '%s' and votes.pid ='%s'" % (session['username'], pid)
	cursor.execute(check_user_votes_query)
	check_user_votes_result = cursor.fetchone()
	# its possible we get none back because the user hasnt voted on this post_content
	if check_user_votes_result is None:
		insert_user_vote_query = "INSERT into votes (pid, uid, vote_type) values ('"+str(pid)+"', '"+str(session['id'])+"', '"+str(vote_type)+"')"
		cursor.execute(insert_user_vote_query)
		conn.commit()
		return jsonify("voteCounted")
	else:
		check_user_vote_direction_query = "SELECT * FROM votes INNER JOIN user ON user.id = votes.uid WHERE user.username = '%s' AND votes.pid = '%s' AND votes.vote_type = %s" % (session['username'], pid, vote_type)
		cursor.execute(check_user_vote_direction_query)
		check_user_vote_direction_result = cursor.fetchone()
		if check_user_vote_direction_result is None:
			# User has voted, but not this direction. Update
			update_user_vote_query = "UPDATE votes SET vote_type = %s WHERE uid = '%s' AND pid = '%s'" % (vote_type, session['id'], pid)
			cursor.execute(update_user_vote_query)
			conn.commit()
			get_new_total_query = "SELECT sum(vote_type) as vote_total from votes where pid = '%s' group by pid" % pid
			cursor.execute(get_new_total_query)
			get_new_total_result = cursor.fetchone()
			return jsonify({'message': "voteChanged", 'vote_total': int(get_new_total_result[0])})
		else:
			# User has already voted this directino on this post. No dice.
			return jsonify({'message': "alreadyVoted"})


# @app.route('/vote', methods=['POST'])
# def vote():
# 	update_current_vote = "UPDATE buzzes set current_vote = 'current_vote + 1' where id = 2"
# 	cursor.execute(update_current_vote)
# 	return redirect('/')


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
		session['username'] = request.form['user_name']
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
	hashed_password_from_mysql = "select password, id from user where username = '%s'" % request.form['username']
	cursor.execute(hashed_password_from_mysql)
	hashed_password = cursor.fetchone()
	# To check a hash against english:
	if hashed_password == None:
		return render_template("sign_in.html", message = "Wrong Username.")
	if bcrypt.checkpw(password, hashed_password[0].encode('utf-8')):
		session['username'] = request.form['username']
		session['id'] = hashed_password[1]
		return redirect('/')
	else:
		return render_template("sign_in.html", message = "Wrong Password.")

@app.route('/logout')
def logout():
	#nuke their session vars.  This will end the session which is what we use to let them into the portal
	session.clear()
	return redirect('/sign_in?message=LoggedOut')

@app.route('/post_submit', methods=['POST'])
def post_submit():
	post_content = request.form['post_content']
	get_user_id_query = "select id from user where username = '%s'" % session['username']
	cursor.execute(get_user_id_query)
	get_user_id_result = cursor.fetchone()
	user_id = get_user_id_result[0]
	insert_post_query = "insert into buzzes (post_content, uid, current_vote) values ('"+post_content+"', "+str(user_id)+", 0)"
	cursor.execute(insert_post_query)
	conn.commit()
	return redirect('/')

@app.route('/follow')
def follow():
	get_all_not_me_users_query = "SELECT * from users where id != '%s'" % session['id']
	# cursor.execute(get_all_not_me_users_query)
	# get_all_not_me_users_result = cursor.fetchall()
	# who user is following
	# we want username and id
	get_all_following_query = "SELECT u.username, f.uid_of_user_being_followed from follow f left join user u on u.id = f.uid_of_user_being_followed where f.uid_of_user_following = '%s'" % session['id']
	cursor.execute(get_all_following_query)
	get_all_following_result = cursor.fetchall()
	# all users in user table minus those user is following
	get_all_not_following_query = "SELECT id, username from user where id not in (select uid_of_user_being_followed from follow where uid_of_user_following = '%s') and id != '%s'" % (session['id'], session['id'])
	cursor.execute(get_all_not_following_query)
	get_all_not_following_result = cursor.fetchall()
	# get_all_following_query = "SELECT * from follow inner join user on follow.uid_of_user_following = '%s'" % session['id']
	return render_template ('follow.html')


		

if __name__ == "__main__":
	app.run(debug=True)