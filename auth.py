from flask import Flask, request
from flask_restful import Resource, Api
import random

app = Flask(__name__)
api = Api(app)

users = {"admin": {"password":"admin", "role":"admin"}}

def create_token():
    return '%030x' % random.randrange(16**30)

def validate_access(name):
    if users[name]["token"]:
        return users[name]["role"]

class User(Resource):
    def get(self, name):
        if name in users:
            return {name: users[name]}
        else:
            return {'success': False, 'error_msg': f'User {name} not found.'}

    def put(self, name):
        user_information = {}
        user_information["password"] = request.form["password"]
        user_information["role"] = request.form["role"]
        users[name] = user_information
        return {name: users[name]}

    def post(self, name):
        # only for admins
        if validate_access(name) == 'admin':
            user_information = {}
            username = request.form["username"]
            user_information["password"] = request.form["password"]
            user_information["role"] = request.form["role"]
            users[username] = user_information
            return {username: users[username]}
        else:
            return {'success': False, 'error_msg': 'No authentification for that action.'}

    def delete(self, name):
        if validate_access(name) == 'admin':
            username = request.form["username"]
            if username in users:
                del users[username]
                return {"success": True, 'msg': f'User {username} deleted.'}
            else:
                return {"success": False, "error_msg": f"User {username} not found"}
        else: return {'success': False, 'error_msg': 'No authentification for that action.'}

class Auth(Resource):
    def post(self, name):
        for username, password in request.form.items():
            pw = password
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