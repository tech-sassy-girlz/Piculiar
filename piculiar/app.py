import pymysql

from flask import Flask, session, redirect, url_for, escape, request, render_template
app = Flask(__name__)
db = pymysql.connect(host="localhost", db="pic_flick", user="root", passwd="Password01")

app.secret_key = "C0d3_Camp_13_aw3s0m3!x"

@app.route("/")
def home():
	return redirect(url_for('login'))
	
@app.route("/signup", methods=["GET", "POST"])
def signup():
	if request.method == "POST":
		# Save user info to database
		name = request.form["username"]
		email = request.form["email"]
		pwd = request.form["pwd"]
		confirm_pwd = request.form["confirm_pwd"]
		
		if name != "" and email != "" and pwd != "" and pwd == confirm_pwd:
			# SELECT * FROM users WHERE email LIKE ? LIMIT 1
			# INSERT INTO users (name, email, pwd) VALUES (?, ?, md5(?));
			sql = "INSERT INTO users (name, email, pwd) VALUES (%s, %s, md5(%s));" 
			data = (name, email, pwd)
			cursor = db.cursor()

			cursor.execute(sql, data)

			select_new_user = "SELECT MAX(id) FROM users;"
			new_user_cursor = db.cursor()

			new_user_cursor.execute(select_new_user)

			result = new_user_cursor.fetchone()

			session["user_id"] = result[0] 
				
			return redirect(url_for("profile"))			
	else:
		# Show sign-up page
		return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		# Starting session for user
		email = request.form["email"]
		pwd = request.form["pwd"]
		
		if email != "" and pwd != "":
			# SELECT id FROM users WHERE email LIKE ? AND pwd LIKE md5(?) LIMIT 1;
			sql = "SELECT id FROM users WHERE email LIKE %s AND pwd LIKE md5(%s) LIMIT 1;" 
			params = (email, pwd)
			cursor = db.cursor()

			cursor.execute(sql, params)
			result = cursor.fetchone()
			session["user_id"] = result[0]

			return redirect(url_for("profile")) 
	else:
		# Show sign-up page
		return render_template("login.html")

@app.route("/logout", methods=["POST"])
def logout():
	if request.method == "POST":
		# Destroy user session
		session.pop("user_id", None)
		return redirect(url_for("login"))

@app.route("/profile", methods=["GET", "POST", "DELETE"])
def profile():
	# SELECT * FROM users WHERE id=?
	select_user_sql = "SELECT name, email FROM users WHERE id=%s"
	cursor = db.cursor()
	
	cursor.execute(select_user_sql, session["user_id"])
	
	user_info = cursor.fetchone() # 0: name, 1: email
	
	if request.method == "POST":
		# Update user information
		name = request.form["name"]
		email = request.form["email"]
		
		if name != "" and email != "":
			# SELECT * FROM users WHERE email LIKE ? LIMIT 1
			# UPDATE users SET name=?, email=? WHERE id=?;
			update_user_sql = "UPDATE users SET name=%s, email=%s WHERE id=%s;"
			update_user_params = (name, email, session["user_id"])
			update_cursor = db.cursor()
			
			update_cursor.execute(update_user_sql, update_user_params)
			
			return redirect(url_for("profile"))
	elif request.method == "DELETE":
		# Delete user information (and images)
		# DELETE FROM images WHERE user_id=?;
		# DELETE FROM users WHERE id=?;
		delete_user_sql = "DELETE FROM users WHERE id=%s;"
		delete_user_cursor = db.cursor()
		
		delete_user_cursor.execute(delete_user_sql, session["user_id"])
		session.pop("user_id", None)
		
		return redirect(url_for("signup"))
	else:
		# Show profile information
		return render_template("profile.html", name=user_info[1], email=user_info[2])

# i.e. www.picflick.com/profile/password
@app.route("/profile/password", methods=["POST"])
def password():
	if request.method == "POST":
		# Update user password
		pwd = request.form["pwd"]
		confirm_pwd = request.form["confirm_pwd"]
		
		if pwd != "" and pwd == confirm_pwd:
			# UPDATE users SET pwd=md5(?) WHERE id=?;
			sql = "UPDATE users SET pwd=md5(%s) WHERE id=%s;"
			params = (pwd, session["user_id"])
			cursor = db.cursor()
						
			cursor.execute(sql, params)
			
			return redirect(url_for("profile"))
		else:
			return render_template("profile.html")

# i.e. www.picflick.com/upload
@app.route("/upload", methods=["GET", "POST"])
def upload():
	if request.method == "POST":
		# Upload image to server
		# INSERT INTO images (user_id, file_name, month_created, year_created) VALUES (?, ?, ?, ?);
		file_name = None # TODO: upload file name
		sql = """INSERT INTO images (user_id, file_name, year_created, month_created) 
			VALUES (%s, %s, YEAR(NOW()), MONTHNAME(NOW()));"""		
		params = (session["user_id"], file_name)
		cursor = db.cursor()
		
		cursor.execute(sql, params)
		
		return redirect(url_for("gallery"))
	else:
		return render_template("upload.html")

# i.e. www.picflick.com/gallery/5
@app.route("/gallery/<user_id>")
def gallery(user_id):
	# Show image gallery
	# SELECT * FROM images WHERE user_id=?
	sql = "SELECT * FROM images WHERE user_id=%s;"
	cursor = db.cursor()
	
	cursor.execute(sql, user_id)
	
	images = cursor.fetchall()
	
	return render_template("gallery.html")

# i.e. www.picflick.com/gallery/5/image/42
@app.route("/gallery/<user_id>/image/<image_id>", methods=["GET", "DELETE"])
def image(user_id, image_id):
	if request.method == "DELETE":
		# Delete an image
		# DELETE FROM images WHERE id=?;
		sql = "DELETE FROM images WHERE id=%s;"
		cursor = db.cursor()

		cursor.execute(sql, image_id)

		return redirect(url_for("gallery"))
	else:
		# Show the specific image
		# SELECT * FROM images WHERE id=?
		sql = "SELECT * FROM images WHERE user_id=%s;"
		cursor = db.cursor()

		cursor.execute(sql, user_id)

		image = cursor.fetchone()

		return render_template("show.html")

if __name__ == "__main__":
	app.run(debug=True)
