import pymysql 
import unittest

class TestImageData(unittest.TestCase):
	def setUp(self):
		self.db = pymysql.connect(host="localhost", user="root", db="pic_flick_test", passwd="Password01") 
		self.c = self.db.cursor()

	def tearDown(self):
		self.db.close()

	def test_create_image(self):
		sql = "INSERT INTO images (user_id, file_name, year_created, month_created) VALUES (%s, %s, YEAR(NOW()), MONTHNAME(NOW()));" 
		params = (1, "some_image.jpg")
		result = self.c.execute(sql, params)

		self.assertEqual(None, self.c.fetchone())	

	def test_select_gallery(self):
		sql = "SELECT * FROM images WHERE user_id=%s;" 
		result = self.c.execute(sql, 1)

		self.assertEqual(1, self.c.fetchone())

	def test_select_image(self):
		sql = "SELECT * FROM images WHERE id=%s LIMIT 1;" 
		result = self.c.execute(sql, 1)

		self.assertEqual(1, self.c.fetchone())

	def test_delete_image(self):
		sql = "DELETE FROM images WHERE id=%s;" 
		result = self.c.execute(sql, 1)

		self.assertEqual(None, self.c.fetchone())	

if __name__ == "__main__":
	unittest.main()
