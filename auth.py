from flask import Flask, request
from flask_restful import Resource, Api
import logging
from requests import get
import random

logging.basicConfig(filename='authlogs.log', format='%(asctime)s %(message)s', filemode='a+', level=logging.INFO)
logger = logging.getLogger()

app = Flask(__name__)
api = Api(app)

users = {"admin": {"password": "admin", "role": "admin"}}
rights = {"admin": ["add_user", "del_user", "add_job", "edit_job", "delete_job", "create_queue", "delete_queue",
                    "get_queues", "pull_job"],
          "manager": ["add_job", "edit_job", "delete_job", "pull_job", "get_queues"],
          "secretary": ["get_users", "get_queues"]}


def check_user(name):
    # check if user exists
    if name not in users:
        logger.info(f'User {name} not in database.')
        return False
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
        return not users[name]["token"] == ""


def validate_access(name):
    # returns role if token is valid
    if check_user(name):
        if check_token(name):  # if token not empty
            logger.info(f'Token for user {name} is valid.')
            return users[name]["role"]  # return role


class User(Resource):
    def get(self, name):
        username = request.form["username"]
        if check_user(name):
            return {username: users[username]}
        else:  # the others get only name and role
            return {'success': False, 'msg': f'User {username} not found.'}

    def put(self, name):
        # update password or username
        # store action to take
        new_password = request.form["new_password"]
        if new_password != None:
            users[name]["password"] = new_password
            logger.info(f'User {name} changed password.')
        else:
            logger.info(f'Password for user {name} was not changed.')
            return {'success': False, 'msg': 'No update made. Check the input.'}


    def post(self, name):
        # only for admins
        username = request.form["username"]
        tk = request.form["token"]
        auth = get('http://localhost:5000/users/api/session/auth', data={"token": tk, "service": "add_user"}).json()
        logging.info(f'User {name} called authentication service for service to delete user {username}.')
        if auth["success"] == False:
            return auth  # access denied

        user_information = {}
        username = request.form["username"]
        user_information["password"] = request.form["password"]
        user_information["role"] = request.form["role"]
        users[username] = user_information
        logger.info(f'User {name} added user {username}.')
        return {'success': True, 'msg': f'Welcome on board, {username}!'}


    def delete(self, name):
        # only for admins
        username = request.form["username"]
        tk = request.form["token"]
        auth = get('http://localhost:5000/users/api/session/auth', data={"token": tk, "service": "del_user"}).json()
        logging.info(f'User {name} called authentication service for service to delete user {username}.')
        if auth["success"] == False:
            return auth # access denied

        if username in users:
            del users[username]
            logger.info(f'User {name} deleted user {username}.')
            return {"success": True, 'msg': f"You're fired, {username}!"}
        else:
            logger.info(f'User {username} not found.')
            return {"success": False, "msg": f"User {username} not found"}



class Login(Resource):
    def post(self, name):
        # user logs in
        if check_user(name) == True:
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
        else:
            return {"success": False, "msg": "Username not in database. Contact admin"}

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
    # Check whether token exists or is valid, and whether user role has access to a service.
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