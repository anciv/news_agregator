import sqlite3


class NewsCommands:
    def __init__(self):
        self.connection = sqlite3.connect('sqlite.db')
        self.cursor = self.connection.cursor()

    def get_news(self):
        with self.connection:
            return self.cursor.execute('SELECT title FROM news').fetchall()

    def check_news(self, site, title, url):
        with self.connection:
            res = self.cursor.execute('SELECT * FROM news WHERE (site, title, url) = (?, ?, ?)',
                                      (site, title, url,)).fetchall()
            return bool(len(res))

    def insert_news(self, site, title, date, url):
        with self.connection:
            return self.cursor.execute('INSERT INTO news (site, title, date, url) VALUES(?,?,?,?)',
                                       (site, title, date, url,))

    def delete_news(self, title):
        with self.connection:
            return self.cursor.execute('DELETE FROM `news` WHERE (title) = (?)',
                                       (title,))


class UserCommands:
    def __init__(self):
        self.connection = sqlite3.connect('sqlite.db')
        self.cursor = self.connection.cursor()

    def get_users(self):
        with self.connection:
            return self.cursor.execute('SELECT user_id FROM user').fetchall()

    def insert_user(self, user_id):
        with self.connection:
            return self.cursor.execute('INSERT INTO user (user_id) VALUES (?)', (user_id, ))

    def user_exists(self, user_id):
        with self.connection:
            res = self.cursor.execute('SELECT * FROM  user WHERE user_id = ?',
                                      (user_id, )).fetchall()
            return bool(len(res))



