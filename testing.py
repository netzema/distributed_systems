from requests import get, put, delete, post
import logging

logging.basicConfig(filename='clientlogs.log', filemode='w+', level=logging.INFO)

"""print(get('http://localhost:5000/users/api/admin').json())
r = post('http://localhost:5000/users/api/session/admin', data={'password':'admin'})
print(r.json()["success"])
print(get('http://localhost:5000/users/api/admin').json())"""


print("Please log in...")
while(True):
    name = input("Username: ")
    password = input("Password: ")
    user = get('http://localhost:5000/users/api/'+name).json()
    username = list(user.items())[0][0]
    logging.info(f'User {username} checks if username exists')

    if 'success' in user:
        print(user["error_msg"])
        continue

    r = post('http://localhost:5000/users/api/session/'+name, data={'password': password}).json()
    logging.info(f'User {username} tries to log in')
    if r["success"] == True:
        tk = r["token"]
        print(r["error_msg"])
        break

    print("Username or password incorrect. Try again")

while(True):
    print("\n\nAvailable commands:\nadd_user *name* *role* *password*\ndelete_user *name*\nrun_job\nget_all_jobs\nget_all_results\n")
    cmd = input(">> ").split()
    print(cmd)
    if cmd[0] == "add_user":
        r = post('http://localhost:5000/users/api/'+username, data={'username' : cmd[1], 'role': cmd[2], 'password': cmd[3]}).json()
        logging.info(f'User {username} tries to add user with metadata: username : {cmd[1]}, role: {cmd[2]}, password: {cmd[3]}')
        print(r["msg"])
        continue

    if cmd[0] == "delete_user":
        d = delete('http://localhost:5000/users/api/'+cmd[1]).json()
        logging.info(f'User {username} tries to delete user {cmd[1]}')
        print(d["msg"])
        continue

    if cmd[0] == "add_job":
        assets = input("Give asset integers")
        u = post('http://localhost:8008/jobs/api/job', data={"user":username, "assets": assets, "token": tk}).json()
        logging.info(f'User {username} tries to add a job with parameters "user":{username}, "assets": {assets}')
        if u["success"] == False:
            print(u["error_msg"])
            continue

        print(u["msg"])



"""        
print("login admin")
print(post('http://localhost:5000/users/api/session/admin', data={'password':'admin'}).json())
print("admin data")
print(get('http://localhost:5000/users/api/admin', data = {'username': 'admin'}).json())
print("Admin logs out")
print(put('http://localhost:5000/users/api/session/admin').json())
print("Logged out admin tries to hire Ted")
print(post('http://localhost:5000/users/api/admin', data={'username': 'Ted', 'password':'somesupersafepassword', 'role': 'manager'}).json())
print("Admin logs in again")
print(post('http://localhost:5000/users/api/session/admin', data={'password':'admin'}).json())
print("Hire Ted, the manager")
print(post('http://localhost:5000/users/api/admin', data={'username': 'Ted', 'password':'somesupersafepassword', 'role': 'manager'}).json())
print("Admin gets infos of Ted")
print(get('http://localhost:5000/users/api/admin', data={'username': 'Ted'}).json())
print("Ted logs in")
print(post('http://localhost:5000/users/api/session/Ted', data={'password':'somesupersafepassword'}).json())
print("Ted gets infos of admin")
print(get('http://localhost:5000/users/api/Ted', data={'username': 'admin'}).json())
print("Ted tries to hire Berta, the secretary.")
print(post('http://localhost:5000/users/api/Ted', data={'username': 'Berta', 'password':'1234', 'role': 'secretary'}).json())
print("Admin gets infos of Berta, the secretary")
print(get('http://localhost:5000/users/api/admin', data={"username":"Berta"}).json())
print("Admin hires Berta, the secretary")
print(post('http://localhost:5000/users/api/admin', data={'username': 'Berta', 'password':'1234', 'role': 'secretary'}).json())
print("Admin accesses Berta's data")
print(get('http://localhost:5000/users/api/admin', data={"username":"Berta"}).json())
print("Ted got mad. He wants to fire Berta, the secretary, now.")
print(delete('http://localhost:5000/users/api/Ted', data = {'username': 'Berta'}).json())
print("Admin accesses Berta's data")
print(get('http://localhost:5000/users/api/admin', data={"username":"Berta"}).json())
print("Admin agrees with Ted and fires Berta, the secretary now.")
print(delete('http://localhost:5000/users/api/admin', data = {'username': 'Berta'}).json())
print("Admin accesses Berta's data")
print(get('http://localhost:5000/users/api/admin', data={"username":"Berta"}).json())
print("Ted logs out")
print(put('http://localhost:5000/users/api/session/Ted').json())
print("Ted logs in with wrong password")
print(post('http://localhost:5000/users/api/session/Ted', data={'password':'somewrongpassword'}).json())
print("Admin wants to get data from Ted now.")
print("Admin logs in again")
print(post('http://localhost:5000/users/api/session/admin', data={'password':'admin'}).json())
print("Hire Ted, the manager")
print(post('http://localhost:5000/users/api/admin', data={'username': 'Ted', 'password':'somesupersafepassword', 'role': 'manager'}).json())
print("Ted logs in")
print(post('http://localhost:5000/users/api/session/Ted', data={'password':'somesupersafepassword'}).json())
print(get('http://localhost:5000/users/api/admin', data={"username":"Ted"}).json())
print('Ted wants to change his password.')
print(put('http://localhost:5000/users/api/Ted', data={'new_password': 'superhotnewpassword'}).json())
print("Admin wants to get data from Ted now.")
print(get('http://localhost:5000/users/api/admin', data={"username":"Ted"}).json())
"""