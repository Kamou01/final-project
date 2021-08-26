import hmac
import sqlite3

from flask import Flask, request
from flask_jwt import JWT, jwt_required, current_identity


class user_info(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def fetch_users():
    with sqlite3.connect('comicbook_store.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(user_info(data[0], data[3], data[4]))
    return new_data


def init_usertable():
    conn = sqlite3.connect('comicbook_store.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")

    conn.commit()
    print("user table created successfully.")


init_usertable()
users = fetch_users()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return username_table.get(user_id, None)


def comicbook_table():
    with sqlite3.connect('comicbook_store.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS comicbooks (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "name TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "description TEXT NOT NULL,"
                     "category TEXT NOT NULL)")
        print("comicbooks table create successfully.")


init_usertable()
comicbook_table()

users = fetch_users()


app = Flask(__name__)
app.debug = True
app.config["SECRET_KEY"] = 'super-secret'

jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required
def protected():
    return '%s' % current_identity


@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']

        print(first_name, username, password, last_name)

        with sqlite3.connect('comicbook_store.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user("
                           "first_name,"
                           "last_name,"
                           "username,"
                           "password) VALUES(?, ?, ?, ?)", (first_name, last_name, username, password))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201

    return response


@app.route('/adding_comic/', methods=["POST"])
def add_comicbooks():
    response = {}

    if request.method == "POST":
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        category = request.form['category']

        with sqlite3.connect('comicbook_store.db') as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO comicbooks("
                               "name,"
                               "price,"
                               "description,"
                               "category) VALUES(?, ?, ?, ?)", (name, price, description, category))
                conn.commit()
                response["status_code"] = 201
                response['description'] = "Comicbook added successfully"
        return response


@app.route('/delete_comic/<int:id>/')
def delete_products(product_id):
    response = {}

    with sqlite3.connect('comicbook_store.db') as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM comicbooks WHERE id=" + str(product_id))
        connection.commit()
        response['status code'] = 200
        response['message'] = "Comic deleted."
    return response


@app.route('/view_comics/')
def view_products():
    response = {}

    with sqlite3.connect('comicbook_store.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM comicbooks')
        conn.commit()

        products = cursor.fetchall()
        response["status_code"] = 201
        response["products"] = products
        response['description'] = "Here are the comics"

    return response


@app.route('/updating_comic/<int:id>/', methods=["PUT"])
def update_comics(id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('comicbook_store.db') as conn:
            print(request.json)
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("name") is not None:
                put_data["name"] = incoming_data.get("name")

                with sqlite3.connect('comicbook_store.db') as connection:
                    cursor = connection.cursor()
                    cursor.execute("UPDATE comicbooks SET name =? WHERE id", (put_data["name"], id))

                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200

            elif incoming_data.get("price") is not None:
                put_data["price"] = incoming_data.get("price")

                with sqlite3.connect('comicbook_store.db') as connection:
                    cursor = connection.cursor()
                    cursor.execute("UPDATE comicbooks SET price =? WHERE id =?", (put_data["price"], id))

                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200

            elif incoming_data.get("description") is not None:
                put_data["description"] = incoming_data.get("description")

                with sqlite3.connect('comicbook_store.db') as connection:
                    cursor = connection.cursor()
                    cursor.execute("UPDATE comicbooks SET description =? WHERE id", (put_data["description"], id))

                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200

            elif incoming_data.get("category") is not None:
                put_data["category"] = incoming_data.get("category")

                with sqlite3.connect('comicbook_store.db') as connection:
                    cursor = connection.cursor()
                    cursor.execute("UPDATE comicbooks SET type =? WHERE id", (put_data["type"], id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200

    return response


@app.route('/view_comic/<int:id>')
def view_comic(id):
    response = {}

    with sqlite3.connect('comicbook_store.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM comicbooks WHERE id =? ', str(id))
        product = cursor.fetchone()
        conn.commit()

        response['status code'] = 201
        response['description'] = "Here are the comics"
        response['data'] = product

    return response


if __name__ == '__main__':
    app.run()