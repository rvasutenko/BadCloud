from src.config import Config
import sqlite3

class DataBase:

    def __init__(self, db_file):
        self.connect = sqlite3.connect(db_file)
        self.cursor = self.connect.cursor()

    async def add_users(self, user_id, name):
        with self.connect:
            return self.cursor.execute("""INSERT INTO users (user_id, name, role) VALUES (?, ?, ?)""",
                                       [user_id, name, 'admin' if user_id == Config.admin_ids else 'user'])
# ___________________________________________________________________________
    async def update_label(self, label, user_id):
        with self.connect:
            return self.cursor.execute("""UPDATE users SET label=(?) WHERE user_id=(?)""",
                                       [label, user_id])

    async def get_payment_status(self, user_id):
        with self.connect:
            return self.cursor.execute("""SELECT bought, label FROM users WHERE user_id=(?)""",
                                       [user_id]).fetchall()

    async def update_payment_status(self, user_id):
        with self.connect:
            return self.cursor.execute("""UPDATE users SET bought=(?) WHERE user_id=(?)""",
                                       [True, user_id])
# ___________________________________________________________________________
    async def get_firm_name(self, firm_id):
        with self.connect:
            return self.cursor.execute("""SELECT firm_name FROM firms WHERE firm_id=(?)""", [firm_id]).fetchall()

    async def get_taste_name(self, taste_id):
        with self.connect:
            return self.cursor.execute("""SELECT taste_name FROM tastes WHERE taste_id=(?)""", [taste_id]).fetchall()
# ___________________________________________________________________________
    async def get_products(self, taste_id):
        with self.connect:
            return self.cursor.execute("""SELECT * FROM products WHERE taste_id=(?)""", [taste_id]).fetchall()

    async def get_user_product(self, product_id):
        with self.connect:
            return self.cursor.execute("""SELECT * FROM products WHERE product_id=(?)""", [product_id]).fetchall()

    async def get_cart(self, user_id):
        with self.connect:
            return self.cursor.execute("""SELECT * FROM cart WHERE user_id=(?)""", [user_id]).fetchall()

    async def add_to_cart(self, user_id, product_id, firm_name, name, price, product_name):
        with self.connect:
            return self.cursor.execute("""INSERT INTO cart (user_id, product_id, firm_name, name, count, price, product_name) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                       [user_id, product_id, firm_name, name, 1, price, product_name])

    async def add_inform(self, user_id, inform):
        with self.connect:
            return self.cursor.execute("""INSERT INTO informs (user_id, inform) VALUES (?, ?)""",
                                       [user_id, inform])

    async def get_inform(self, user_id):
        with self.connect:
            return self.cursor.execute("""SELECT * FROM informs WHERE user_id=(?)""", [user_id]).fetchall()

    async def empty_inform(self, user_id):
        with self.connect:
            return self.cursor.execute("""DELETE FROM informs WHERE user_id=(?)""", [user_id])

    async def empty_cart(self, user_id):
        with self.connect:
            return self.cursor.execute("""DELETE FROM cart WHERE user_id=(?)""", [user_id])
# ______________________________________
    async def get_categories(self):
        with self.connect:
            return self.cursor.execute("""SELECT * FROM categories""").fetchall()

    async def get_firms(self, category_id):
        with self.connect:
            return self.cursor.execute("""SELECT * FROM firms WHERE category_id=(?)""", [category_id]).fetchall()

    async def get_firm_id(self, taste_id):
        with self.connect:
            return self.cursor.execute("""SELECT * FROM tastes WHERE taste_id=(?)""", [taste_id]).fetchall()

    async def get_tastes(self, firm_id):
        with self.connect:
            return self.cursor.execute("""SELECT * FROM tastes WHERE firm_id=(?)""", [firm_id]).fetchall()

    async def get_count_in_cart(self, user_id, product_id):
        with self.connect:
            return self.cursor.execute("""SELECT count FROM cart WHERE user_id=(?) AND product_id=(?)""",
                                       [user_id, product_id]).fetchall()

    async def get_count_in_stock(self, product_id):
        with self.connect:
            return self.cursor.execute("""SELECT count FROM products WHERE product_id=(?)""",
                                       [product_id]).fetchall()

    async def remove_one_item(self, product_id, user_id):
        with self.connect:
            return self.cursor.execute("""DELETE FROM cart WHERE product_id=(?) AND user_id=(?)""",
                                       [product_id, user_id])

    async def change_count(self, count, product_id, user_id):
        with self.connect:
            return self.cursor.execute("""UPDATE cart SET count=(?) WHERE product_id=(?) AND user_id=(?)""",
                                       [count, product_id, user_id])
