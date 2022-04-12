from flask import Flask, request
from flask_restful import Resource, Api
import logging
import random

logging.basicConfig(filename='authlogs.log', format='%(asctime)s %(message)s', filemode='w', level=logging.INFO)

logger = logging.getLogger()


app = Flask(__name__)
api = Api(app)

users = {"admin": {"password":"admin", "role":"admin"}}
rights = {"admin": ["add_user", "del_user", "add_job", "edit_job", "delete_job"],
          "manager": ["add_job", "edit_job", "delete_job"],
          "secretary": ["get_users"]}

def check_user(name):
    # check if user exists
    if name not in users:
        logger.info(f'User {name} not in database.')
        return {"Name not in database."}
    else:
        logger.info(f'User {name} found.')
        return True

def create_token():
    # create random base-64 token
    logger.info(f'Token created.')
    return '%030x' % random.randrange(16**30)

def check_token(name):
    # check if token is not empty
    if check_user(name):
        logger.info(f'Checking token for user {name}.')
        return not "token" in users[name]

def validate_access(name):
    # returns role if token is valid
    if check_user(name):
        if check_token(name): # if token not empty
            logger.info(f'Token for user {name} is valid.')
            return users[name]["role"] # return role

class User(Resource):
    def get(self, name):
        # get information of a given user

        # check if user exists
        if check_user(name):
            # store name whose information to access
            username = request.form["username"]
            if username in users: # if user to be accessed exists
                access = validate_access(name) # check which role user has
                if access == "admin": # admin gets all info
                    logger.info(f'User {name} accessed data of {username}.')
                    return {username: users[username]}
                else: # the others get only name and role
                    logger.info(f'User {name} does not have the rights to access data of {username}.')
                    return {username: {'username': username, 'role': users[username]['role']}}
            else: # if user does not exist
                logger.info(f'User {username} not found.')
                return {'success': False, 'msg': f'User {username} not found.'}

    def put(self, name):
        # update password
        if check_user(name):
            # check if user is logged in
            # role does not matter, everybody can change their password
            if validate_access(name):
                new_password = request.form["new_password"]
                if new_password != None:
                    users[name]["password"] = new_password
                    logger.info(f'User {name} changed password.')
                else:
                    # if no new password provided
                    logger.info(f'Password for user {name} was not changed.')
                    return {'success': False, 'msg': 'No update made. No new password provided.'}
                return {'success': True, 'msg':'Updated password.'}
            else:
                # if user has no validation fails (due to missing token or user not in data cache)
                logger.info(f'User {name} not logged in.')
                return {'success': False, 'msg': 'Please log in.'}

    def post(self, name):
        # add new users; only for admins
        if check_user(name):
            # check if user is an admin
            if validate_access(name) == 'admin':
                # store information of new user
                user_information = {}
                username = request.form["username"]
                user_information["password"] = request.form["password"]
                user_information["role"] = request.form["role"]
                users[username] = user_information
                logger.info(f'User {name} added user {username}.')
                return {'success': True, 'msg': f'Welcome on board, {username}!'}
            else:
                # if user is no admin
                logger.info(f'User {name} is not allowed to add new users.')
                return {'success': False, 'msg': 'No authentification for that action.'}

    def delete(self, name):
        # delete an existing user; only for admins
        if check_user(name):
            # check if user is admin
            if validate_access(name) == 'admin':
                username = request.form["username"]
                # if user to be deleted exists
                if username in users:
                    # delete user
                    del users[username]
                    logger.info(f'User {name} deleted user {username}.')
                    return {"success": True, 'msg': f"You're fired, {username}!"}
                else:
                    # if the user does not exist
                    logger.info(f'User {username} not found.')
                    return {"success": False, "msg": f"User {username} not found"}
            else:
                # if user is no admin
                logger.info(f'User {name} is not allowed to delete users.')
                return {'success': False, 'msg': 'No authentication for that action.'}

class Login(Resource):
    def post(self, name):
        # user logs in
        if check_user(name):
            # login with password and username
            # get params from request
            for username, password in request.form.items():
                pw = password
            # if passwords match
            if users[name]["password"] == pw:
                tk = create_token() # create a login token
                users[name]["token"] = tk
                logger.info(f'User {name} signed in.')
                return {"success": True, "msg": "", "token": tk}
            else:
                # if passwords don't match
                logger.info(f'User {name} tried to sign in but failed.')
                return {"success": False, "msg": "Wrong username or password."}

    def put(self, name):
        # user logs out
        if check_user(name):
            # check if token exists
            if "token" in users[name]:
                # reset token
                del users[name]["token"]
                logger.info(f'User {name} signed out.')
                return {'success': True, 'msg': f'User {name} logged out.'}
            else:
                # if no token exists -> user was not logged in
                logger.info(f'User {name} could not sign out.')
                return {'success': False, 'msg': f'User {name} not logged in.'}
        else:
            # if user not found
            logger.info(f'User {name} not found.')
            return {'success': False, 'msg': 'User not found.'}



class Auth(Resource):
    def get(self):
        # check if token is valid and user is allowed to call service
        token = request.form["token"]
        service = request.form["service"]

        for k in users.keys(): # go through all users
            if "token" in users[k].keys(): # check if token exists
                if users[k]["token"] == token: # check if tokens match
                    if users[k]["role"] in rights: # check if a user's role exists
                        if service in rights[users[k]["role"]]: # check if the user's role is in the service's requirements
                            logger.info(f'User {k} granted access to {service}.')
                            return {'success': True} # request access granted
                        else:
                            # if the user is not allowed to call the service
                            logger.info(f'User {k} not granted access to {service}.')
                            return {'success': False, 'msg': 'Request denied.'}
                else:
                    # if the tokens do not match
                    continue
            else:
                # if the user has no token yet
                continue

        # if token not found
        logger.info(f'Token not found. Could not perform {service}.')
        return {'success': False, 'msg': 'Token not found.'}

api.add_resource(User, '/users/api/<string:name>')
api.add_resource(Login, '/users/api/session/<string:name>')
api.add_resource(Auth, '/users/api/session/auth')

if __name__ == '__main__':
    app.run(debug=True)