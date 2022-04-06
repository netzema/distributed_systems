from flask import Flask, request
from flask_restful import Resource, Api
import random

app = Flask(__name__)
api = Api(app)

users = {"admin": {"password":"admin", "role":"admin"}}

def create_token():
    return '%030x' % random.randrange(16**30)


class User(Resource):
    def get(self, name):
        return {name: users[name]}

    def put(self, name):
        user_information = {}
        user_information["password"] = request.form["password"]
        user_information["role"] = request.form["role"]
        users[name] = user_information
        return {name: users[name]}

    def post(self, name):
        user_information = {}
        user_information["password"] = request.form["password"]
        user_information["role"] = request.form["role"]
        users[name] = user_information
        return {name: users[name]}

    def delete(self, name):
        if name in users:
            del users[name]
            return {"success": True}
        else:
            return {"success": False, "error_msg": "User not found"}

class Auth(Resource):
    def post(self, name):
        pw = request.form("password")
        if users[name]["password"] != pw:
            return {"success": False, "error_msg": "Wrong username or password."}
        else:
            tk = create_token()
            users[name]["token"] = tk
            return {"success": True, "error_msg": ""}


api.add_resource(User, '/users/api/<string:name>')
api.add_resource(Auth, '/users/api/session/<string:name>')

if __name__ == '__main__':
    app.run(debug=True)