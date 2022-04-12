from flask import Flask, request
from flask_restful import Resource, Api
import random
import logging

logging.basicConfig(filename='authlogs.log', filemode='w+', level=logging.INFO)

app = Flask(__name__)
api = Api(app)

users = {"admin": {"password":"admin", "role":"admin"}}
rights = {"admin": ["add_user", "del_user", "add_job", "edit_job"],
          "manager": ["add_job", "edit_job"],
          "secretary": ["get_users"]}

def check_user(name):
    if name not in users:
        return {"Name not in database."}
    else:
        return True

def create_token():
    # random base-64 token
    return '%030x' % random.randrange(16**30)

def check_token(name):
    # check if token is not empty
    if check_user(name):
        return not users[name]["token"] == ""

def validate_access(name):
    # returns role if token is valid
    if check_user(name):
        if check_token(name): # if token not empty
            return users[name]["role"] # return role

class User(Resource):
    def get(self, name):
        if check_user(name):
            # store name
            username = request.form["username"]
            if username in users: # if user to be accessed exists
                access = validate_access(name) # check which role user has
                if access == "admin": # admin gets all info
                    return {username: users[username]}
                else: # the others get only name and role
                    return {username: {'username': username, 'role': users[username]['role']}}
            else: # if user does not exist
                return {'success': False, 'error_msg': f'User {username} not found.'}

    def put(self, name):
        # update password or username
        # store action to take
        if check_user(name):
            if validate_access(name):
                new_password = request.form["new_password"]
                print(new_password)
                if new_password != None:
                    users[name]["password"] = new_password
                else:
                    return {'success': False, 'error_msg': 'No update made. Check the input.'}
                return {'success': True, 'msg':'Updated password.'}
            else:
                return {'success': False, 'msg': 'Please log in.'}

    def post(self, name):
        # only for admins
        if check_user(name):
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
        if check_user(name):
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

class Login(Resource):
    def post(self, name):
        if check_user(name):
            # login with password and username
            for username, password in request.form.items():
                pw = password

            if users[name]["password"] == pw:
                tk = create_token()
                users[name]["token"] = tk
                logging.info(f'User {name} signed in')
                return {"success": True, "error_msg": "", "token": tk}
            else:
                logging.info(f'User {name} tried to sign in but failed.')
                return {"success": False, "error_msg": "Wrong username or password."}

    def put(self, name):
        if check_user(name):
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



class Auth(Resource):
    def get(self):
        token = request.form["token"]
        service = request.form["service"]

        for k in users.keys():
            if "token" in users[k].keys():
                if users[k]["token"] == token: # check if token exists
                    if users[k]["role"] in rights:
                        if service in rights[users[k]["role"]]:
                            return {'success': True} # request access granted
                else:
                    continue
            else:
                continue

        # if token not found
        return {'success': False, 'error_msg': 'Request denied.'}



api.add_resource(User, '/users/api/<string:name>')
api.add_resource(Login, '/users/api/session/<string:name>')
api.add_resource(Auth, '/users/api/session/auth')

if __name__ == '__main__':
    app.run(debug=True)