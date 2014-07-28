import pymysql 
import unittest

class TestUserData(unittest.TestCase):
	def setUp(self):
		self.data = ("Pori", "porialex@gmail.com", "passwd")
		self.db = pymysql.connect(host="localhost", user="root", db="pic_flick_test", passwd="Password01") 
		self.c = self.db.cursor()

	def tearDown(self):
		self.db.close()

	def test_create_user(self):
		sql = "INSERT INTO users (name, email, pwd) VALUES (%s, %s, md5(%s));" 
		result = self.c.execute(sql, self.data)

		self.assertEqual(None, self.c.fetchone())	
	
	def test_select_user_from_log_in(self):
		sql = "SELECT id FROM users WHERE email LIKE %s AND pwd LIKE md5(%s) LIMIT 1;" 
		params = (self.data[1], self.data[2])
		result = self.c.execute(sql, params)

		self.assertEqual(1, self.c.fetchone())	

	def test_select_user(self):
		sql = "SELECT * FROM users WHERE id=%s;" 
		result = self.c.execute(sql, 1)

		self.assertEqual(1, self.c.fetchone())	

	def test_update_user(self):
		sql = "UPDATE users SET name=%s, email=%s WHERE id=%s;" 
		params = ("Alex", "alex@pori.io", 1)
		result = self.c.execute(sql, params)

		self.assertEqual(None, self.c.fetchone())	
	
	def test_update_user_password(self):
		sql = "UPDATE users SET pwd=md5(%s) WHERE id=%s;" 
		params = ("password", 1)
		result = self.c.execute(sql, params)

		self.assertEqual(None, self.c.fetchone())	
	
	def test_delete_user(self):
		sql = "DELETE FROM users WHERE id=%s;" 
		result = self.c.execute(sql, 1)

		self.assertEqual(None, self.c.fetchone())	

if __name__ == "__main__":
	unittest.main()
