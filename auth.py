from flask import Flask, request
from flask_restful import Resource, Api
import random

app = Flask(__name__)
api = Api(app)

users = {"admin": {"password":"admin", "role":"admin"}}

def create_token():
    return '%030x' % random.randrange(16**30)

def check_token(name):
    # check if token is not empty
    return not users[name]["token"] == ""

def validate_access(name):
    if check_token(name): # if token not empty
        return users[name]["role"] # return role

class User(Resource):
    def get(self, name):
        # store name
        username = request.form["username"]
        if username in users: # if user to be accessed exists
            access = validate_access(name) # check which role user has
            if access == "admin": # admin gets all info
                return {username: users[username]}
            else: # the others get only name and role
                return {username: {'username': username, 'role': users[username]['role']}}
        else: # if user does not exist
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
            # store information of new user
            user_information = {}
            username = request.form["username"]
            user_information["password"] = request.form["password"]
            user_information["role"] = request.form["role"]
            users[username] = user_information
            return {'success': True, 'msg': f'Welcome on board, {username}!'}
        else:
            return {'success': False, 'error_msg': 'No authentification for that action.'}

    def delete(self, name):
        # only for admins
        if validate_access(name) == 'admin':
            username = request.form["username"]
            if username in users:
                # delete user
                del users[username]
                return {"success": True, 'msg': f"You're fired, {username}!"}
            else:
                return {"success": False, "error_msg": f"User {username} not found"}
        else:
            return {'success': False, 'error_msg': 'No authentication for that action.'}

class Auth(Resource):
    def post(self, name):
        # login with password and username
        for username, password in request.form.items():
            pw = password
        if users[name]["password"] == pw:
            tk = create_token()
            users[name]["token"] = tk
            return {"success": True, "error_msg": ""}
        else:
            return {"success": False, "error_msg": "Wrong username or password."}


    def put(self, name):
        # log out
        if name in users:
            if users[name]['token'] != "":
                # reset token
                users[name]["token"] = ""
                return {'success': True, 'msg': f'User {name} logged out.'}
            else:
                return {'success': False, 'error_msg': f'User {name} not logged in.'}
        else:
            return {'success': False, 'error_msg': 'User not found.'}

api.add_resource(User, '/users/api/<string:name>')
api.add_resource(Auth, '/users/api/session/<string:name>')

if __name__ == '__main__':
    app.run(debug=True)