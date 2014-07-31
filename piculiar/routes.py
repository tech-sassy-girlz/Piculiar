import os

from flask import session, redirect, url_for, escape, request, render_template
from piculiar import app 
from db import execute, query, fetch

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
			create_user_sql = "INSERT INTO users (name, email, pwd) VALUES (%s, %s, md5(%s));" 
			params = (name, email, pwd)

			execute(create_user_sql, params)

			select_new_user = "SELECT MAX(id) FROM users;"
			result = fetch(select_new_user)

			session["user_id"] = result[0] 
				
			return redirect(url_for("profile"))			
	else:
		# Show sign-up page
		return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		# Starting session for user
		email = request.form["username"]
		pwd = request.form["pwd"]
		
		if email != "" and pwd != "":
			sql = "SELECT id FROM users WHERE name LIKE %s AND pwd LIKE md5(%s) LIMIT 1;" 
			params = (email, pwd)
			result = fetch(sql, params) 

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
	select_user_sql = "SELECT name, email FROM users WHERE id=%s;"
	user_info = fetch(select_user_sql, session["user_id"]) # 0: name, 1: email
	
	if request.method == "POST":
		# Update user information
		name = request.form["username"]
		email = request.form["email"]
		
		if name != "" and email != "":
			# SELECT * FROM users WHERE email LIKE ? LIMIT 1
			update_user_sql = "UPDATE users SET name=%s, email=%s WHERE id=%s;"
			update_user_params = (name, email, session["user_id"])
			
			execute(update_user_sql, update_user_params)
			
			return redirect(url_for("profile"))
	elif request.method == "DELETE":
		# Delete user information (and images)
		# DELETE FROM images WHERE user_id=?;
		delete_user_sql = "DELETE FROM users WHERE id=%s;"
		
		execute(delete_user_sql, session["user_id"])

		session.pop("user_id", None)
		
		return redirect(url_for("signup"))
	else:
		# Show profile information
		return render_template("profile.html", name=user_info[0], email=user_info[1])

# i.e. www.picflick.com/profile/password
@app.route("/profile/password", methods=["POST"])
def password():
	if request.method == "POST":
		# Update user password
		pwd = request.form["pwd"]
		confirm_pwd = request.form["pwd_confirm"]
		
		if pwd != "" and pwd == confirm_pwd:
			sql = "UPDATE users SET pwd=md5(%s) WHERE id=%s;"
			params = (pwd, session["user_id"])
						
			execute(sql, params)
			
			return redirect(url_for("profile"))
		else:
			return render_template("profile.html")

def allowed_file(filename):
	allowed_extensions = set(["jpg", "jpeg", "png", "gif"])

	return '.' in filename and filename.rsplit('.', 1)[1] in allowed_extensions

# i.e. www.picflick.com/upload
@app.route("/upload", methods=["GET", "POST"])
def upload():
	if request.method == "POST":
		# Upload image to server
		file = request.files["image"]	
		if file and allowed_file(file.filename):
			sql = """INSERT INTO images (user_id, file_name, year_created, month_created) 
				VALUES (%s, %s, YEAR(NOW()), MONTHNAME(NOW()));"""		
			params = (session["user_id"], file.filename)
		
			execute(sql, params)

			select_new_image = "SELECT id, year_created, month_created FROM images WHERE user_id=%s ORDER BY id DESC LIMIT 1;"
			image_info = fetch(select_new_image, session["user_id"])
			
			upload_folder = app.config["UPLOAD_FOLDER"]
			year_folder = upload_folder + "/" + image_info[1]
			month_folder = year_folder + "/" + image_info[2]

			if not os.path.exists(year_folder):
				os.makedirs(year_folder)
			
			if not os.path.exists(month_folder):
				os.makedirs(month_folder)

			file.save(os.path.join(month_folder, file.filename))
		
			return redirect(url_for("gallery", user_id=session["user_id"]))

	return render_template("upload.html")

# i.e. www.picflick.com/gallery/5
@app.route("/gallery/<user_id>")
def gallery(user_id):
	select_user_sql = "SELECT name, email FROM users WHERE id=%s LIMIT 1;"
	user_info = fetch(select_user_sql, user_id)

	# Show image gallery
	select_images_sql = "SELECT id, file_name, year_created, month_created FROM images WHERE user_id=%s;"
	images = query(select_images_sql, user_id)
		
	return render_template("gallery.html", user_info=user_info, images=images)

# i.e. www.picflick.com/gallery/5/image/42
@app.route("/gallery/<user_id>/image/<image_id>", methods=["GET", "DELETE"])
def image(user_id, image_id):
	if request.method == "DELETE":
		# Delete an image
		sql = "DELETE FROM images WHERE id=%s;"

		execute(sql, image_id)

		return redirect(url_for("gallery"))
	else:
		# Show the specific image
		sql = "SELECT * FROM images WHERE user_id=%s;"
		images = query(sql, user_id)

		return render_template("show.html")

