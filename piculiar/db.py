import os
import json

from flask import g
from piculiar import app

def load_config():
	db_conf_json = json.load(open("database"))
	db_conf = db_conf_json["development"]

	if os.getenv("PICULIAR_ENV", "development") == "production":
		db_conf = db_conf_json["production"]
		
	app.config.update(db_conf)

load_config()

def connect_db():
	"""Connect to the local database"""
	# TODO: load database.json config
	db = pymysql.connect(host=app.config["host"], db=app.config["db"], user=app.config["user"], passwd=app.config["passwd"])
	return db

def init_db():
	# TODO: Initialize database schema
	pass

def get_db():
	"""Creates a new database if none exists and returns the connection"""
	if not hasattr(g, "mysql_db"):
		g.mysql_db = connect_db()
	return g.mysql_db

def execute(sql, params=None):
	"""Execute a non-query statement"""
	cursor = get_db().cursor()

	return cursor.execute(sql, params)

def query(sql, params=None):
	"""Get queried data"""
	cursor = get_db().cursor()
	cursor.execute(sql, params)

	return cursor.fetchall()

def fetch(sql, params=None):
	"""Gets one row of data"""
	cursor = get_db().cursor()
	cursor.execute(sql, params)

	return cursor.fetchone()

@app.teardown_appcontext
def close_db(err):
	if hasattr(g, "mysql_db"):
		g.mysql_db.close()

